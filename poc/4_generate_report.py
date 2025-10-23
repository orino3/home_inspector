#!/usr/bin/env python3
"""
POC Script 4: Report Generation
Generates professional home inspection report from correlated data
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def load_correlations(correlations_path: str) -> List[Dict]:
    """Load correlation results"""
    with open(correlations_path, 'r') as f:
        return json.load(f)


def generate_executive_summary(all_issues: List[Dict], property_info: Dict) -> str:
    """
    Generate executive summary using GPT-5

    Args:
        all_issues: All detected issues
        property_info: Property information

    Returns:
        Executive summary text
    """

    print("📝 Generating executive summary...")

    # Prepare issue summary
    issues_by_severity = {}
    for issue in all_issues:
        severity = issue.get('severity', 'unknown')
        issues_by_severity.setdefault(severity, []).append(issue['title'])

    prompt = f"""Generate a professional executive summary for a home inspection report.

**PROPERTY:**
{json.dumps(property_info, indent=2)}

**ISSUES FOUND:**
{json.dumps(issues_by_severity, indent=2)}

**Total Issues:** {len(all_issues)}

**REQUIREMENTS:**
1. Write 2-3 paragraphs
2. Start with overall property condition
3. Highlight major concerns
4. Be professional and objective
5. Use home inspection industry terminology
6. End with general recommendations

Do NOT use markdown formatting. Return plain text.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.5
    )

    summary = response.choices[0].message.content.strip()

    print(f"   ✅ Summary generated ({len(summary)} chars)")

    return summary


def organize_issues_by_category(all_issues: List[Dict]) -> Dict[str, List[Dict]]:
    """Organize issues by category for report sections"""

    categories = {}

    for issue in all_issues:
        category = issue.get('category', 'other')
        categories.setdefault(category, []).append(issue)

    return categories


def generate_section_content(category: str, issues: List[Dict]) -> str:
    """Generate content for a report section"""

    if not issues:
        return f"No significant {category} issues were observed during the inspection."

    content = []

    for i, issue in enumerate(issues, 1):
        severity_emoji = {
            'safety_hazard': '🚨',
            'major': '⚠️',
            'moderate': '⚠️',
            'minor': '📋',
            'informational': 'ℹ️'
        }.get(issue.get('severity', 'minor'), '📋')

        content.append(f"{severity_emoji} **{issue.get('title', 'Untitled Issue')}**")
        content.append(f"Location: {issue.get('location', 'Not specified')}")
        content.append(f"Severity: {issue.get('severity', 'Not specified').replace('_', ' ').title()}")
        content.append(f"\nDescription: {issue.get('description', 'No description provided')}")

        if issue.get('recommendations'):
            content.append(f"\nRecommendation: {issue['recommendations']}")

        if issue.get('inspector_notes'):
            content.append(f"\nInspector Notes: {issue['inspector_notes']}")

        content.append("\n" + "-" * 80 + "\n")

    return "\n".join(content)


def generate_full_report(
    correlations: List[Dict],
    property_info: Dict,
    output_dir: str = "outputs/reports"
) -> Dict:
    """
    Generate complete inspection report

    Args:
        correlations: All correlation results
        property_info: Property information
        output_dir: Output directory

    Returns:
        Complete report data
    """

    print("\n📄 Generating full inspection report...\n")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Extract all issues
    all_issues = []
    for correlation in correlations:
        correlated_issues = correlation.get('correlation', {}).get('correlated_issues', [])
        for issue in correlated_issues:
            # Add photo reference
            issue['photo_reference'] = Path(correlation['photo_path']).name
            issue['photo_timestamp'] = correlation.get('photo_timestamp')
            all_issues.append(issue)

    # Generate executive summary
    executive_summary = generate_executive_summary(all_issues, property_info)

    # Organize by category
    issues_by_category = organize_issues_by_category(all_issues)

    # Calculate overall condition rating
    severity_weights = {
        'safety_hazard': 5,
        'major': 4,
        'moderate': 3,
        'minor': 2,
        'informational': 1
    }

    total_severity_score = sum(
        severity_weights.get(issue.get('severity', 'minor'), 2)
        for issue in all_issues
    )

    # Overall rating (1-5, where 5 is excellent)
    if total_severity_score == 0:
        overall_rating = 5
    elif total_severity_score < 10:
        overall_rating = 4
    elif total_severity_score < 30:
        overall_rating = 3
    elif total_severity_score < 60:
        overall_rating = 2
    else:
        overall_rating = 1

    overall_condition_text = {
        5: "Excellent",
        4: "Good",
        3: "Fair",
        2: "Poor",
        1: "Needs Immediate Attention"
    }[overall_rating]

    # Create report structure
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "inspection_date": property_info.get('inspection_date', datetime.now().strftime('%Y-%m-%d')),
            "generator": "Home Inspector AI - POC v0.1"
        },
        "property_info": property_info,
        "executive_summary": executive_summary,
        "overall_condition": {
            "rating": overall_rating,
            "text": overall_condition_text,
            "severity_score": total_severity_score
        },
        "statistics": {
            "total_issues": len(all_issues),
            "by_severity": {
                "safety_hazard": sum(1 for i in all_issues if i.get('severity') == 'safety_hazard'),
                "major": sum(1 for i in all_issues if i.get('severity') == 'major'),
                "moderate": sum(1 for i in all_issues if i.get('severity') == 'moderate'),
                "minor": sum(1 for i in all_issues if i.get('severity') == 'minor'),
                "informational": sum(1 for i in all_issues if i.get('severity') == 'informational')
            },
            "by_category": {cat: len(issues) for cat, issues in issues_by_category.items()}
        },
        "sections": {},
        "all_issues": all_issues
    }

    # Generate sections
    category_names = {
        'structural': 'Structural',
        'foundation': 'Foundation',
        'roof': 'Roof',
        'exterior': 'Exterior',
        'electrical': 'Electrical',
        'plumbing': 'Plumbing',
        'hvac': 'HVAC',
        'interior': 'Interior',
        'appliances': 'Appliances',
        'safety': 'Safety',
        'other': 'Other Observations'
    }

    for category, issues in issues_by_category.items():
        section_name = category_names.get(category, category.title())
        print(f"   📝 Section: {section_name} ({len(issues)} issues)")

        report['sections'][category] = {
            "title": section_name,
            "issue_count": len(issues),
            "content": generate_section_content(category, issues),
            "issues": issues
        }

    # Save report JSON
    json_output_path = Path(output_dir) / "inspection_report.json"
    with open(json_output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Report saved to: {json_output_path}")

    # Generate human-readable text report
    text_report = generate_text_report(report)
    text_output_path = Path(output_dir) / "inspection_report.txt"
    with open(text_output_path, 'w') as f:
        f.write(text_report)

    print(f"✅ Text report saved to: {text_output_path}")

    return report


def generate_text_report(report: Dict) -> str:
    """Generate human-readable text report"""

    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("HOME INSPECTION REPORT")
    lines.append("=" * 80)
    lines.append("")

    # Property info
    prop_info = report['property_info']
    lines.append(f"Property Address: {prop_info.get('address', 'N/A')}")
    lines.append(f"Inspection Date: {report['metadata']['inspection_date']}")
    lines.append(f"Report Generated: {report['metadata']['generated_at']}")
    lines.append("")

    # Overall condition
    lines.append("OVERALL CONDITION")
    lines.append("-" * 80)
    overall = report['overall_condition']
    lines.append(f"Rating: {overall['text']} ({overall['rating']}/5)")
    lines.append("")

    # Executive summary
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 80)
    lines.append(report['executive_summary'])
    lines.append("")

    # Statistics
    lines.append("INSPECTION SUMMARY")
    lines.append("-" * 80)
    stats = report['statistics']
    lines.append(f"Total Issues Found: {stats['total_issues']}")
    lines.append("")
    lines.append("By Severity:")
    for severity, count in stats['by_severity'].items():
        if count > 0:
            lines.append(f"  - {severity.replace('_', ' ').title()}: {count}")
    lines.append("")
    lines.append("By Category:")
    for category, count in stats['by_category'].items():
        if count > 0:
            lines.append(f"  - {category.title()}: {count}")
    lines.append("")

    # Detailed sections
    lines.append("=" * 80)
    lines.append("DETAILED FINDINGS")
    lines.append("=" * 80)
    lines.append("")

    for section_data in report['sections'].values():
        lines.append(f"\n{section_data['title'].upper()}")
        lines.append("-" * 80)
        lines.append(section_data['content'])

    return "\n".join(lines)


if __name__ == "__main__":
    # Test report generation
    correlations_file = "outputs/correlations/all_correlations.json"

    if os.path.exists(correlations_file):
        correlations = load_correlations(correlations_file)

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

        report = generate_full_report(correlations, property_info)

        print("\n📊 FINAL REPORT STATISTICS:")
        print(f"   Total Issues: {report['statistics']['total_issues']}")
        print(f"   Overall Condition: {report['overall_condition']['text']}")
        print(f"   Sections: {len(report['sections'])}")

    else:
        print("⚠️  Correlations file not found")
        print("📝 Run script 3 first:")
        print("   python poc/3_correlate.py")
