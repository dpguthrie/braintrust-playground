# Pipecat AI Study Partner

An intelligent voice-based study assistant that can discuss and explain articles from Wikipedia or arXiv papers. This example demonstrates real-time voice conversations with AI using Pipecat's pipeline framework, integrated with Braintrust for observability and tracing.

## Table of Contents

- [What is Pipecat AI Study Partner?](#what-is-pipecat-ai-study-partner)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [API Keys Setup](#api-keys-setup)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

## What is Pipecat AI Study Partner?

The Pipecat AI Study Partner is a real-time voice assistant that helps you understand and learn from academic articles and research papers. Simply provide a URL to a Wikipedia article or arXiv paper, and the AI will engage in a natural voice conversation to help you understand the content.

The application demonstrates:
- **Real-time voice interaction** using Daily.co for WebRTC transport
- **Speech-to-Text (STT)** processing with automatic transcription
- **Large Language Model (LLM)** processing with OpenAI GPT-4o-mini
- **Text-to-Speech (TTS)** with Cartesia for natural voice synthesis
- **Content extraction** from web articles and PDF papers
- **Observability and tracing** with Braintrust integration
- **Voice Activity Detection (VAD)** for natural conversation flow

## Features

- 🎤 **Real-time Voice Conversations**: Natural back-and-forth discussions about articles
- 📚 **Multi-source Content**: Supports Wikipedia articles and arXiv research papers
- 🧠 **Intelligent Summarization**: AI breaks down complex content into digestible explanations
- 🔊 **High-quality Speech Synthesis**: Natural-sounding voice responses using Cartesia
- 📊 **Full Observability**: Complete tracing and metrics with Braintrust integration
- ⚡ **Low Latency**: Optimized pipeline for responsive conversations
- 🎯 **Focused Responses**: Concise 2-sentence explanations to keep conversations engaging
- 🔄 **Interruption Handling**: Natural conversation flow with interruption support

## Requirements

### System Requirements
- **Python**: 3.12 or higher
- **Operating System**: macOS, Linux, or Windows
- **Internet Connection**: Required for real-time voice communication
- **Microphone and Speakers**: For voice interaction

### Dependencies
- **[Pipecat AI](https://pipecat.ai/)**: Real-time voice AI framework
- **[Daily.co](https://daily.co/)**: WebRTC platform for real-time communication
- **[OpenAI](https://openai.com/)**: Large language model for conversation
- **[Cartesia](https://cartesia.ai/)**: High-quality text-to-speech synthesis
- **[Braintrust](https://braintrust.dev/)**: Observability and tracing platform

### API Keys Required
- **Daily API Key**: Sign up at [daily.co](https://daily.co/) for real-time communication
- **OpenAI API Key**: Get your key from [platform.openai.com](https://platform.openai.com/)
- **Cartesia API Key**: Register at [cartesia.ai](https://cartesia.ai/) for TTS
- **Braintrust API Key**: Sign up at [braintrust.dev](https://braintrust.dev/) for observability

## Installation

### 1. Navigate to the Example Directory
```bash
cd pipecat_example
```

### 2. Create Virtual Environment (Recommended)
```bash
uv venv
```

### 3. Install Dependencies
```bash
uv pip install -r requirements.txt
```

## Configuration

### 1. Set Up Environment Variables
Copy the .env.example to a .env file and fill in

```bash
cp .env.example .env
```


### 2. Daily Room Setup
You have two options for setting up your Daily room:

**Option A: Use existing room**
- Set `DAILY_SAMPLE_ROOM_URL` to your existing Daily room URL

**Option B: Create room dynamically**
- The application can create temporary rooms using your Daily API key

## Usage

### Quick Start

1. **Start the application**:
```bash
python src/app.py
```

2. **Enter article URL** when prompted:
```bash
Enter the URL of the article you would like to talk about: https://en.wikipedia.org/wiki/Artificial_intelligence
```

3. **Join the voice conversation**:
   - The application will provide a Daily room URL
   - Open the URL in your browser or Daily app
   - Start speaking to discuss the article with your AI study partner

### Supported URL Types

**Wikipedia Articles**:
```bash
https://en.wikipedia.org/wiki/Machine_learning
https://en.wikipedia.org/wiki/Neural_network
```

**arXiv Papers**:
```bash
https://arxiv.org/abs/2301.07041
https://arxiv.org/pdf/2301.07041.pdf
```

### Example Conversation Flow

1. **AI**: "Hello! I'm ready to discuss the article with you. What would you like to learn about?"
2. **You**: "Can you explain the main concepts in this paper?"
3. **AI**: "This paper introduces a new approach to neural networks that improves efficiency by 40%. The key innovation is using attention mechanisms in a novel way."
4. **You**: "How does that compare to traditional methods?"
5. **AI**: "Traditional methods require more computational resources and achieve lower accuracy. This approach is both faster and more precise."

## How It Works

### Pipeline Architecture

```
Audio Input → STT → LLM Context → OpenAI LLM → TTS → Audio Output
     ↑                                                      ↓
     └────────────── Real-time Voice Pipeline ──────────────┘
```

### Processing Flow

1. **Content Extraction**: 
   - Downloads and parses Wikipedia articles or arXiv PDFs
   - Truncates content to fit model context limits (10,000 tokens)

2. **Voice Pipeline**:
   - **Input**: Captures user voice through Daily.co WebRTC
   - **STT**: Converts speech to text with automatic transcription
   - **LLM**: Processes text with OpenAI GPT-4o-mini for intelligent responses
   - **TTS**: Converts AI responses to speech using Cartesia
   - **Output**: Streams audio back to user in real-time

3. **Observability**:
   - All interactions are traced and monitored through Braintrust
   - Performance metrics and conversation analytics are collected
   - Full pipeline visibility for debugging and optimization

## API Keys Setup

### Braintrust API Key
1. Sign up at [braintrust.dev](https://braintrust.dev/)
2. Go to Settings → API Keys
3. Create new API key
4. Add to `.env` as `BRAINTRUST_API_KEY`

### Daily.co API Key
1. Sign up at [daily.co](https://daily.co/)
2. Go to [Dashboard → Developers](https://dashboard.daily.co/developers)
3. Create a new API key
4. Add to `.env` as `DAILY_API_KEY`

### OpenAI API Key
1. Create account at [platform.openai.com](https://platform.openai.com/)
2. Navigate to [API Keys](https://platform.openai.com/api-keys)
3. Create new secret key
4. Add to `.env` as `OPENAI_API_KEY`

### Cartesia API Key
1. Register at [cartesia.ai](https://cartesia.ai/)
2. Access your API dashboard
3. Generate new API key
4. Add to `.env` as `CARTESIA_API_KEY`

## Troubleshooting

### Common Issues

**1. Audio Issues**
```bash
# Check microphone permissions
# Ensure Daily room URL is accessible
# Verify browser supports WebRTC
```

**2. API Key Errors**
```bash
# Verify all required API keys are set in .env
# Check API key permissions and quotas
# Ensure .env file is in the correct directory
```

**3. Content Extraction Failures**
```bash
# Verify URL is accessible
# Check internet connection
# Try alternative article URLs
```

**4. Pipeline Errors**
```bash
# Check logs for specific error messages
# Verify all dependencies are installed
# Ensure Python version compatibility
```

### Debug Mode
Enable console export for detailed tracing:
```bash
export OTEL_CONSOLE_EXPORT=true
python src/app.py
```

### Manual Testing
Use the manual script for debugging:
```bash
python src/manual.py
```

## Architecture

### Core Components

- **`app.py`**: Main application with full voice pipeline
- **`manual.py`**: Setup manual tracing
- **`runner.py`**: Daily.co configuration and room management
- **`requirements.txt`**: All Python dependencies

### Dependencies Overview

```python
# Core Framework
pipecat-ai[daily,cartesia,openai,silero]  # Voice AI pipeline

# LLM & AI Services
openai                    # Language model
cartesia                  # Text-to-speech

# Content Processing
beautifulsoup4            # HTML parsing
pypdf                     # PDF text extraction
tiktoken                  # Token counting

# Observability
braintrust[cli]           # Experiment tracking
opentelemetry-exporter-otlp-proto-http  # Tracing

# Utilities
python-dotenv            # Environment management
```

## Contributing

We welcome contributions to improve the Pipecat AI Study Partner!

### Ways to Contribute
- 🐛 **Bug Reports**: Report issues with voice quality, content extraction, or pipeline errors
- 💡 **Feature Requests**: Suggest new content sources, voice improvements, or UI enhancements
- 📝 **Documentation**: Improve setup guides, troubleshooting, or usage examples
- 🧪 **Testing**: Test with different article types, languages, or edge cases
- 🔧 **Code Improvements**: Optimize performance, add error handling, or enhance features

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/voice-improvements`
3. Make your changes and test thoroughly
4. Update documentation if needed
5. Submit a pull request with detailed description

### Testing Guidelines
- Test with various Wikipedia articles and arXiv papers
- Verify voice quality and conversation flow
- Check error handling for invalid URLs
- Ensure all API integrations work correctly

## Support

### Getting Help
- 📚 **Pipecat Documentation**: [docs.pipecat.ai](https://docs.pipecat.ai/)
- 💬 **Issues**: Open a [GitHub Issue](https://github.com/your-username/braintrust-playground/issues)
- 🌟 **Examples**: Check other examples in this repository
- 📧 **Community**: Join the Pipecat Discord community

### Useful Resources
- [Daily.co WebRTC Guide](https://docs.daily.co/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Cartesia Voice Samples](https://cartesia.ai/voices)
- [Braintrust Observability Guide](https://www.braintrust.dev/docs)

## License

This project is part of the Braintrust Playground and is licensed under the MIT License.

---

**Ready to start learning?** 🎓🤖

Experience the future of AI-powered education with voice-based learning that makes complex topics engaging and accessible!
