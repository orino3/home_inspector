#!/usr/bin/env python3
"""
Generate Realistic Home Inspection Photos using DALL-E 3
Creates photorealistic inspection images for testing the POC
"""

import os
import json
import requests
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Output directory
OUTPUT_DIR = Path("sample_data/realistic_photos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Inspection scenarios to generate
INSPECTION_SCENARIOS = [
    {
        "filename": "ceiling_water_stain.jpg",
        "timestamp": 30.0,
        "prompt": """Photorealistic image of a residential interior ceiling with a brown water stain.
The stain is approximately 12 inches in diameter, brownish-yellow in color, showing moisture damage.
The ceiling is white painted drywall. The photo is taken from below looking up, showing the stain clearly.
Professional home inspection photo quality, well-lit, clear details. No people in the image.""",
        "issue_type": "plumbing",
        "severity": "moderate"
    },
    {
        "filename": "gfci_outlet.jpg",
        "timestamp": 90.0,
        "prompt": """Photorealistic close-up photo of a GFCI electrical outlet on a white wall.
The outlet is beige/ivory colored with test and reset buttons visible. Professional home inspection photo,
well-lit, sharp focus on the outlet. The outlet appears to be in a bedroom or living area.
Standard residential GFCI outlet. No people in the image.""",
        "issue_type": "electrical",
        "severity": "safety_hazard"
    },
    {
        "filename": "cabinet_water_damage.jpg",
        "timestamp": 145.0,
        "prompt": """Photorealistic photo looking inside a kitchen sink cabinet showing water damage.
The cabinet bottom is particle board with visible warping and discoloration from water exposure.
Dark stains and warping visible. Plumbing pipes visible in the background.
Professional home inspection photo, interior cabinet view, clear lighting showing the damage.
No people in the image.""",
        "issue_type": "plumbing",
        "severity": "minor"
    },
    {
        "filename": "roof_shingle_damage.jpg",
        "timestamp": 200.0,
        "prompt": """Photorealistic photo of damaged roof shingles on a residential home.
Several asphalt shingles are curling, cracked, or missing. Close-up view showing deteriorated shingles.
Taken from roof level. Professional home inspection photo quality, daylight, clear details of damage.
No people in the image.""",
        "issue_type": "roof",
        "severity": "major"
    },
    {
        "filename": "foundation_crack.jpg",
        "timestamp": 250.0,
        "prompt": """Photorealistic photo of a concrete foundation wall with a vertical crack.
The crack is approximately 1/8 inch wide, running vertically for several feet.
Concrete is gray, some moisture staining visible. Basement or crawl space setting.
Professional home inspection photo, clear view of the crack, good lighting.
No people in the image.""",
        "issue_type": "structural",
        "severity": "major"
    },
    {
        "filename": "hvac_rust.jpg",
        "timestamp": 300.0,
        "prompt": """Photorealistic photo of a residential HVAC unit showing rust and corrosion.
Air handler or furnace with visible rust spots on the metal casing.
Close-up view showing deterioration. Professional home inspection photo,
mechanical room or basement setting, clear lighting showing rust detail.
No people in the image.""",
        "issue_type": "hvac",
        "severity": "moderate"
    }
]


def generate_inspection_photo(scenario: dict) -> str:
    """
    Generate a realistic inspection photo using DALL-E 3

    Args:
        scenario: Dict with filename, prompt, and metadata

    Returns:
        Path to saved image file
    """

    filename = scenario['filename']
    prompt = scenario['prompt']
    output_path = OUTPUT_DIR / filename

    print(f"\n📸 Generating: {filename}")
    print(f"   Issue: {scenario['issue_type']} ({scenario['severity']})")

    try:
        # Generate image with DALL-E 3
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",  # "standard" or "hd"
            style="natural",  # "natural" or "vivid" - natural is more photorealistic
            n=1
        )

        # Get the image URL
        image_url = response.data[0].url

        # Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        # Save to file
        with open(output_path, 'wb') as f:
            f.write(image_response.content)

        file_size = os.path.getsize(output_path) / 1024
        print(f"   ✅ Generated successfully ({file_size:.1f} KB)")

        return str(output_path)

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def create_photo_metadata():
    """Create metadata files for the generated photos"""

    # Photo timestamps mapping
    photo_timestamps = {
        scenario['filename']: scenario['timestamp']
        for scenario in INSPECTION_SCENARIOS
    }

    timestamps_path = Path("sample_data") / "realistic_photo_timestamps.json"
    with open(timestamps_path, 'w') as f:
        json.dump(photo_timestamps, f, indent=2)

    print(f"\n✅ Created photo timestamps: {timestamps_path}")

    # Photo metadata (issues, severity, etc.)
    photo_metadata = [
        {
            "filename": scenario['filename'],
            "timestamp": scenario['timestamp'],
            "issue_type": scenario['issue_type'],
            "severity": scenario['severity'],
            "prompt_used": scenario['prompt']
        }
        for scenario in INSPECTION_SCENARIOS
    ]

    metadata_path = Path("sample_data") / "realistic_photo_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(photo_metadata, f, indent=2)

    print(f"✅ Created photo metadata: {metadata_path}")


def main():
    print("=" * 80)
    print("GENERATING REALISTIC HOME INSPECTION PHOTOS")
    print("=" * 80)
    print(f"\nUsing DALL-E 3 API to generate {len(INSPECTION_SCENARIOS)} photorealistic images")
    print(f"Output directory: {OUTPUT_DIR}")

    generated_photos = []

    for scenario in INSPECTION_SCENARIOS:
        photo_path = generate_inspection_photo(scenario)
        if photo_path:
            generated_photos.append(photo_path)

    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"\n✅ Successfully generated {len(generated_photos)}/{len(INSPECTION_SCENARIOS)} photos")

    if generated_photos:
        print(f"\n📁 Photos saved to: {OUTPUT_DIR}")
        for photo in generated_photos:
            size = os.path.getsize(photo) / 1024
            print(f"   - {Path(photo).name} ({size:.1f} KB)")

        # Create metadata files
        create_photo_metadata()

        print("\n💰 Estimated Cost:")
        cost_per_image = 0.040  # DALL-E 3 standard quality 1024x1024 = $0.040
        total_cost = len(generated_photos) * cost_per_image
        print(f"   DALL-E 3 (1024x1024, standard): ${cost_per_image} per image")
        print(f"   Total: ${total_cost:.2f}")

        print("\n🎯 Next Steps:")
        print("   1. Review the generated photos in: sample_data/realistic_photos/")
        print("   2. Run POC test with realistic photos:")
        print("      python run_poc_with_realistic_photos.py")
        print("   3. Commit photos to repository for testing")

    else:
        print("\n❌ No photos were generated successfully")
        print("   Check your OpenAI API key and billing status")


if __name__ == "__main__":
    main()
