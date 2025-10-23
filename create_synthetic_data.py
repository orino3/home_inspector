#!/usr/bin/env python3
"""
Create synthetic test data for POC validation
This creates mock inspection data that we'll process with REAL APIs
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Create directories
Path("sample_data/audio").mkdir(parents=True, exist_ok=True)
Path("sample_data/photos").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("CREATING SYNTHETIC TEST DATA")
print("=" * 80)

# ============================================================================
# 1. Create Mock Audio Transcript
# ============================================================================
print("\n1. Creating synthetic audio transcript...")

# This simulates what Whisper would return
# In real test, we'd call Whisper API with actual audio
mock_transcript = {
    "file": "sample_data/audio/inspection_sample.mp3",
    "duration": 180.0,  # 3 minutes
    "language": "en",
    "full_text": """
    Good morning, I'm starting the inspection at 123 Main Street.
    This is a single-family home built in 1985, approximately 2400 square feet.

    I'm now in the master bedroom on the second floor. Looking up at the ceiling,
    I can see a water stain approximately 12 inches in diameter near the bathroom wall.
    The stain appears to be brownish in color, which typically indicates an old leak.
    However, I'm touching it now and it feels slightly damp, so this could be an active leak.
    I recommend having a licensed plumber investigate the shower pan in the bathroom above
    to determine the source. This is a moderate concern that should be addressed soon.

    Moving to the electrical outlet on the north wall near the window. I'm testing
    this GFCI outlet with my tester... and it's not tripping. The GFCI is not functioning
    properly. This is a safety hazard because GFCI outlets are required in bedrooms
    for protection against electrical shock. This outlet should be replaced immediately
    by a licensed electrician. I'm marking this as a major safety concern.

    Now I'm heading down to the kitchen. Looking at the cabinet under the sink,
    I can see some water damage to the particle board. There's warping and discoloration,
    which indicates past water intrusion. Checking the pipes... they appear to be dry now,
    but the damage suggests there was a leak at some point. The homeowner should monitor
    this area and consider replacing the damaged cabinet bottom. This is a minor issue.

    That concludes the main areas of concern I found during this inspection.
    """,
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 15.0,
            "text": "Good morning, I'm starting the inspection at 123 Main Street. This is a single-family home built in 1985, approximately 2400 square feet.",
            "confidence": 0.95
        },
        {
            "id": 1,
            "start": 15.5,
            "end": 35.0,
            "text": "I'm now in the master bedroom on the second floor. Looking up at the ceiling, I can see a water stain approximately 12 inches in diameter near the bathroom wall.",
            "confidence": 0.92
        },
        {
            "id": 2,
            "start": 35.5,
            "end": 55.0,
            "text": "The stain appears to be brownish in color, which typically indicates an old leak. However, I'm touching it now and it feels slightly damp, so this could be an active leak.",
            "confidence": 0.94
        },
        {
            "id": 3,
            "start": 55.5,
            "end": 75.0,
            "text": "I recommend having a licensed plumber investigate the shower pan in the bathroom above to determine the source. This is a moderate concern that should be addressed soon.",
            "confidence": 0.93
        },
        {
            "id": 4,
            "start": 76.0,
            "end": 95.0,
            "text": "Moving to the electrical outlet on the north wall near the window. I'm testing this GFCI outlet with my tester... and it's not tripping.",
            "confidence": 0.91
        },
        {
            "id": 5,
            "start": 95.5,
            "end": 115.0,
            "text": "The GFCI is not functioning properly. This is a safety hazard because GFCI outlets are required in bedrooms for protection against electrical shock.",
            "confidence": 0.94
        },
        {
            "id": 6,
            "start": 115.5,
            "end": 130.0,
            "text": "This outlet should be replaced immediately by a licensed electrician. I'm marking this as a major safety concern.",
            "confidence": 0.96
        },
        {
            "id": 7,
            "start": 131.0,
            "end": 150.0,
            "text": "Now I'm heading down to the kitchen. Looking at the cabinet under the sink, I can see some water damage to the particle board.",
            "confidence": 0.93
        },
        {
            "id": 8,
            "start": 150.5,
            "end": 165.0,
            "text": "There's warping and discoloration, which indicates past water intrusion. Checking the pipes... they appear to be dry now, but the damage suggests there was a leak at some point.",
            "confidence": 0.92
        },
        {
            "id": 9,
            "start": 165.5,
            "end": 180.0,
            "text": "The homeowner should monitor this area and consider replacing the damaged cabinet bottom. This is a minor issue. That concludes the main areas of concern I found during this inspection.",
            "confidence": 0.94
        }
    ],
    "words": []  # Would be populated by real Whisper API
}

# Save transcript
transcript_path = "outputs/transcriptions/inspection_sample_transcript.json"
Path("outputs/transcriptions").mkdir(parents=True, exist_ok=True)
with open(transcript_path, 'w') as f:
    json.dump(mock_transcript, f, indent=2)

print(f"   ✅ Created mock transcript: {transcript_path}")
print(f"   Duration: {mock_transcript['duration']}s")
print(f"   Segments: {len(mock_transcript['segments'])}")

# ============================================================================
# 2. Create Synthetic Photos
# ============================================================================
print("\n2. Creating synthetic inspection photos...")

# Create simple test images that represent the issues mentioned in the narration
photos = [
    {
        "filename": "photo1_ceiling_stain.jpg",
        "timestamp": 30.0,  # Mentioned at ~30 seconds
        "description": "Water stain on bedroom ceiling - brownish discoloration",
        "text_on_image": "WATER STAIN\nCeiling - Master Bedroom"
    },
    {
        "filename": "photo2_gfci_outlet.jpg",
        "timestamp": 90.0,  # Mentioned at ~90 seconds
        "description": "GFCI electrical outlet on bedroom wall",
        "text_on_image": "GFCI OUTLET\nNot Functioning"
    },
    {
        "filename": "photo3_cabinet_damage.jpg",
        "timestamp": 145.0,  # Mentioned at ~145 seconds
        "description": "Water damaged cabinet under kitchen sink",
        "text_on_image": "CABINET DAMAGE\nUnder Kitchen Sink"
    }
]

for photo_info in photos:
    # Create a simple image with text
    img = Image.new('RGB', (800, 600), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)

    # Add colored rectangle to simulate the issue area
    if "stain" in photo_info["filename"]:
        # Brown stain
        draw.rectangle([300, 200, 500, 350], fill=(139, 90, 43))
    elif "gfci" in photo_info["filename"]:
        # White outlet
        draw.rectangle([300, 200, 500, 400], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
        # Outlet holes
        draw.ellipse([350, 250, 380, 280], fill=(50, 50, 50))
        draw.ellipse([420, 250, 450, 280], fill=(50, 50, 50))
        draw.ellipse([350, 320, 380, 350], fill=(50, 50, 50))
        draw.ellipse([420, 320, 450, 350], fill=(50, 50, 50))
    elif "cabinet" in photo_info["filename"]:
        # Warped wood
        draw.rectangle([200, 300, 600, 500], fill=(101, 67, 33))
        # Warping/damage lines
        for i in range(5):
            y = 320 + i * 35
            draw.line([(220, y), (580, y + 10)], fill=(80, 50, 20), width=2)

    # Add text label
    try:
        # Try to use a default font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        # Fallback to default
        font = ImageFont.load_default()

    # Add text
    lines = photo_info["text_on_image"].split('\n')
    y_offset = 50
    for line in lines:
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (800 - text_width) // 2

        # Draw text with shadow for visibility
        draw.text((x+2, y_offset+2), line, fill=(0, 0, 0), font=font)
        draw.text((x, y_offset), line, fill=(200, 0, 0), font=font)
        y_offset += 50

    # Save image
    photo_path = f"sample_data/photos/{photo_info['filename']}"
    img.save(photo_path)
    print(f"   ✅ Created: {photo_info['filename']} (timestamp: {photo_info['timestamp']}s)")

print(f"\n   Total photos created: {len(photos)}")

# ============================================================================
# 3. Create Photo Timestamp Mapping
# ============================================================================
print("\n3. Creating photo timestamp mapping...")

photo_timestamps = {
    photo["filename"]: photo["timestamp"]
    for photo in photos
}

mapping_path = "sample_data/photo_timestamps.json"
with open(mapping_path, 'w') as f:
    json.dump(photo_timestamps, f, indent=2)

print(f"   ✅ Created: {mapping_path}")

# ============================================================================
# 4. Create Property Info
# ============================================================================
print("\n4. Creating property information...")

property_info = {
    "address": "123 Main Street, Springfield, IL 62701",
    "property_type": "Single Family Home",
    "year_built": "1985",
    "square_footage": "2,400 sq ft",
    "inspection_date": "2025-10-23",
    "customer_name": "John Doe (Synthetic Test)",
    "inspector_name": "AI Test Inspector"
}

property_path = "sample_data/property_info.json"
with open(property_path, 'w') as f:
    json.dump(property_info, f, indent=2)

print(f"   ✅ Created: {property_path}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("SYNTHETIC DATA CREATION COMPLETE")
print("=" * 80)

print(f"""
✅ Created:
   - Mock audio transcript (simulates Whisper output)
   - 3 synthetic photos (simple images with labels)
   - Photo timestamp mapping
   - Property information

📁 Files created:
   - outputs/transcriptions/inspection_sample_transcript.json
   - sample_data/photos/photo1_ceiling_stain.jpg
   - sample_data/photos/photo2_gfci_outlet.jpg
   - sample_data/photos/photo3_cabinet_damage.jpg
   - sample_data/photo_timestamps.json
   - sample_data/property_info.json

🎯 Next steps:
   1. Run photo analysis with REAL GPT-4o Vision API
   2. Run correlation engine
   3. Generate report

   Run: python run_poc_test.py
""")
