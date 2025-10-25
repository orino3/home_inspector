#!/usr/bin/env python3
"""
POC Script 5: PDF Report Generation
Generates professional PDF reports with embedded photos
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def generate_pdf_report(
    report_json_path: str,
    correlations_path: str,
    property_info: Dict,
    output_path: str = None
) -> str:
    """
    Generate professional PDF report with embedded photos

    Args:
        report_json_path: Path to JSON report
        correlations_path: Path to correlations (for photo references)
        property_info: Property information dict
        output_path: Output PDF path (optional)

    Returns:
        Path to generated PDF
    """

    # Load report data
    with open(report_json_path, 'r') as f:
        report = json.load(f)

    # Load correlations (for photo access)
    with open(correlations_path, 'r') as f:
        correlations = json.load(f)

    # Default output path
    if not output_path:
        output_dir = Path(report_json_path).parent
        output_path = output_dir / "inspection_report.pdf"

    # Create PDF
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Container for PDF elements
    story = []

    # Styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=10
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )

    # Title
    story.append(Paragraph("HOME INSPECTION REPORT", title_style))
    story.append(Spacer(1, 0.3*inch))

    # Property Information Table
    property_data = [
        ['Property Address:', property_info.get('address', 'N/A')],
        ['Property Type:', property_info.get('property_type', 'N/A')],
        ['Year Built:', str(property_info.get('year_built', 'N/A'))],
        ['Square Footage:', property_info.get('square_footage', 'N/A')],
        ['Inspection Date:', property_info.get('inspection_date', 'N/A')],
        ['Inspector:', property_info.get('inspector_name', 'N/A')],
        ['Customer:', property_info.get('customer_name', 'N/A')],
    ]

    property_table = Table(property_data, colWidths=[2*inch, 4.5*inch])
    property_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(property_table)
    story.append(Spacer(1, 0.4*inch))

    # Overall Condition
    story.append(Paragraph("OVERALL CONDITION", heading1_style))
    overall = report.get('overall_condition', {})
    rating_text = f"{overall.get('text', 'N/A')} ({overall.get('rating', 0)}/5)"
    story.append(Paragraph(f"<b>Rating:</b> {rating_text}", normal_style))
    story.append(Spacer(1, 0.2*inch))

    # Executive Summary
    story.append(Paragraph("EXECUTIVE SUMMARY", heading1_style))
    summary = report.get('executive_summary', 'No summary available.')
    story.append(Paragraph(summary, normal_style))
    story.append(Spacer(1, 0.3*inch))

    # Statistics
    story.append(Paragraph("INSPECTION SUMMARY", heading1_style))
    stats = report.get('statistics', {})

    stats_text = f"<b>Total Issues Found:</b> {stats.get('total_issues', 0)}<br/><br/>"

    # By Severity
    by_severity = stats.get('by_severity', {})
    if any(by_severity.values()):
        stats_text += "<b>By Severity:</b><br/>"
        severity_icons = {
            'safety_hazard': '🚨',
            'major': '⚠️',
            'moderate': '⚠️',
            'minor': '📋',
            'informational': 'ℹ️'
        }
        for severity, count in by_severity.items():
            if count > 0:
                icon = severity_icons.get(severity, '•')
                severity_name = severity.replace('_', ' ').title()
                stats_text += f"&nbsp;&nbsp;• {severity_name}: {count}<br/>"
        stats_text += "<br/>"

    # By Category
    by_category = stats.get('by_category', {})
    if any(by_category.values()):
        stats_text += "<b>By Category:</b><br/>"
        for category, count in by_category.items():
            if count > 0:
                category_name = category.title()
                stats_text += f"&nbsp;&nbsp;• {category_name}: {count}<br/>"

    story.append(Paragraph(stats_text, normal_style))
    story.append(Spacer(1, 0.3*inch))

    # Page break before detailed findings
    story.append(PageBreak())

    # Detailed Findings
    story.append(Paragraph("DETAILED FINDINGS", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    # Group issues by category
    sections = report.get('sections', {})

    for category, section_data in sections.items():
        # Section heading
        section_title = section_data.get('title', category.title())
        story.append(Paragraph(section_title.upper(), heading2_style))
        story.append(Spacer(1, 0.1*inch))

        # Issues in this section
        issues = section_data.get('issues', [])

        for issue in issues:
            # Issue title with severity icon
            severity_icons = {
                'safety_hazard': '🚨',
                'major': '⚠️',
                'moderate': '⚠️',
                'minor': '📋',
                'informational': 'ℹ️'
            }
            icon = severity_icons.get(issue.get('severity', 'minor'), '•')
            title = f"<b>{icon} {issue.get('title', 'Untitled Issue')}</b>"
            story.append(Paragraph(title, normal_style))
            story.append(Spacer(1, 0.05*inch))

            # Issue details
            details = f"<b>Location:</b> {issue.get('location', 'N/A')}<br/>"
            details += f"<b>Severity:</b> {issue.get('severity', 'N/A').replace('_', ' ').title()}<br/><br/>"
            details += f"<b>Description:</b><br/>{issue.get('description', 'No description available.')}<br/><br/>"
            details += f"<b>Recommendation:</b><br/>{issue.get('recommendations', 'No recommendations.')}<br/>"

            if issue.get('inspector_notes'):
                details += f"<br/><b>Inspector Notes:</b><br/>{issue['inspector_notes']}<br/>"

            story.append(Paragraph(details, normal_style))
            story.append(Spacer(1, 0.1*inch))

            # Try to add photo
            photo_ref = issue.get('photo_reference')
            if photo_ref:
                # Find the photo in correlations
                for corr in correlations:
                    if Path(corr['photo_path']).name == photo_ref:
                        photo_path = corr['photo_path']
                        if os.path.exists(photo_path):
                            try:
                                # Add photo with caption
                                img = Image(photo_path, width=4*inch, height=3*inch)
                                story.append(img)
                                caption = f"Photo: {photo_ref} (Timestamp: {issue.get('photo_timestamp', 'N/A')}s)"
                                story.append(Paragraph(f"<i>{caption}</i>", normal_style))
                                story.append(Spacer(1, 0.1*inch))
                            except Exception as e:
                                print(f"⚠️  Could not embed photo {photo_ref}: {e}")
                        break

            # Divider between issues
            story.append(Spacer(1, 0.2*inch))

    # Build PDF
    doc.build(story)

    return str(output_path)


if __name__ == "__main__":
    # Test PDF generation
    import sys

    report_json = "outputs/reports/inspection_report.json"
    correlations = "outputs/correlations/synthetic_test_correlations.json"
    property_info_file = "sample_data/property_info.json"

    if os.path.exists(report_json) and os.path.exists(correlations) and os.path.exists(property_info_file):
        with open(property_info_file, 'r') as f:
            property_info = json.load(f)

        print("📄 Generating PDF report...")
        pdf_path = generate_pdf_report(report_json, correlations, property_info)
        print(f"✅ PDF generated: {pdf_path}")
        print(f"   File size: {os.path.getsize(pdf_path) / 1024:.1f} KB")
    else:
        print("❌ Missing required files. Run the POC test first:")
        print("   python run_synthetic_test.py")
