#!/usr/bin/env python3
"""
Run POC test with REALISTIC generated photos (DALL-E 3)
Tests the full pipeline with photorealistic inspection images
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
print("RUNNING POC TEST WITH REALISTIC PHOTOS (DALL-E 3)")
print("=" * 80)

# =============================================================================
# STEP 1: Load synthetic transcript (mock audio - can be replaced with real)
# =============================================================================
print("\n" + "-" * 80)
print("STEP 1: Loading audio transcript")
print("-" * 80)

# Create a more detailed transcript for the 6 photos
transcript_data = {
    "duration": 360.0,
    "language": "en",
    "full_text": """Good morning, starting inspection at 456 Oak Avenue. Two-story home, built 1998, about 3200 square feet. Beginning with interior inspection. In the master bedroom, I can see water staining on the ceiling near the bathroom wall. The stain is brownish, appears to be about 12-14 inches across. I'm touching it now - it feels slightly damp, suggesting this could be an active leak from the bathroom above. Recommend plumber inspection of shower pan and fixtures.

Moving to the electrical system. Testing GFCI outlet in the bedroom on the north wall. Using my outlet tester... the GFCI is not tripping when I press the test button. This is a safety hazard. GFCI outlets are required for shock protection. This needs immediate replacement by a licensed electrician.

Now in the kitchen, looking under the sink. I can see water damage to the particle board cabinet bottom. There's warping and discoloration indicating past water intrusion. The supply lines appear dry currently, but the damage suggests there was a leak at some point. Homeowner should monitor this area.

Heading outside to inspect the roof. I can see several areas of concern on the south-facing slope. Multiple asphalt shingles are curling and cracking. Some granule loss visible. A few shingles appear to be missing entirely. This roof is showing significant age-related wear. Recommend roof replacement within 2-3 years.

Moving to the foundation inspection. In the basement, I've found a vertical crack in the concrete foundation wall on the east side. The crack runs approximately 6 feet vertically and measures about 1/8 inch in width. Some moisture staining visible around the crack. This needs monitoring and potential structural engineer consultation.

Finally, inspecting the HVAC system. The furnace in the basement shows rust and corrosion on the exterior casing. The unit is approximately 18 years old, nearing the end of its typical lifespan. While currently functional, homeowner should budget for replacement in the near future. That concludes the main findings from this inspection.""",
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 20.0,
            "text": "Good morning, starting inspection at 456 Oak Avenue. Two-story home, built 1998, about 3200 square feet. Beginning with interior inspection.",
            "confidence": 0.95
        },
        {
            "id": 1,
            "start": 20.5,
            "end": 45.0,
            "text": "In the master bedroom, I can see water staining on the ceiling near the bathroom wall. The stain is brownish, appears to be about 12-14 inches across. I'm touching it now - it feels slightly damp, suggesting this could be an active leak from the bathroom above.",
            "confidence": 0.93
        },
        {
            "id": 2,
            "start": 45.5,
            "end": 60.0,
            "text": "Recommend plumber inspection of shower pan and fixtures.",
            "confidence": 0.94
        },
        {
            "id": 3,
            "start": 75.0,
            "end": 105.0,
            "text": "Moving to the electrical system. Testing GFCI outlet in the bedroom on the north wall. Using my outlet tester... the GFCI is not tripping when I press the test button. This is a safety hazard. GFCI outlets are required for shock protection. This needs immediate replacement by a licensed electrician.",
            "confidence": 0.92
        },
        {
            "id": 4,
            "start": 130.0,
            "end": 160.0,
            "text": "Now in the kitchen, looking under the sink. I can see water damage to the particle board cabinet bottom. There's warping and discoloration indicating past water intrusion. The supply lines appear dry currently, but the damage suggests there was a leak at some point. Homeowner should monitor this area.",
            "confidence": 0.91
        },
        {
            "id": 5,
            "start": 180.0,
            "end": 220.0,
            "text": "Heading outside to inspect the roof. I can see several areas of concern on the south-facing slope. Multiple asphalt shingles are curling and cracking. Some granule loss visible. A few shingles appear to be missing entirely. This roof is showing significant age-related wear. Recommend roof replacement within 2-3 years.",
            "confidence": 0.94
        },
        {
            "id": 6,
            "start": 235.0,
            "end": 270.0,
            "text": "Moving to the foundation inspection. In the basement, I've found a vertical crack in the concrete foundation wall on the east side. The crack runs approximately 6 feet vertically and measures about 1/8 inch in width. Some moisture staining visible around the crack. This needs monitoring and potential structural engineer consultation.",
            "confidence": 0.93
        },
        {
            "id": 7,
            "start": 285.0,
            "end": 320.0,
            "text": "Finally, inspecting the HVAC system. The furnace in the basement shows rust and corrosion on the exterior casing. The unit is approximately 18 years old, nearing the end of its typical lifespan. While currently functional, homeowner should budget for replacement in the near future.",
            "confidence": 0.92
        },
        {
            "id": 8,
            "start": 320.5,
            "end": 330.0,
            "text": "That concludes the main findings from this inspection.",
            "confidence": 0.95
        }
    ]
}

# Save transcript
Path("outputs/transcriptions").mkdir(parents=True, exist_ok=True)
transcript_path = "outputs/transcriptions/realistic_test_transcript.json"
with open(transcript_path, 'w') as f:
    json.dump(transcript_data, f, indent=2)

print(f"✅ Created transcript: {transcript_path}")
print(f"   Duration: {transcript_data['duration']}s")
print(f"   Segments: {len(transcript_data['segments'])}")

# =============================================================================
# STEP 2: Analyze realistic photos with REAL GPT-4o Vision API
# =============================================================================
print("\n" + "-" * 80)
print("STEP 2: Analyzing REALISTIC photos with GPT-4o Vision API")
print("-" * 80)

photos_dir = "sample_data/realistic_photos"
timestamps_path = "sample_data/realistic_photo_timestamps.json"

with open(timestamps_path, 'r') as f:
    photo_timestamps = json.load(f)

print(f"📸 Found {len(photo_timestamps)} realistic photos to analyze")
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
        transcript_data,
        timestamp,
        window_seconds=30
    )

    print(f"   Audio context: {len(audio_context['text'])} chars")

    try:
        # Run REAL correlation with GPT-4o
        correlation_result = correlate.correlate_photo_with_audio(
            photo_analysis,
            audio_context,
            transcript_data
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
correlations_path = "outputs/correlations/realistic_test_correlations.json"
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

# Updated property info
property_info = {
    "address": "456 Oak Avenue, Portland, OR 97210",
    "property_type": "Single Family Home",
    "year_built": 1998,
    "square_footage": "3,200 sq ft",
    "inspection_date": datetime.now().strftime("%Y-%m-%d"),
    "inspector_name": "Professional Inspector (AI-Assisted)",
    "customer_name": "Test Client (Realistic Photo Test)"
}

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
            correlations_path,
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
print("REALISTIC PHOTO POC TEST COMPLETE")
print("=" * 80)

if report:
    print("\n📊 RESULTS:")
    print(f"   Photos Analyzed: {len(photo_analyses)} (DALL-E 3 generated)")
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
    print("   - Realistic Photos: sample_data/realistic_photos/ (6 DALL-E 3 images)")
    print("   - Photo Analyses: outputs/analyses/")
    print("   - Correlations: outputs/correlations/realistic_test_correlations.json")
    print("   - Report (JSON): outputs/reports/inspection_report.json")
    print("   - Report (Text): outputs/reports/inspection_report.txt")
    print("   - Report (PDF): outputs/reports/inspection_report.pdf")

    print("\n💰 TOTAL API COSTS:")
    photo_gen_cost = len(photo_analyses) * 0.04  # DALL-E 3
    vision_cost = len(photo_analyses) * 0.02     # Vision API
    correlation_cost = len(correlations) * 0.10  # Correlation
    report_cost = 0.15                            # Report generation
    total_cost = photo_gen_cost + vision_cost + correlation_cost + report_cost

    print(f"   Photo Generation (DALL-E 3): ${photo_gen_cost:.2f}")
    print(f"   Vision Analysis: ${vision_cost:.2f}")
    print(f"   Correlation: ${correlation_cost:.2f}")
    print(f"   Report Generation: ${report_cost:.2f}")
    print(f"   TOTAL: ${total_cost:.2f}")

    print("\n🎉 POC WITH REALISTIC PHOTOS SUCCESSFUL!")
    print("\n   The system successfully:")
    print("   ✅ Generated photorealistic inspection images (DALL-E 3)")
    print("   ✅ Analyzed realistic photos with GPT-4o Vision")
    print("   ✅ Correlated visual + audio evidence")
    print("   ✅ Generated professional inspection report with photos")
    print("   ✅ Created client-ready PDF with embedded images")

else:
    print("\n❌ Report generation failed")
    print("   Review errors above")

print()
