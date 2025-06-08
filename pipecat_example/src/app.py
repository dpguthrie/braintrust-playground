import asyncio
import io
import os
from typing import Optional

import aiohttp
import tiktoken
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.context.context import Context
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import ReadableSpan, Span, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanProcessor
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pypdf import PdfReader
from runner import configure

load_dotenv()


class PipecatAttributeTransformer(SpanProcessor):
    def on_start(self, span: Span, parent_context: Optional[Context]) -> None:
        pass

    def on_end(self, span: ReadableSpan) -> None:
        if span._attributes is not None:
            input_value = span._attributes.pop("input", None)
            if input_value is not None:
                span._attributes["braintrust.input"] = input_value
            output_value = span._attributes.pop("output", None)
            if output_value is not None:
                span._attributes["braintrust.output"] = output_value

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: Optional[int] = None) -> None:
        pass


# Configure OpenTelemetry exporter for Braintrust
exporter = OTLPSpanExporter()
provider = TracerProvider()
provider.add_span_processor(PipecatAttributeTransformer())
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)


# Count number of tokens used in model and truncate the content
def truncate_content(content, model_name):
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(content)

    max_tokens = 10000
    if len(tokens) > max_tokens:
        truncated_tokens = tokens[:max_tokens]
        return encoding.decode(truncated_tokens)
    return content


# Main function to extract content from url
async def get_article_content(url: str, aiohttp_session: aiohttp.ClientSession):
    if "arxiv.org" in url:
        return await get_arxiv_content(url, aiohttp_session)
    else:
        return await get_wikipedia_content(url, aiohttp_session)


# Helper function to extract content from Wikipedia url (this is
# technically agnostic to URL type but will work best with Wikipedia
# articles)
async def get_wikipedia_content(url: str, aiohttp_session: aiohttp.ClientSession):
    async with aiohttp_session.get(url) as response:
        if response.status != 200:
            return "Failed to download Wikipedia article."

        text = await response.text()
        soup = BeautifulSoup(text, "html.parser")

        content = soup.find("div", {"class": "mw-parser-output"})

        if content:
            return content.get_text()
        else:
            return "Failed to extract Wikipedia article content."


# Helper function to extract content from arXiv url


async def get_arxiv_content(url: str, aiohttp_session: aiohttp.ClientSession):
    if "/abs/" in url:
        url = url.replace("/abs/", "/pdf/")
    if not url.endswith(".pdf"):
        url += ".pdf"

    async with aiohttp_session.get(url) as response:
        if response.status != 200:
            return "Failed to download arXiv PDF."

        content = await response.read()
        pdf_file = io.BytesIO(content)
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text


# This is the main function that handles STT -> LLM -> TTS


async def main():
    url = input("Enter the URL of the article you would like to talk about: ")

    async with aiohttp.ClientSession() as session:
        article_content = await get_article_content(url, session)
        article_content = truncate_content(article_content, model_name="gpt-4o-mini")

        (room_url, token) = await configure(session)

        transport = DailyTransport(
            room_url,
            token,
            "studypal",
            DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                transcription_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            ),
        )

        tts = CartesiaTTSService(
            api_key=os.getenv("CARTESIA_API_KEY"),
            voice_id=os.getenv(
                "CARTESIA_VOICE_ID", "4d2fd738-3b3d-4368-957a-bb4805275bd9"
            ),
            # British Narration Lady: 4d2fd738-3b3d-4368-957a-bb4805275bd9
        )

        llm = OpenAILLMService(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
        )

        messages = [
            {
                "role": "system",
                "content": f"""You are an AI study partner. You have been given the following article content:

{article_content}

Your task is to help the user understand and learn from this article in 2 sentences. THESE RESPONSES SHOULD BE ONLY MAX 2 SENTENCES. THIS INSTRUCTION IS VERY IMPORTANT. RESPONSES SHOULDN'T BE LONG.
""",
            },
        ]

        context = OpenAILLMContext(messages)
        context_aggregator = llm.create_context_aggregator(context)

        pipeline = Pipeline(
            [
                transport.input(),
                context_aggregator.user(),
                llm,
                tts,
                transport.output(),
                context_aggregator.assistant(),
            ]
        )

        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                audio_out_sample_rate=44100,
                allow_interruptions=True,
                enable_metrics=True,
                enable_usage_metrics=True,
            ),
            enable_tracing=True,
            conversation_id="study-session-" + str(asyncio.get_event_loop().time()),
        )

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            await transport.capture_participant_transcription(participant["id"])
            messages.append(
                {
                    "role": "system",
                    "content": "Hello! I'm ready to discuss the article with you. What would you like to learn about?",
                }
            )
            await task.queue_frames([context_aggregator.user().get_context_frame()])

        @transport.event_handler("on_participant_left")
        async def on_participant_left(transport, participant, reason):
            await task.cancel()

        runner = PipelineRunner()

        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
