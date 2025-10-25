#!/usr/bin/env python3
"""
POC Script 2: Photo Analysis
Uses GPT-5 Vision to analyze inspection photos
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def encode_image(image_path: str) -> str:
    """Encode image to base64 for API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_photo(
    photo_path: str,
    photo_timestamp: float = None,
    output_dir: str = "outputs/analyses"
) -> Dict:
    """
    Analyze a single photo using GPT-5 Vision

    Args:
        photo_path: Path to photo file
        photo_timestamp: When photo was taken in audio timeline (seconds)
        output_dir: Directory to save analysis results

    Returns:
        Dict containing analysis results
    """

    print(f"🔍 Analyzing photo: {photo_path}")

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Encode image
    base64_image = encode_image(photo_path)

    # Create analysis prompt
    prompt = """You are an expert home inspector analyzing this photo.

Identify and describe:
1. **Location**: What room/area is this? (e.g., "Master Bedroom", "Roof - North Side", "Electrical Panel")
2. **Visible Elements**: What components/systems are visible?
3. **Issues Detected**: Any defects, damage, or concerns? Be specific.
4. **Severity**: For each issue - is it informational, minor, moderate, major, or safety hazard?
5. **Recommendations**: What actions should be taken?

Return your analysis in this JSON format:
{
  "location": "string",
  "visible_elements": ["element1", "element2"],
  "issues_detected": [
    {
      "title": "Short descriptive title",
      "description": "Detailed description",
      "category": "structural|electrical|plumbing|hvac|roof|exterior|interior|safety|other",
      "severity": "informational|minor|moderate|major|safety_hazard",
      "recommendation": "What should be done"
    }
  ],
  "overall_assessment": "Brief summary",
  "confidence": 0.0-1.0
}

Be professional and use proper home inspection terminology.
If no issues are visible, return empty issues_detected array.
"""

    # Call GPT-4o Vision (best for structured JSON output - 100% reliability)
    response = client.chat.completions.create(
        model="gpt-4o",  # Using GPT-4o - best for reliable structured outputs
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1500,
        temperature=0.3,  # Lower temperature for more consistent analysis
        response_format={"type": "json_object"}  # Ensure JSON response
    )

    # Parse response
    analysis_text = response.choices[0].message.content

    try:
        analysis = json.loads(analysis_text)
    except json.JSONDecodeError:
        print("⚠️  Failed to parse JSON response, using text")
        analysis = {"raw_response": analysis_text}

    # Add metadata
    result = {
        "photo_path": photo_path,
        "photo_timestamp": photo_timestamp,
        "analysis": analysis,
        "model_used": "gpt-4o",
        "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
    }

    # Save to JSON
    output_filename = Path(photo_path).stem + "_analysis.json"
    output_path = Path(output_dir) / output_filename

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✅ Analysis saved to: {output_path}")

    # Print summary
    if 'issues_detected' in analysis:
        num_issues = len(analysis['issues_detected'])
        print(f"📊 Issues found: {num_issues}")
        if num_issues > 0:
            for issue in analysis['issues_detected']:
                print(f"   - {issue.get('title', 'Untitled')} ({issue.get('severity', 'unknown')})")
    else:
        print(f"📊 Analysis: {analysis.get('overall_assessment', 'N/A')}")

    return result


def analyze_multiple_photos(photo_dir: str, photo_timestamps: Dict[str, float] = None) -> List[Dict]:
    """
    Analyze multiple photos in a directory

    Args:
        photo_dir: Directory containing photos
        photo_timestamps: Dict mapping photo filenames to timestamps

    Returns:
        List of analysis results
    """

    photo_dir = Path(photo_dir)
    photo_files = sorted(photo_dir.glob("*.jpg")) + sorted(photo_dir.glob("*.png"))

    if not photo_files:
        print(f"⚠️  No photos found in {photo_dir}")
        return []

    print(f"\n📸 Found {len(photo_files)} photos to analyze\n")

    results = []

    for i, photo_path in enumerate(photo_files, 1):
        print(f"\n[{i}/{len(photo_files)}]", end=" ")

        # Get timestamp if provided
        timestamp = None
        if photo_timestamps and photo_path.name in photo_timestamps:
            timestamp = photo_timestamps[photo_path.name]

        result = analyze_photo(str(photo_path), timestamp)
        results.append(result)

    print(f"\n✅ Analyzed {len(results)} photos")

    return results


if __name__ == "__main__":
    # Test with sample photos
    sample_photo_dir = "sample_data/photos"

    if os.path.exists(sample_photo_dir) and list(Path(sample_photo_dir).glob("*.jpg")):
        # Example timestamps (would come from photo metadata or manual tagging)
        timestamps = {
            "photo1.jpg": 45.0,
            "photo2.jpg": 120.5,
            "photo3.jpg": 185.2
        }

        results = analyze_multiple_photos(sample_photo_dir, timestamps)

        # Summary
        total_issues = sum(
            len(r['analysis'].get('issues_detected', []))
            for r in results
            if 'analysis' in r
        )
        print(f"\n📊 SUMMARY:")
        print(f"   Photos analyzed: {len(results)}")
        print(f"   Total issues detected: {total_issues}")

    else:
        print(f"⚠️  Sample photos not found in {sample_photo_dir}")
        print("📝 This script is ready. Add sample photos to test.")
        print("\nTo test manually:")
        print("  from poc.analyze_photos import analyze_photo")
        print("  result = analyze_photo('path/to/photo.jpg', timestamp=120.5)")
