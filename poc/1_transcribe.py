#!/usr/bin/env python3
"""
POC Script 1: Audio Transcription
Uses OpenAI Whisper API to transcribe inspector's narration
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def transcribe_audio(audio_file_path: str, output_dir: str = "outputs/transcriptions") -> Dict:
    """
    Transcribe audio file using OpenAI Whisper API

    Args:
        audio_file_path: Path to audio file (mp3, wav, m4a, etc.)
        output_dir: Directory to save transcription results

    Returns:
        Dict containing transcription data with timestamps
    """

    print(f"📝 Transcribing: {audio_file_path}")

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Open audio file
    with open(audio_file_path, "rb") as audio_file:
        # Call Whisper API with timestamp granularity
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",  # Get detailed response with timestamps
            timestamp_granularities=["word", "segment"]  # Word-level and segment-level timestamps
        )

    # Process the transcription
    result = {
        "file": audio_file_path,
        "duration": transcript.duration if hasattr(transcript, 'duration') else None,
        "language": transcript.language if hasattr(transcript, 'language') else "en",
        "full_text": transcript.text,
        "segments": [],
        "words": []
    }

    # Extract segments (sentences/utterances)
    if hasattr(transcript, 'segments') and transcript.segments:
        result["segments"] = [
            {
                "id": seg.id if hasattr(seg, 'id') else i,
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip(),
                "confidence": getattr(seg, 'avg_logprob', 0.0)
            }
            for i, seg in enumerate(transcript.segments)
        ]

    # Extract words (for precise correlation)
    if hasattr(transcript, 'words') and transcript.words:
        result["words"] = [
            {
                "word": word.word,
                "start": word.start,
                "end": word.end
            }
            for word in transcript.words
        ]

    # Save to JSON
    output_filename = Path(audio_file_path).stem + "_transcript.json"
    output_path = Path(output_dir) / output_filename

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✅ Transcription saved to: {output_path}")
    print(f"📊 Duration: {result.get('duration', 'unknown')}s")
    print(f"📊 Segments: {len(result['segments'])}")
    print(f"📊 Words: {len(result['words'])}")
    print(f"📊 Language: {result['language']}")

    return result


def extract_keywords(transcription: Dict) -> List[str]:
    """
    Extract potential issue keywords from transcription
    (Used for correlation in next step)
    """

    # Common home inspection issue keywords
    issue_keywords = [
        'crack', 'leak', 'damage', 'broken', 'missing', 'worn',
        'stain', 'mold', 'rust', 'corrosion', 'hole', 'gap',
        'loose', 'defect', 'issue', 'problem', 'concern',
        'repair', 'replace', 'recommend', 'immediate', 'safety'
    ]

    text_lower = transcription['full_text'].lower()

    found_keywords = [kw for kw in issue_keywords if kw in text_lower]

    print(f"\n🔍 Found issue keywords: {', '.join(found_keywords)}")

    return found_keywords


def get_audio_context_window(transcription: Dict, timestamp: float, window_seconds: int = 30) -> Dict:
    """
    Get audio context around a specific timestamp

    Args:
        transcription: Full transcription data
        timestamp: Timestamp in seconds
        window_seconds: How many seconds before/after to include

    Returns:
        Dict with relevant text and segments
    """

    start_time = max(0, timestamp - window_seconds)
    end_time = timestamp + window_seconds

    # Get segments in this window
    relevant_segments = [
        seg for seg in transcription['segments']
        if seg['start'] <= end_time and seg['end'] >= start_time
    ]

    # Combine text
    context_text = " ".join(seg['text'] for seg in relevant_segments)

    return {
        "timestamp": timestamp,
        "window_start": start_time,
        "window_end": end_time,
        "text": context_text,
        "segments": relevant_segments
    }


if __name__ == "__main__":
    # Test with sample audio (will be created in next step)
    sample_audio = "sample_data/audio/inspection_sample.mp3"

    if os.path.exists(sample_audio):
        result = transcribe_audio(sample_audio)
        keywords = extract_keywords(result)

        # Test context window (e.g., at 120 seconds)
        context = get_audio_context_window(result, 120, window_seconds=30)
        print(f"\n📍 Context at 120s: {context['text'][:100]}...")
    else:
        print(f"⚠️  Sample audio not found: {sample_audio}")
        print("📝 This script is ready. Add sample audio to test.")
        print("\nTo test manually:")
        print("  from poc.transcribe import transcribe_audio")
        print("  result = transcribe_audio('path/to/audio.mp3')")
