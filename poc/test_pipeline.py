#!/usr/bin/env python3
"""
POC End-to-End Test Pipeline
Runs the complete workflow: Audio -> Photos -> Correlation -> Report
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add poc directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our POC modules
from poc import transcribe, analyze_photos, correlate, generate_report


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_section(text: str):
    """Print formatted section"""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80 + "\n")


def run_full_pipeline(
    audio_file: str,
    photos_dir: str,
    photo_timestamps: dict,
    property_info: dict
):
    """
    Run complete POC pipeline

    Args:
        audio_file: Path to inspection audio file
        photos_dir: Directory containing inspection photos
        photo_timestamps: Dict mapping photo filenames to timestamps
        property_info: Property information dict

    Returns:
        Final report dict
    """

    print_header("HOME INSPECTOR AI - PHASE 0 POC PIPELINE")

    start_time = datetime.now()

    # ==========================================================================
    # STEP 1: TRANSCRIBE AUDIO
    # ==========================================================================
    print_section("STEP 1: Transcribing Audio")

    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        print("\n📝 To test the POC, you need:")
        print("   1. Sample audio file (inspector narration)")
        print("   2. Sample photos from the inspection")
        print("   3. Timestamps linking photos to audio")
        print("\nSee sample_data/README.md for instructions.")
        return None

    transcription = transcribe.transcribe_audio(audio_file)
    keywords = transcribe.extract_keywords(transcription)

    # ==========================================================================
    # STEP 2: ANALYZE PHOTOS
    # ==========================================================================
    print_section("STEP 2: Analyzing Photos with Vision AI")

    photo_analyses = analyze_photos.analyze_multiple_photos(photos_dir, photo_timestamps)

    if not photo_analyses:
        print("❌ No photos to analyze")
        return None

    # ==========================================================================
    # STEP 3: CORRELATE PHOTOS WITH AUDIO
    # ==========================================================================
    print_section("STEP 3: Correlating Photos with Audio Context")

    correlations = correlate.correlate_all_photos(photo_analyses, transcription)

    # ==========================================================================
    # STEP 4: GENERATE REPORT
    # ==========================================================================
    print_section("STEP 4: Generating Professional Report")

    report = generate_report.generate_full_report(correlations, property_info)

    # ==========================================================================
    # SUMMARY
    # ==========================================================================
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print_header("POC PIPELINE COMPLETE!")

    print("📊 RESULTS:")
    print(f"   Audio Duration: {transcription.get('duration', 'unknown')}s")
    print(f"   Photos Processed: {len(photo_analyses)}")
    print(f"   Issues Detected: {report['statistics']['total_issues']}")
    print(f"   Overall Condition: {report['overall_condition']['text']}")
    print(f"   Processing Time: {duration:.1f}s")
    print("")
    print("📁 OUTPUT FILES:")
    print(f"   Transcription: outputs/transcriptions/")
    print(f"   Photo Analyses: outputs/analyses/")
    print(f"   Correlations: outputs/correlations/")
    print(f"   Report (JSON): outputs/reports/inspection_report.json")
    print(f"   Report (Text): outputs/reports/inspection_report.txt")
    print("")

    # Issues breakdown
    print("🔍 ISSUES BY SEVERITY:")
    for severity, count in report['statistics']['by_severity'].items():
        if count > 0:
            emoji = {
                'safety_hazard': '🚨',
                'major': '⚠️',
                'moderate': '⚠️',
                'minor': '📋',
                'informational': 'ℹ️'
            }.get(severity, '📋')
            print(f"   {emoji} {severity.replace('_', ' ').title()}: {count}")
    print("")

    # Cost estimation
    print("💰 ESTIMATED API COSTS:")
    # Rough estimation based on OpenAI pricing
    transcription_cost = (transcription.get('duration', 0) / 60) * 0.006  # $0.006/min
    vision_cost = len(photo_analyses) * 0.02  # ~$0.02 per image
    reasoning_cost = 0.05  # Correlation + report generation
    total_cost = transcription_cost + vision_cost + reasoning_cost

    print(f"   Transcription: ${transcription_cost:.3f}")
    print(f"   Vision Analysis: ${vision_cost:.3f}")
    print(f"   Reasoning: ${reasoning_cost:.3f}")
    print(f"   TOTAL: ${total_cost:.3f}")
    print("")

    print("✅ Review the text report at: outputs/reports/inspection_report.txt")
    print("")

    return report


def create_sample_data_instructions():
    """Create instructions for sample data"""

    instructions = """# Sample Data Instructions

To test the POC pipeline, you need:

## 1. Audio File

Record a short home inspection walkthrough (3-5 minutes is enough for POC):

**Example narration:**
```
"I'm now in the master bedroom. The room is approximately 12 by 14 feet.
Looking at the ceiling, I notice a water stain near the bathroom wall.
This appears to be an active leak, possibly from the shower pan above.
I recommend having a plumber investigate this immediately.

Moving to the electrical outlet near the window, I'm testing the GFCI...
The GFCI is not functioning properly. This is a safety concern and should
be replaced by a licensed electrician..."
```

**Format:** MP3, WAV, or M4A
**Save to:** `sample_data/audio/inspection_sample.mp3`

## 2. Photos

Take 3-5 photos corresponding to your narration:

- `photo1.jpg` - Water stain on ceiling (timestamp: 30s in audio)
- `photo2.jpg` - GFCI outlet (timestamp: 95s in audio)
- `photo3.jpg` - Another issue (timestamp: 150s in audio)

**Save to:** `sample_data/photos/`

## 3. Photo Timestamps

In `test_pipeline.py`, update the `photo_timestamps` dict:

```python
photo_timestamps = {
    "photo1.jpg": 30.0,   # Water stain mentioned at 30s
    "photo2.jpg": 95.0,   # GFCI mentioned at 95s
    "photo3.jpg": 150.0   # Another issue at 150s
}
```

## 4. Run the Test

```bash
python poc/test_pipeline.py
```

## Alternative: Use Online Samples

Can't record your own? Use free home inspection footage:
- YouTube: Search "home inspection walkthrough"
- Download audio using yt-dlp or similar
- Extract relevant frames as photos

Remember: This is just for POC testing. Production system will handle
real inspector data automatically.
"""

    sample_readme_path = "sample_data/README.md"
    with open(sample_readme_path, 'w') as f:
        f.write(instructions)

    print(f"📝 Created instructions: {sample_readme_path}")


if __name__ == "__main__":
    # Check if sample data exists
    audio_file = "sample_data/audio/inspection_sample.mp3"
    photos_dir = "sample_data/photos"

    # Create instructions if sample data doesn't exist
    if not os.path.exists(audio_file):
        print("\n⚠️  Sample data not found!")
        print("\nCreating instructions for sample data...")
        create_sample_data_instructions()
        print("\n📝 See sample_data/README.md for instructions")
        print("\nOnce you have sample data, run:")
        print("   python poc/test_pipeline.py")
        sys.exit(0)

    # Example property info
    property_info = {
        "address": "123 Main Street, Springfield, IL 62701",
        "property_type": "Single Family Home",
        "year_built": "1985",
        "square_footage": "2,400 sq ft",
        "inspection_date": datetime.now().strftime('%Y-%m-%d'),
        "customer_name": "John Doe",
        "inspector_name": "Professional Inspector LLC"
    }

    # Photo timestamps (UPDATE THESE to match your audio)
    photo_timestamps = {
        "photo1.jpg": 30.0,   # Timestamp in seconds when this photo relates to audio
        "photo2.jpg": 95.0,
        "photo3.jpg": 150.0
        # Add more as needed
    }

    # Run the pipeline!
    report = run_full_pipeline(
        audio_file=audio_file,
        photos_dir=photos_dir,
        photo_timestamps=photo_timestamps,
        property_info=property_info
    )

    if report:
        print("🎉 POC VALIDATION SUCCESSFUL!")
        print("\nNext steps:")
        print("1. Review the generated report")
        print("2. Validate accuracy against known issues")
        print("3. If accuracy >80%, POC is successful!")
        print("4. Proceed to build production system")
