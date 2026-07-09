# RAG-Based AI Course Assistant

An AI-powered Retrieval-Augmented Generation (RAG) system built to act as a smart assistant for a web development video course. It processes video tutorials, creates transcripts with Whisper, embeds them via Ollama, and serves an interactive web interface using a Flask backend.

## Architecture & Workflow

The system is split into two primary pipelines:

### 1. Data Ingestion & Preprocessing Pipeline
- **`video_to_mp3.py`**: Extracts audio (MP3) from raw video files (`.mp4`/`.mkv`) using `ffmpeg`.
- **`mp3_to_json.py`**: Transcribes the audio to text chunks with timestamps using the OpenAI `whisper` model.
- **`merge_chunks.py`**: Merges smaller transcript chunks into contextually richer blocks.
- **`preprocess_json.py`**: Converts the text chunks into vector embeddings using Ollama (`mxbai-embed-large`) and stores them in a serialized pandas DataFrame (`embeddings.joblib`).

### 2. RAG & Inference Pipeline
- **`app.py`**: A Flask server hosting the web interface. 
- **`process_incoming.py`**: Handles incoming queries, calculates cosine similarity against the `embeddings.joblib` vector store, fetches the top most relevant context chunks, and prompts the LLM.
- **`src/core/pipeline.py` & Agentic Setup**: Coordinates the query execution using semantic caching, routing, memory management, and streams responses using `llama3.2` model.

## Technology Stack

- **Backend Framework**: Flask
- **LLM Engine**: Ollama (Local inference)
- **Models Used**: 
  - `whisper` (small): For Audio-to-Text translation & transcription.
  - `mxbai-embed-large`: For generating embeddings.
  - `llama3.2`: For generating conversational responses based on the retrieved context.
- **Data & similarity**: `pandas`, `numpy`, `scikit-learn` (Cosine Similarity)
- **Utilities**: `ffmpeg`, `joblib`

## Getting Started

### Prerequisites

1. Install [Ollama](https://ollama.ai/) and pull the necessary models:
   ```bash
   ollama run llama3.2
   ollama pull mxbai-embed-large
   ```
2. Install [FFmpeg](https://ffmpeg.org/download.html) and ensure it is accessible in your system's PATH.
3. Install Python dependencies:
   ```bash
   pip install flask python-dotenv pandas numpy scikit-learn joblib requests openai-whisper
   ```

### Running the Data Pipeline (One-Time Setup)

1. **Place raw video tutorials** in the `videos/` folder.
2. **Convert to Audio**: `python video_to_mp3.py`
3. **Transcribe**: `python mp3_to_json.py`
4. **Merge Context**: `python merge_chunks.py`
5. **Generate Embeddings**: `python preprocess_json.py`

### Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to `http://localhost:5000` to interact with the course assistant.

## Features
- **Video Subtitle RAG**: Seamlessly answers queries by pointing users to specific concepts taught in the video tutorials, complete with timestamps.
- **Streaming Responses**: Real-time answer streaming via server-sent events for lower perceived latency.
- **Agentic Pipeline**: Foundational support for multi-hop reasoning, semantic caching, and memory context for follow-up questions.
