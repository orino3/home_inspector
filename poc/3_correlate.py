#!/usr/bin/env python3
"""
POC Script 3: Audio-Photo Correlation
Correlates photos with audio context to generate comprehensive issue descriptions
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def load_transcription(transcription_path: str) -> Dict:
    """Load transcription JSON"""
    with open(transcription_path, 'r') as f:
        return json.load(f)


def load_analysis(analysis_path: str) -> Dict:
    """Load photo analysis JSON"""
    with open(analysis_path, 'r') as f:
        return json.load(f)


def get_audio_context_at_timestamp(transcription: Dict, timestamp: float, window_seconds: int = 30) -> Dict:
    """
    Get audio context around a photo timestamp

    Args:
        transcription: Full transcription data
        timestamp: Photo timestamp in seconds
        window_seconds: Context window size (seconds before/after)

    Returns:
        Dict with relevant audio context
    """

    start_time = max(0, timestamp - window_seconds)
    end_time = timestamp + window_seconds

    # Get segments in this window
    relevant_segments = [
        seg for seg in transcription.get('segments', [])
        if seg['start'] <= end_time and seg['end'] >= start_time
    ]

    # Combine text
    context_text = " ".join(seg['text'] for seg in relevant_segments)

    return {
        "timestamp": timestamp,
        "window_start": start_time,
        "window_end": end_time,
        "text": context_text.strip(),
        "segments": relevant_segments,
        "segment_count": len(relevant_segments)
    }


def correlate_photo_with_audio(
    photo_analysis: Dict,
    audio_context: Dict,
    transcription: Dict
) -> Dict:
    """
    Use GPT-5 to correlate photo analysis with audio context

    This is the MAGIC - AI combines what it sees with what inspector said

    Args:
        photo_analysis: Photo analysis results from script 2
        audio_context: Audio context window
        transcription: Full transcription for additional context

    Returns:
        Correlated issue data
    """

    photo_path = photo_analysis['photo_path']
    timestamp = photo_analysis.get('photo_timestamp')

    print(f"🔗 Correlating photo: {Path(photo_path).name} @ {timestamp}s")

    # Extract photo analysis
    vision_analysis = photo_analysis.get('analysis', {})
    issues_from_vision = vision_analysis.get('issues_detected', [])

    # Prepare correlation prompt
    prompt = f"""You are correlating a home inspection photo with the inspector's audio narration.

**PHOTO ANALYSIS:**
Location: {vision_analysis.get('location', 'Unknown')}
Visible Elements: {', '.join(vision_analysis.get('visible_elements', []))}
Issues Detected in Photo: {json.dumps(issues_from_vision, indent=2)}
Overall Assessment: {vision_analysis.get('overall_assessment', 'N/A')}

**WHAT INSPECTOR SAID (at this moment):**
Timestamp: {timestamp}s
Audio Context: "{audio_context['text']}"

**TASK:**
Combine the visual analysis with the inspector's words to create comprehensive issue descriptions.

For each issue:
1. Match visual findings with audio mentions
2. Create a professional description using BOTH sources
3. Extract specific details from audio (measurements, observations, concerns)
4. Determine if inspector mentioned severity or urgency
5. Note any recommendations inspector stated

Return JSON:
{{
  "correlated_issues": [
    {{
      "title": "Concise issue title",
      "description": "Professional description combining vision + audio",
      "category": "structural|electrical|plumbing|hvac|roof|exterior|interior|safety|other",
      "severity": "informational|minor|moderate|major|safety_hazard",
      "location": "Specific location",
      "evidence": {{
        "from_photo": "What we see in the photo",
        "from_audio": "What inspector said about it",
        "correlation_confidence": 0.0-1.0
      }},
      "recommendations": "What should be done",
      "inspector_notes": "Any specific comments from inspector"
    }}
  ],
  "correlation_quality": {{
    "audio_context_relevant": true/false,
    "issues_mentioned_in_audio": 0-N,
    "confidence_score": 0.0-1.0,
    "reasoning": "Why this correlation was made"
  }}
}}

If audio doesn't mention this area, still include issues from photo but note low correlation.
"""

    # Call GPT-4o (best for structured JSON output - 100% reliability)
    response = client.chat.completions.create(
        model="gpt-4o",  # Using GPT-4o - best for reliable structured outputs
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=2000,
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    # Parse response
    correlation_result = json.loads(response.choices[0].message.content)

    # Add metadata
    result = {
        "photo_path": photo_path,
        "photo_timestamp": timestamp,
        "audio_context_used": audio_context,
        "correlation": correlation_result,
        "model_used": "gpt-4o"
    }

    # Print summary
    correlated_issues = correlation_result.get('correlated_issues', [])
    print(f"   ✅ Correlated {len(correlated_issues)} issues")

    quality = correlation_result.get('correlation_quality', {})
    confidence = quality.get('confidence_score', 0)
    print(f"   📊 Correlation confidence: {confidence:.2%}")

    return result


def correlate_all_photos(
    photo_analyses: List[Dict],
    transcription: Dict,
    output_dir: str = "outputs/correlations"
) -> List[Dict]:
    """
    Correlate all photos with audio

    Args:
        photo_analyses: List of photo analysis results
        transcription: Full transcription data
        output_dir: Output directory

    Returns:
        List of correlation results
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    correlations = []

    print(f"\n🔗 Correlating {len(photo_analyses)} photos with audio...\n")

    for i, photo_analysis in enumerate(photo_analyses, 1):
        print(f"[{i}/{len(photo_analyses)}]", end=" ")

        # Get timestamp
        timestamp = photo_analysis.get('photo_timestamp')

        if timestamp is None:
            print(f"⚠️  No timestamp for {photo_analysis['photo_path']}, skipping")
            continue

        # Get audio context
        audio_context = get_audio_context_at_timestamp(transcription, timestamp)

        # Correlate
        correlation = correlate_photo_with_audio(
            photo_analysis,
            audio_context,
            transcription
        )

        correlations.append(correlation)

    # Save all correlations
    output_path = Path(output_dir) / "all_correlations.json"
    with open(output_path, 'w') as f:
        json.dump(correlations, f, indent=2)

    print(f"\n✅ All correlations saved to: {output_path}")

    # Summary statistics
    total_issues = sum(
        len(c['correlation'].get('correlated_issues', []))
        for c in correlations
    )

    avg_confidence = sum(
        c['correlation'].get('correlation_quality', {}).get('confidence_score', 0)
        for c in correlations
    ) / len(correlations) if correlations else 0

    print(f"\n📊 CORRELATION SUMMARY:")
    print(f"   Photos processed: {len(correlations)}")
    print(f"   Total issues correlated: {total_issues}")
    print(f"   Average confidence: {avg_confidence:.2%}")

    return correlations


if __name__ == "__main__":
    # Test correlation
    transcript_file = "outputs/transcriptions/inspection_sample_transcript.json"
    analyses_dir = "outputs/analyses"

    if os.path.exists(transcript_file) and os.path.exists(analyses_dir):
        # Load transcription
        transcription = load_transcription(transcript_file)

        # Load all photo analyses
        analysis_files = list(Path(analyses_dir).glob("*_analysis.json"))
        photo_analyses = [load_analysis(str(f)) for f in analysis_files]

        # Correlate
        correlations = correlate_all_photos(photo_analyses, transcription)

    else:
        print("⚠️  Missing transcription or photo analyses")
        print("📝 Run scripts 1 and 2 first:")
        print("   python poc/1_transcribe.py")
        print("   python poc/2_analyze_photos.py")
