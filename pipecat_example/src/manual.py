import asyncio
import io
import json
import os
import sys
from typing import Any, Dict

import aiohttp
import tiktoken
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.utils.tracing.setup import setup_tracing
from pypdf import PdfReader
from runner import configure

load_dotenv()

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

# Set up manual OpenTelemetry tracer with updated semantic conventions
resource = Resource.create(
    {
        "service.name": "pipecat-study-assistant",
        "service.version": "1.0.0",
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    }
)

# Configure tracer provider
trace.set_tracer_provider(TracerProvider(resource=resource))

# Configure Braintrust exporter
braintrust_exporter = OTLPSpanExporter(
    endpoint="https://api.braintrust.dev/otel/v1/traces",
    headers={
        "Authorization": f"Bearer {os.getenv('BRAINTRUST_API_KEY')}",
        "x-bt-parent": f"project_name:{os.getenv('BRAINTRUST_PROJECT_NAME')}",
    },
)

# Add span processor
span_processor = BatchSpanProcessor(braintrust_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Get manual tracer
manual_tracer = trace.get_tracer("study-assistant-manual", "1.0.0")

# Also set up Pipecat's built-in tracing
setup_tracing(
    service_name="pipecat-demo",
    exporter=braintrust_exporter,
    console_export=bool(os.getenv("OTEL_CONSOLE_EXPORT")),
)


def truncate_content(content, model_name):
    """Count tokens and truncate content with manual tracing"""
    with manual_tracer.start_as_current_span("content_processing") as span:
        span.set_attribute("operation.type", "tokenization")
        span.set_attribute("model.name", model_name)

        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(content)

        max_tokens = 10000
        original_length = len(tokens)
        span.set_attribute("tokens.original_count", original_length)
        span.set_attribute("tokens.max_allowed", max_tokens)

        if len(tokens) > max_tokens:
            truncated_tokens = tokens[:max_tokens]
            result = encoding.decode(truncated_tokens)
            span.set_attribute("content.truncated", True)
            span.set_attribute("tokens.final_count", max_tokens)
        else:
            result = content
            span.set_attribute("content.truncated", False)
            span.set_attribute("tokens.final_count", original_length)

        span.set_attribute("content.character_count", len(result))
        return result


async def get_article_content(url: str, aiohttp_session: aiohttp.ClientSession):
    """Extract content with manual tracing"""
    with manual_tracer.start_as_current_span("article_extraction") as span:
        span.set_attribute("url.full", url)
        span.set_attribute("extraction.type", "arxiv" if "arxiv.org" in url else "web")

        try:
            if "arxiv.org" in url:
                result = await get_arxiv_content(url, aiohttp_session)
            else:
                result = await get_wikipedia_content(url, aiohttp_session)

            span.set_attribute("extraction.success", True)
            span.set_attribute("content.length", len(result))
            return result
        except Exception as e:
            span.set_attribute("extraction.success", False)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise


async def get_wikipedia_content(url: str, aiohttp_session: aiohttp.ClientSession):
    """Wikipedia extraction with detailed tracing"""
    with manual_tracer.start_as_current_span("wikipedia_extraction") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.url", url)

        async with aiohttp_session.get(url) as response:
            span.set_attribute("http.status_code", response.status)

            if response.status != 200:
                span.set_attribute("extraction.error", "HTTP request failed")
                return "Failed to download Wikipedia article."

            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            content = soup.find("div", {"class": "mw-parser-output"})

            if content:
                extracted_text = content.get_text()
                span.set_attribute(
                    "extraction.paragraphs_found", len(soup.find_all("p"))
                )
                span.set_attribute("content.extracted_length", len(extracted_text))
                return extracted_text
            else:
                span.set_attribute("extraction.error", "Content div not found")
                return "Failed to extract Wikipedia article content."


async def get_arxiv_content(url: str, aiohttp_session: aiohttp.ClientSession):
    """ArXiv PDF extraction with detailed tracing"""
    with manual_tracer.start_as_current_span("arxiv_extraction") as span:
        # Convert abstract URL to PDF URL
        if "/abs/" in url:
            url = url.replace("/abs/", "/pdf/")
        if not url.endswith(".pdf"):
            url += ".pdf"

        span.set_attribute("pdf.url", url)
        span.set_attribute("http.method", "GET")

        async with aiohttp_session.get(url) as response:
            span.set_attribute("http.status_code", response.status)

            if response.status != 200:
                span.set_attribute("extraction.error", "PDF download failed")
                return "Failed to download arXiv PDF."

            content = await response.read()
            span.set_attribute("pdf.size_bytes", len(content))

            pdf_file = io.BytesIO(content)
            pdf_reader = PdfReader(pdf_file)

            page_count = len(pdf_reader.pages)
            span.set_attribute("pdf.page_count", page_count)

            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text

            span.set_attribute("content.extracted_length", len(text))
            return text


def create_llm_span_attributes(
    messages: list, model: str, response: str = None
) -> Dict[str, Any]:
    """Create OpenTelemetry GenAI semantic convention attributes"""
    attributes = {
        # Updated GenAI semantic conventions (v1.28.0+)
        "gen_ai.system": "openai",
        "gen_ai.request.model": model,
        "gen_ai.operation.name": "chat",
    }

    # Handle messages array - use JSON format for complex structures
    if messages:
        attributes["gen_ai.input"] = json.dumps(messages)

    if response:
        attributes["gen_ai.output"] = response

    return attributes


async def main():
    conversation_id = f"study-session-{int(asyncio.get_event_loop().time())}"

    with manual_tracer.start_as_current_span("study_session") as session_span:
        session_span.set_attribute("conversation.id", conversation_id)
        session_span.set_attribute("session.type", "interactive_study")

        url = input("Enter the URL of the article you would like to talk about: ")
        session_span.set_attribute("article.url", url)

        async with aiohttp.ClientSession() as session:
            # Extract and process article content
            article_content = await get_article_content(url, session)
            article_content = truncate_content(
                article_content, model_name="gpt-4o-mini"
            )

            (room_url, token) = await configure(session)
            session_span.set_attribute("daily.room_configured", True)

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
            )

            llm = OpenAILLMService(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-4o-mini",
            )

            # Create system message with manual tracing
            with manual_tracer.start_as_current_span(
                "system_prompt_creation"
            ) as prompt_span:
                system_content = f"""You are an AI study partner. You have been given the following article content:

{article_content}

Your task is to help the user understand and learn from this article in 2 sentences. THESE RESPONSES SHOULD BE ONLY MAX 2 SENTENCES. THIS INSTRUCTION IS VERY IMPORTANT. RESPONSES SHOULDN'T BE LONG.
"""

                messages = [{"role": "system", "content": system_content}]

                # Log system prompt details
                prompt_span.set_attribute("prompt.type", "system")
                prompt_span.set_attribute("prompt.character_count", len(system_content))
                prompt_span.set_attribute(
                    "article.character_count", len(article_content)
                )

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
                conversation_id=conversation_id,
            )

            @transport.event_handler("on_first_participant_joined")
            async def on_first_participant_joined(transport, participant):
                with manual_tracer.start_as_current_span("participant_joined") as span:
                    span.set_attribute("participant.id", participant["id"])
                    span.set_attribute("event.type", "first_participant_joined")

                    await transport.capture_participant_transcription(participant["id"])

                    greeting_message = {
                        "role": "assistant",
                        "content": "Hello! I'm ready to discuss the article with you. What would you like to learn about?",
                    }
                    messages.append(greeting_message)

                    # Log greeting with updated semantic conventions
                    span.set_attributes(
                        create_llm_span_attributes(
                            messages=messages[-1:],
                            model="gpt-4o-mini",
                            response=greeting_message["content"],
                        )
                    )

                    await task.queue_frames(
                        [context_aggregator.user().get_context_frame()]
                    )

            @transport.event_handler("on_participant_left")
            async def on_participant_left(transport, participant, reason):
                with manual_tracer.start_as_current_span("participant_left") as span:
                    span.set_attribute("participant.id", participant["id"])
                    span.set_attribute("event.type", "participant_left")
                    span.set_attribute("leave.reason", reason)

                    await task.cancel()

            runner = PipelineRunner()

            # Final span before running
            session_span.set_attribute("pipeline.configured", True)
            session_span.set_attribute("services.llm", "openai-gpt-4o-mini")
            session_span.set_attribute("services.tts", "cartesia")
            session_span.set_attribute("services.transport", "daily")

            await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
