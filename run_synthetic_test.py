#!/usr/bin/env python3
"""
Run POC test with synthetic data and REAL API calls
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add poc directory to path
sys.path.insert(0, str(Path(__file__).parent / "poc"))

# Import POC modules directly
import importlib.util

# Load analyze_photos module
spec = importlib.util.spec_from_file_location("analyze_photos", "poc/2_analyze_photos.py")
analyze_photos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze_photos)

# Load correlate module
spec = importlib.util.spec_from_file_location("correlate", "poc/3_correlate.py")
correlate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(correlate)

# Load generate_report module
spec = importlib.util.spec_from_file_location("generate_report", "poc/4_generate_report.py")
generate_report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_report)

# Load generate_pdf module
spec = importlib.util.spec_from_file_location("generate_pdf", "poc/5_generate_pdf.py")
generate_pdf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_pdf)

print("=" * 80)
print("RUNNING POC TEST WITH SYNTHETIC DATA + REAL APIs")
print("=" * 80)

# =============================================================================
# STEP 1: Load synthetic transcript (skip Whisper API call to save cost)
# =============================================================================
print("\n" + "-" * 80)
print("STEP 1: Loading synthetic transcript")
print("-" * 80)

transcript_path = "outputs/transcriptions/inspection_sample_transcript.json"
with open(transcript_path, 'r') as f:
    transcription = json.load(f)

print(f"✅ Loaded transcript: {transcript_path}")
print(f"   Duration: {transcription['duration']}s")
print(f"   Segments: {len(transcription['segments'])}")
print(f"   Full text length: {len(transcription['full_text'])} chars")

# =============================================================================
# STEP 2: Analyze photos with REAL GPT-4o Vision API
# =============================================================================
print("\n" + "-" * 80)
print("STEP 2: Analyzing photos with REAL GPT-4o Vision API")
print("-" * 80)

photos_dir = "sample_data/photos"
timestamps_path = "sample_data/photo_timestamps.json"

with open(timestamps_path, 'r') as f:
    photo_timestamps = json.load(f)

print(f"📸 Found {len(photo_timestamps)} photos to analyze")
print()

# Analyze each photo with REAL API
photo_analyses = []
for photo_filename, timestamp in photo_timestamps.items():
    photo_path = Path(photos_dir) / photo_filename

    print(f"Analyzing: {photo_filename} (timestamp: {timestamp}s)")

    try:
        analysis = analyze_photos.analyze_photo(
            str(photo_path),
            photo_timestamp=timestamp
        )
        photo_analyses.append(analysis)
        print(f"   ✅ Analysis complete")
        print(f"   Issues detected: {len(analysis['analysis']['issues_detected'])}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        # Continue with other photos

print(f"\n✅ Analyzed {len(photo_analyses)} photos with REAL Vision API")

# =============================================================================
# STEP 3: Correlate photos with audio using REAL GPT-4o API
# =============================================================================
print("\n" + "-" * 80)
print("STEP 3: Correlating photos with audio context (REAL API)")
print("-" * 80)

correlations = []
for photo_analysis in photo_analyses:
    photo_name = Path(photo_analysis['photo_path']).name
    timestamp = photo_analysis['photo_timestamp']

    print(f"\nCorrelating: {photo_name}")
    print(f"   Timestamp: {timestamp}s")

    # Get audio context window
    audio_context = correlate.get_audio_context_at_timestamp(
        transcription,
        timestamp,
        window_seconds=30
    )

    print(f"   Audio context: {len(audio_context['text'])} chars")

    try:
        # Run REAL correlation with GPT-4o
        correlation_result = correlate.correlate_photo_with_audio(
            photo_analysis,
            audio_context,
            transcription
        )

        correlations.append({
            "photo_path": photo_analysis['photo_path'],
            "photo_timestamp": timestamp,
            "photo_analysis": photo_analysis,
            "audio_context": audio_context,
            "correlation": correlation_result
        })

        print(f"   ✅ Correlation complete")
        print(f"   Correlated issues: {len(correlation_result['correlated_issues'])}")
        print(f"   Confidence: {correlation_result['correlation_quality']['confidence']}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

# Save correlations
correlations_path = "outputs/correlations/synthetic_test_correlations.json"
Path("outputs/correlations").mkdir(parents=True, exist_ok=True)
with open(correlations_path, 'w') as f:
    json.dump(correlations, f, indent=2)

print(f"\n✅ Saved correlations to: {correlations_path}")

# =============================================================================
# STEP 4: Generate report using REAL GPT-4o API
# =============================================================================
print("\n" + "-" * 80)
print("STEP 4: Generating professional report (REAL API)")
print("-" * 80)

# Load property info
with open("sample_data/property_info.json", 'r') as f:
    property_info = json.load(f)

try:
    # Generate REAL report
    report = generate_report.generate_full_report(
        correlations,
        property_info,
        output_dir="outputs/reports"
    )

    print(f"\n✅ Report generation complete")

    # Generate PDF report
    print("\n📄 Generating PDF report...")
    try:
        pdf_path = generate_pdf.generate_pdf_report(
            "outputs/reports/inspection_report.json",
            "outputs/correlations/synthetic_test_correlations.json",
            property_info
        )
        pdf_size = os.path.getsize(pdf_path) / 1024
        print(f"   ✅ PDF generated: {pdf_path}")
        print(f"   File size: {pdf_size:.1f} KB")
    except Exception as e:
        print(f"   ❌ Error generating PDF: {e}")

except Exception as e:
    print(f"\n❌ Error generating report: {e}")
    report = None

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("POC TEST COMPLETE")
print("=" * 80)

if report:
    print("\n📊 RESULTS:")
    print(f"   Audio Duration: {transcription['duration']}s")
    print(f"   Photos Analyzed: {len(photo_analyses)}")
    print(f"   Correlations Created: {len(correlations)}")
    print(f"   Total Issues Detected: {report['statistics']['total_issues']}")
    print(f"   Overall Condition: {report['overall_condition']['text']} ({report['overall_condition']['rating']}/5)")

    print("\n🔍 ISSUES BY SEVERITY:")
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

    print("\n📁 OUTPUT FILES:")
    print("   - Transcript: outputs/transcriptions/inspection_sample_transcript.json")
    print("   - Photo Analyses: outputs/analyses/")
    print("   - Correlations: outputs/correlations/synthetic_test_correlations.json")
    print("   - Report (JSON): outputs/reports/inspection_report.json")
    print("   - Report (Text): outputs/reports/inspection_report.txt")
    print("   - Report (PDF): outputs/reports/inspection_report.pdf")

    print("\n✅ Review the full report at: outputs/reports/inspection_report.txt")
    print()

    # Show cost estimate
    print("💰 ESTIMATED API COSTS:")
    vision_cost = len(photo_analyses) * 0.02  # ~$0.02 per image
    correlation_cost = len(correlations) * 0.10  # ~$0.10 per correlation
    report_cost = 0.15  # Report generation
    total_cost = vision_cost + correlation_cost + report_cost

    print(f"   Vision Analysis: ${vision_cost:.3f}")
    print(f"   Correlation: ${correlation_cost:.3f}")
    print(f"   Report Generation: ${report_cost:.3f}")
    print(f"   TOTAL: ${total_cost:.3f}")

    print("\n🎉 POC VALIDATION SUCCESSFUL!")
    print("\nNext Steps:")
    print("   1. Review the generated report quality")
    print("   2. Validate accuracy of issue detection and correlation")
    print("   3. If accuracy >80%, proceed to production backend build")

else:
    print("\n❌ Report generation failed")
    print("   Review errors above and check API key configuration")

print()
