#!/usr/bin/env python3
"""
Generate Realistic Home Inspection Photos - iPhone 16 Style
Creates photorealistic inspection images that look like iPhone 16 photos
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
OUTPUT_DIR = Path("sample_data/iphone_photos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# iPhone 16 photography characteristics to include in prompts:
# - Natural smartphone photography angle
# - Good dynamic range (HDR-like)
# - Slightly wide angle lens perspective
# - Natural colors with good white balance
# - Sharp detail typical of modern phone cameras
# - Hand-held casual perspective

# Expanded inspection scenarios
INSPECTION_SCENARIOS = [
    # INTERIOR ISSUES
    {
        "filename": "ceiling_water_stain.jpg",
        "timestamp": 30.0,
        "prompt": """Photo taken with iPhone 16 showing a residential bedroom ceiling with a brown water stain.
The stain is approximately 12 inches in diameter, brownish-yellow color showing moisture damage.
White painted drywall ceiling. Shot from below looking up at an angle, typical smartphone perspective.
Natural indoor lighting, good dynamic range, sharp iPhone camera quality. Casual hand-held angle.
No people in frame. Realistic iPhone 16 photo characteristics.""",
        "issue_type": "interior",
        "severity": "moderate",
        "category": "Water Damage"
    },
    {
        "filename": "window_condensation.jpg",
        "timestamp": 60.0,
        "prompt": """iPhone 16 photo of a double-pane window with condensation between the glass panes.
Water droplets and fog visible between the two panes indicating seal failure.
Residential interior window, white frame. Natural daylight coming through the window.
Shot straight-on from inside the room. Sharp iPhone detail, good color accuracy.
Typical smartphone casual photography style. No people visible.""",
        "issue_type": "interior",
        "severity": "minor",
        "category": "Window Issues"
    },
    {
        "filename": "hardwood_floor_damage.jpg",
        "timestamp": 85.0,
        "prompt": """iPhone 16 photo of hardwood flooring with water damage and buckling.
Medium brown hardwood planks with visible warping and discoloration from moisture.
Floor boards are uneven and lifting at the edges. Natural indoor lighting.
Shot at a slight downward angle typical of phone camera. Good depth and detail.
Realistic iPhone color balance and sharpness. No people in the shot.""",
        "issue_type": "interior",
        "severity": "moderate",
        "category": "Flooring"
    },

    # ELECTRICAL ISSUES
    {
        "filename": "gfci_outlet.jpg",
        "timestamp": 110.0,
        "prompt": """Close-up iPhone 16 photo of a beige GFCI electrical outlet on a white wall.
Test and reset buttons clearly visible. Standard residential outlet in bedroom.
Shot close-up with good focus, typical iPhone macro capability. Well-lit, sharp details.
Slight angle from below, casual hand-held perspective. Natural indoor lighting.
Clean iPhone 16 image quality. No people in frame.""",
        "issue_type": "electrical",
        "severity": "safety_hazard",
        "category": "Outlets"
    },
    {
        "filename": "electrical_panel_rust.jpg",
        "timestamp": 135.0,
        "prompt": """iPhone 16 photo of an electrical service panel showing rust and corrosion.
Gray metal panel box with visible rust stains around edges and bottom.
Circuit breakers visible inside. Basement or utility room setting with overhead lighting.
Shot straight-on from about 3 feet away. Good iPhone dynamic range showing detail.
Typical smartphone perspective and color accuracy. No people visible.""",
        "issue_type": "electrical",
        "severity": "major",
        "category": "Electrical Panel"
    },

    # PLUMBING ISSUES
    {
        "filename": "cabinet_water_damage.jpg",
        "timestamp": 160.0,
        "prompt": """iPhone 16 photo looking inside kitchen sink cabinet showing water damage.
Particle board cabinet bottom with visible warping and dark water stains.
White PVC plumbing pipes visible. Shot from above looking down into the cabinet.
Natural kitchen lighting, good iPhone HDR showing detail in shadows.
Realistic smartphone wide-angle perspective. No people in the image.""",
        "issue_type": "plumbing",
        "severity": "minor",
        "category": "Cabinets"
    },
    {
        "filename": "water_heater_leak.jpg",
        "timestamp": 185.0,
        "prompt": """iPhone 16 photo of a residential water heater with visible leak and corrosion.
White cylindrical water heater with rust stains and water pooling at the base.
Concrete floor visible, utility room or basement setting. Overhead lighting.
Shot from standing height looking slightly down, typical casual phone angle.
Good detail and color with iPhone camera quality. No people in frame.""",
        "issue_type": "plumbing",
        "severity": "major",
        "category": "Water Heater"
    },
    {
        "filename": "toilet_base_leak.jpg",
        "timestamp": 210.0,
        "prompt": """iPhone 16 photo showing water staining around the base of a toilet.
White porcelain toilet with visible water damage on floor tiles around the base.
Bathroom setting with natural and overhead lighting mixed. Tile floor.
Shot from slightly above looking down at an angle, typical smartphone perspective.
Sharp iPhone detail showing the stains clearly. No people visible.""",
        "issue_type": "plumbing",
        "severity": "moderate",
        "category": "Bathroom"
    },

    # ROOF ISSUES
    {
        "filename": "roof_shingle_damage.jpg",
        "timestamp": 235.0,
        "prompt": """iPhone 16 photo of damaged asphalt roof shingles taken from roof level.
Multiple shingles are curling, cracked, and some are missing. Gray/black asphalt shingles.
Bright daylight, good dynamic range showing texture and damage detail.
Slightly wide angle typical of iPhone camera. Hand-held casual perspective.
Clear blue sky partially visible. Sharp focus on damaged shingles. No people.""",
        "issue_type": "roof",
        "severity": "major",
        "category": "Shingles"
    },
    {
        "filename": "roof_flashing_gap.jpg",
        "timestamp": 260.0,
        "prompt": """iPhone 16 photo of roof flashing around chimney with visible gaps.
Metal flashing at brick chimney showing separation and gaps where water could enter.
Red brick chimney, asphalt shingles visible. Bright outdoor lighting.
Shot from roof level at an angle. Good iPhone color accuracy and sharpness.
Natural smartphone photography style. No people in the image.""",
        "issue_type": "roof",
        "severity": "moderate",
        "category": "Flashing"
    },

    # FOUNDATION & STRUCTURAL
    {
        "filename": "foundation_crack.jpg",
        "timestamp": 285.0,
        "prompt": """iPhone 16 photo of concrete foundation wall with vertical crack.
Gray concrete with a 1/8 inch wide vertical crack running several feet up the wall.
Some moisture staining visible around the crack. Basement setting with artificial lighting.
Shot straight-on from a few feet away. Good iPhone exposure showing crack detail.
Typical hand-held smartphone perspective. No people visible.""",
        "issue_type": "structural",
        "severity": "major",
        "category": "Foundation"
    },
    {
        "filename": "basement_support_beam_sag.jpg",
        "timestamp": 310.0,
        "prompt": """iPhone 16 photo of a wooden support beam in basement showing sagging.
Wooden beam visibly bowing downward under load. Basement ceiling joists visible.
Concrete foundation walls in background. Overhead basement lighting.
Shot from standing position looking up at an angle, typical phone perspective.
Clear detail showing the sag. Natural iPhone color and dynamic range. No people.""",
        "issue_type": "structural",
        "severity": "safety_hazard",
        "category": "Structural Support"
    },

    # HVAC ISSUES
    {
        "filename": "hvac_rust.jpg",
        "timestamp": 335.0,
        "prompt": """iPhone 16 photo of residential furnace with severe rust and corrosion.
Metal HVAC unit with visible rust spots and deterioration on the casing.
Basement or mechanical room setting. Utility room lighting.
Shot from a few feet away at chest height, typical smartphone angle.
Good detail showing rust extent. Natural iPhone image quality. No people in frame.""",
        "issue_type": "hvac",
        "severity": "moderate",
        "category": "Furnace"
    },
    {
        "filename": "ac_unit_damage.jpg",
        "timestamp": 360.0,
        "prompt": """iPhone 16 photo of outdoor AC condenser unit with damaged fins.
Air conditioning unit with bent and crushed cooling fins on the side.
Exterior residential setting, concrete pad, some grass visible. Natural daylight.
Shot from standing height looking slightly down. Good iPhone dynamic range.
Typical casual smartphone photography perspective. No people visible.""",
        "issue_type": "hvac",
        "severity": "minor",
        "category": "Air Conditioning"
    },

    # EXTERIOR ISSUES
    {
        "filename": "siding_damage.jpg",
        "timestamp": 385.0,
        "prompt": """iPhone 16 photo of vinyl house siding with cracks and damage.
Beige vinyl siding with visible cracks, warping, and a piece broken/missing.
Exterior wall of house, natural outdoor daylight. Some shadow and highlight detail.
Shot from standing position, slightly wide angle typical of iPhone.
Good color accuracy and sharpness. Casual smartphone perspective. No people.""",
        "issue_type": "exterior",
        "severity": "moderate",
        "category": "Siding"
    },
    {
        "filename": "gutter_separation.jpg",
        "timestamp": 410.0,
        "prompt": """iPhone 16 photo of rain gutter separating from house fascia.
White aluminum gutter pulling away from the roof edge, visible gap and sagging.
Residential exterior, blue sky visible in background. Bright natural daylight.
Shot from ground level looking up at an angle, typical phone camera perspective.
Good dynamic range showing detail. Natural iPhone colors. No people in frame.""",
        "issue_type": "exterior",
        "severity": "minor",
        "category": "Gutters"
    },
    {
        "filename": "deck_railing_loose.jpg",
        "timestamp": 435.0,
        "prompt": """iPhone 16 photo of wooden deck railing that is loose and wobbly.
Brown stained wood deck railing with visible gap at connection point to post.
Outdoor deck setting, natural daylight. Deck boards visible in foreground.
Shot from deck level, casual hand-held angle typical of smartphone photography.
Good detail showing the loose connection. Natural iPhone image quality. No people.""",
        "issue_type": "exterior",
        "severity": "safety_hazard",
        "category": "Deck"
    },
    {
        "filename": "driveway_cracks.jpg",
        "timestamp": 460.0,
        "prompt": """iPhone 16 photo of concrete driveway with multiple cracks and deterioration.
Gray concrete with several cracks running across, some spalling and wear visible.
Residential driveway, bright outdoor daylight casting some shadows.
Shot from standing height looking down at an angle. Slightly wide angle view.
Good iPhone detail showing crack patterns. Natural colors. No people visible.""",
        "issue_type": "exterior",
        "severity": "minor",
        "category": "Driveway"
    },

    # ATTIC ISSUES
    {
        "filename": "attic_mold.jpg",
        "timestamp": 485.0,
        "prompt": """iPhone 16 photo of attic rafters showing dark mold growth.
Wooden rafters and plywood sheathing with visible black/dark mold stains.
Attic space, some natural light from vents plus flashlight illumination.
Shot looking up at rafters from attic floor. Good iPhone exposure in low light.
Shows texture and extent of mold. Typical hand-held phone angle. No people.""",
        "issue_type": "attic",
        "severity": "safety_hazard",
        "category": "Mold"
    },
    {
        "filename": "insufficient_insulation.jpg",
        "timestamp": 510.0,
        "prompt": """iPhone 16 photo of attic floor showing inadequate insulation coverage.
Pink fiberglass insulation batts that are thin and patchy, gaps visible.
Attic space with exposed floor joists. Natural light from attic vents.
Shot looking down at the attic floor. Clear detail showing insulation gaps.
Good iPhone color accuracy. Casual smartphone perspective. No people in frame.""",
        "issue_type": "attic",
        "severity": "minor",
        "category": "Insulation"
    }
]


def generate_inspection_photo(scenario: dict) -> str:
    """
    Generate a realistic iPhone 16-style inspection photo using DALL-E 3

    Args:
        scenario: Dict with filename, prompt, and metadata

    Returns:
        Path to saved image file
    """

    filename = scenario['filename']
    prompt = scenario['prompt']
    output_path = OUTPUT_DIR / filename

    print(f"\n📸 Generating: {filename}")
    print(f"   Category: {scenario['category']} ({scenario['severity']})")

    try:
        # Generate image with GPT-image-1 (newest model, 75% cheaper than DALL-E 3)
        # Note: GPT-image-1 returns base64-encoded images, not URLs
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            # Note: GPT-image-1 doesn't have quality/style parameters like DALL-E 3
            n=1
        )

        # GPT-image-1 returns base64-encoded image data
        import base64
        b64_data = response.data[0].b64_json
        image_data = base64.b64decode(b64_data)

        # Save to file
        with open(output_path, 'wb') as f:
            f.write(image_data)

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

    timestamps_path = Path("sample_data") / "iphone_photo_timestamps.json"
    with open(timestamps_path, 'w') as f:
        json.dump(photo_timestamps, f, indent=2)

    print(f"\n✅ Created photo timestamps: {timestamps_path}")

    # Photo metadata (issues, severity, etc.)
    photo_metadata = [
        {
            "filename": scenario['filename'],
            "timestamp": scenario['timestamp'],
            "issue_type": scenario['issue_type'],
            "category": scenario['category'],
            "severity": scenario['severity'],
            "prompt_used": scenario['prompt']
        }
        for scenario in INSPECTION_SCENARIOS
    ]

    metadata_path = Path("sample_data") / "iphone_photo_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(photo_metadata, f, indent=2)

    print(f"✅ Created photo metadata: {metadata_path}")


def main():
    print("=" * 80)
    print("GENERATING IPHONE 16 STYLE HOME INSPECTION PHOTOS")
    print("=" * 80)
    print(f"\nUsing GPT-image-1 API to generate {len(INSPECTION_SCENARIOS)} iPhone-style images")
    print(f"   Model: gpt-image-1 (OpenAI's newest, March 2025)")
    print(f"   Cost: $0.015 per 1024x1024 image (75% cheaper than DALL-E 3)")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"\nIPhone 16 characteristics:")
    print(f"  - Natural smartphone perspective and angles")
    print(f"  - Good dynamic range (HDR-like)")
    print(f"  - Slightly wide angle lens")
    print(f"  - Sharp detail and natural colors")
    print(f"  - Hand-held casual photography style")

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

        # Group by category
        from collections import defaultdict
        by_category = defaultdict(list)
        for scenario in INSPECTION_SCENARIOS:
            by_category[scenario['issue_type']].append(scenario['filename'])

        print(f"\n📊 Photos by category:")
        for category, files in sorted(by_category.items()):
            print(f"   {category.upper()}: {len(files)} photos")

        total_size = sum(os.path.getsize(p) for p in generated_photos) / 1024 / 1024
        print(f"\n💾 Total size: {total_size:.1f} MB")

        # Create metadata files
        create_photo_metadata()

        print("\n💰 Estimated Cost:")
        cost_per_image = 0.015  # GPT-image-1: 1024x1024 = $0.015 (75% cheaper than DALL-E 3)
        total_cost = len(generated_photos) * cost_per_image
        print(f"   GPT-image-1 (1024x1024): ${cost_per_image} per image")
        print(f"   Total: ${total_cost:.2f}")
        print(f"   Savings vs DALL-E 3: ${(0.040 - 0.015) * len(generated_photos):.2f} (75% reduction)")

        print("\n🎯 Next Steps:")
        print("   1. Review the generated photos in: sample_data/iphone_photos/")
        print("   2. Update test runner for expanded photo set")
        print("   3. Run POC test with iPhone photos")
        print("   4. Commit photos to repository for testing")

    else:
        print("\n❌ No photos were generated successfully")
        print("   Check your OpenAI API key and billing status")


if __name__ == "__main__":
    main()
