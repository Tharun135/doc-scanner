"""
Solution-Focused PDF Documentation Generator for Writing Rules
This creates PDFs containing solutions for each writing issue that can be uploaded to the database
"""

import os
import sys
import re
import ast
import importlib.util
from pathlib import Path
from datetime import datetime

# PDF generation libraries with proper error handling
PDF_AVAILABLE = False
SimpleDocTemplate = None
Paragraph = None
Spacer = None
Table = None
TableStyle = None
PageBreak = None
getSampleStyleSheet = None
ParagraphStyle = None
inch = None
colors = None
TA_CENTER = None
TA_LEFT = None
TA_JUSTIFY = None
A4 = None

def import_pdf_libraries():
    """Import PDF libraries and set global variables"""
    global PDF_AVAILABLE, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    global getSampleStyleSheet, ParagraphStyle, inch, colors, TA_CENTER, TA_LEFT, TA_JUSTIFY, A4
    
    try:
        from reportlab.lib.pagesizes import A4 as _A4
        from reportlab.platypus import SimpleDocTemplate as _SimpleDocTemplate, Paragraph as _Paragraph, Spacer as _Spacer, Table as _Table, TableStyle as _TableStyle, PageBreak as _PageBreak
        from reportlab.lib.styles import getSampleStyleSheet as _getSampleStyleSheet, ParagraphStyle as _ParagraphStyle
        from reportlab.lib.units import inch as _inch
        from reportlab.lib import colors as _colors
        from reportlab.lib.enums import TA_CENTER as _TA_CENTER, TA_LEFT as _TA_LEFT, TA_JUSTIFY as _TA_JUSTIFY
        
        # Set global variables
        SimpleDocTemplate = _SimpleDocTemplate
        Paragraph = _Paragraph
        Spacer = _Spacer
        Table = _Table
        TableStyle = _TableStyle
        PageBreak = _PageBreak
        getSampleStyleSheet = _getSampleStyleSheet
        ParagraphStyle = _ParagraphStyle
        inch = _inch
        colors = _colors
        TA_CENTER = _TA_CENTER
        TA_LEFT = _TA_LEFT
        TA_JUSTIFY = _TA_JUSTIFY
        A4 = _A4
        PDF_AVAILABLE = True
        return True
    except ImportError:
        return False

# Try to import PDF libraries initially
import_pdf_libraries()

def get_rule_solutions(rule_name):
    """Get comprehensive solutions for each writing rule"""
    solutions = {
        'consistency_rules': {
            'issue_types': [
                'Inconsistent step numbering',
                'Mixed heading formats',
                'Inconsistent spacing',
                'Mixed bullet point styles',
                'Inconsistent terminology'
            ],
            'solutions': [
                {
                    'problem': 'Inconsistent Step Numbering',
                    'description': 'Document has mixed step numbering formats (1., 2), 3., etc.)',
                    'solution': 'Use consistent numbering format throughout the document',
                    'before_example': '1. First step\n2) Second step\n3. Third step',
                    'after_example': '1. First step\n2. Second step\n3. Third step',
                    'best_practice': 'Always use the same format: "1.", "2.", "3." with periods and spaces',
                    'why_important': 'Consistent numbering improves readability and maintains professional appearance'
                },
                {
                    'problem': 'Mixed Heading Formats',
                    'description': 'Headers use different formatting styles (# vs ## vs bold text)',
                    'solution': 'Standardize heading hierarchy using consistent markdown or formatting',
                    'before_example': '# Main Title\n**Subtitle**\n### Another Section',
                    'after_example': '# Main Title\n## Subtitle\n### Subsection',
                    'best_practice': 'Use hierarchical heading structure: # for main, ## for sections, ### for subsections',
                    'why_important': 'Consistent heading structure aids navigation and document scanning'
                },
                {
                    'problem': 'Inconsistent Terminology',
                    'description': 'Same concept referred to with different terms throughout document',
                    'solution': 'Choose one term and use it consistently throughout the document',
                    'before_example': 'Click the button... Press the key... Select the option',
                    'after_example': 'Click the button... Click the key... Click the option',
                    'best_practice': 'Create a terminology glossary and stick to preferred terms',
                    'why_important': 'Consistent terminology reduces confusion and improves clarity'
                }
            ]
        },
        'passive_voice': {
            'issue_types': [
                'Passive voice construction',
                'Weak passive sentences',
                'Unnecessary passive voice'
            ],
            'solutions': [
                {
                    'problem': 'Passive Voice Construction',
                    'description': 'Sentence uses passive voice instead of active voice',
                    'solution': 'Convert to active voice by making the doer the subject',
                    'before_example': 'The file was created by the system.',
                    'after_example': 'The system created the file.',
                    'best_practice': 'Use active voice for clarity: Subject + Verb + Object',
                    'why_important': 'Active voice is more direct, clear, and engaging for readers'
                },
                {
                    'problem': 'Weak Passive Sentences',
                    'description': 'Passive voice makes the sentence vague about who performs the action',
                    'solution': 'Specify who performs the action and use active voice',
                    'before_example': 'Errors were found in the code.',
                    'after_example': 'The testing team found errors in the code.',
                    'best_practice': 'Always specify who or what performs the action',
                    'why_important': 'Clear responsibility assignment improves accountability and understanding'
                },
                {
                    'problem': 'Unnecessary Passive Voice',
                    'description': 'Passive voice used when active voice would be clearer',
                    'solution': 'Replace with active voice for more direct communication',
                    'before_example': 'The installation steps are demonstrated in a video.',
                    'after_example': 'This video demonstrates the installation steps.',
                    'best_practice': 'Default to active voice unless passive is specifically needed',
                    'why_important': 'Active voice creates stronger, more engaging technical writing'
                }
            ]
        },
        'long_sentence': {
            'issue_types': [
                'Sentences over 25 words',
                'Complex compound sentences',
                'Run-on sentences'
            ],
            'solutions': [
                {
                    'problem': 'Sentences Over 25 Words',
                    'description': 'Sentence contains too many words, making it hard to follow',
                    'solution': 'Break into shorter, focused sentences',
                    'before_example': 'To configure the system, you must first access the control panel, then navigate to the settings menu, select the appropriate options, and finally save your changes before exiting.',
                    'after_example': 'To configure the system, first access the control panel. Navigate to the settings menu and select the appropriate options. Finally, save your changes before exiting.',
                    'best_practice': 'Keep sentences under 20 words for technical documentation',
                    'why_important': 'Shorter sentences improve comprehension and reduce cognitive load'
                },
                {
                    'problem': 'Complex Compound Sentences',
                    'description': 'Multiple ideas joined with conjunctions create confusing sentences',
                    'solution': 'Separate complex ideas into individual sentences',
                    'before_example': 'Click the Start button and wait for the system to initialize, but if errors occur, check the log files and restart the process.',
                    'after_example': 'Click the Start button and wait for the system to initialize. If errors occur, check the log files. Then restart the process.',
                    'best_practice': 'One main idea per sentence for technical instructions',
                    'why_important': 'Clear separation of ideas prevents confusion in procedures'
                }
            ]
        },
        'style_rules': {
            'issue_types': [
                'Inconsistent style',
                'Informal language',
                'Poor formatting'
            ],
            'solutions': [
                {
                    'problem': 'Inconsistent Style',
                    'description': 'Document mixes formal and informal writing styles',
                    'solution': 'Maintain consistent professional tone throughout',
                    'before_example': "You'll need to setup the config. It's pretty easy to do.",
                    'after_example': 'You need to set up the configuration. This process is straightforward.',
                    'best_practice': 'Use professional, consistent tone in technical documentation',
                    'why_important': 'Consistent style maintains credibility and professionalism'
                },
                {
                    'problem': 'Exclamation Mark Overuse',
                    'description': 'Multiple exclamation marks used inappropriately',
                    'solution': 'Use periods for statements, reserve exclamation marks for warnings',
                    'before_example': 'The system is working perfectly!!',
                    'after_example': 'The system is working correctly.',
                    'best_practice': 'Use exclamation marks only for warnings or critical alerts',
                    'why_important': 'Professional documentation uses restrained punctuation'
                }
            ]
        },
        'grammar_rules': {
            'issue_types': [
                'Subject-verb disagreement',
                'Incorrect tense usage',
                'Article errors'
            ],
            'solutions': [
                {
                    'problem': 'Subject-Verb Disagreement',
                    'description': 'Subject and verb do not agree in number',
                    'solution': 'Match verb form with subject number (singular/plural)',
                    'before_example': 'The files is corrupted.',
                    'after_example': 'The files are corrupted.',
                    'best_practice': 'Singular subjects take singular verbs; plural subjects take plural verbs',
                    'why_important': 'Proper grammar maintains professional credibility'
                },
                {
                    'problem': 'Incorrect Tense Usage',
                    'description': 'Mixed or inappropriate verb tenses',
                    'solution': 'Use consistent, appropriate tense throughout',
                    'before_example': 'The system will process data and had generated reports.',
                    'after_example': 'The system will process data and generate reports.',
                    'best_practice': 'Use present tense for current procedures, future for planned actions',
                    'why_important': 'Consistent tense usage improves clarity and understanding'
                }
            ]
        },
        'terminology_rules': {
            'issue_types': [
                'Inconsistent technical terms',
                'Non-standard terminology',
                'Ambiguous terms'
            ],
            'solutions': [
                {
                    'problem': 'Inconsistent Technical Terms',
                    'description': 'Same technical concept referred to with different terms',
                    'solution': 'Standardize on one preferred technical term',
                    'before_example': 'Open the dialog box... Close the popup window... Exit the modal',
                    'after_example': 'Open the dialog box... Close the dialog box... Exit the dialog box',
                    'best_practice': 'Create and follow a technical terminology glossary',
                    'why_important': 'Consistent terminology prevents confusion in technical procedures'
                },
                {
                    'problem': 'Non-Standard Terminology',
                    'description': 'Uses non-standard or deprecated technical terms',
                    'solution': 'Replace with current, industry-standard terminology',
                    'before_example': 'Right-click on the icon to access the popup menu',
                    'after_example': 'Right-click on the icon to access the context menu',
                    'best_practice': 'Use current industry-standard terms for UI elements',
                    'why_important': 'Standard terminology aligns with user expectations and training'
                }
            ]
        },
        'vague_terms': {
            'issue_types': [
                'Vague quantifiers',
                'Imprecise language',
                'Ambiguous instructions'
            ],
            'solutions': [
                {
                    'problem': 'Vague Quantifiers',
                    'description': 'Uses imprecise terms like "some," "many," "few"',
                    'solution': 'Replace with specific quantities or clear descriptions',
                    'before_example': 'Wait a few seconds for the process to complete.',
                    'after_example': 'Wait 5-10 seconds for the process to complete.',
                    'best_practice': 'Use specific numbers, timeframes, or measurable criteria',
                    'why_important': 'Precise language sets clear expectations and reduces confusion'
                },
                {
                    'problem': 'Ambiguous Instructions',
                    'description': 'Instructions that can be interpreted multiple ways',
                    'solution': 'Provide specific, step-by-step instructions',
                    'before_example': 'Configure the settings appropriately.',
                    'after_example': 'Set the timeout to 30 seconds and enable automatic retry.',
                    'best_practice': 'Specify exact actions, values, and parameters',
                    'why_important': 'Clear instructions prevent errors and support successful task completion'
                }
            ]
        }
    }
    
    return solutions.get(rule_name, {
        'issue_types': ['General writing issues'],
        'solutions': [{
            'problem': 'General Writing Issue',
            'solution': 'Follow writing best practices for technical documentation',
            'best_practice': 'Use clear, concise, and professional language',
            'why_important': 'Good writing improves user experience and reduces support requests'
        }]
    })

def create_solution_pdf(rule_name, output_dir):
    """Create a solution-focused PDF for a writing rule"""
    if not PDF_AVAILABLE:
        return False
    
    solutions_data = get_rule_solutions(rule_name)
    filename = f"{rule_name}_solutions.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4, 
                          rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=72)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    solution_heading_style = ParagraphStyle(
        'SolutionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkgreen,
        borderWidth=1,
        borderColor=colors.darkgreen,
        borderPadding=10
    )
    
    problem_style = ParagraphStyle(
        'ProblemStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.darkred,
        fontName='Helvetica-Bold'
    )
    
    # Story container
    story = []
    
    # Title page
    rule_display_name = rule_name.replace('_', ' ').title()
    story.append(Paragraph(f"{rule_display_name}", title_style))
    story.append(Paragraph("Writing Solutions Guide", styles['Heading2']))
    story.append(Spacer(1, 30))
    
    # Introduction
    story.append(Paragraph("How to Use This Guide", styles['Heading3']))
    story.append(Paragraph(
        "This guide provides specific solutions for writing issues detected by the DocScanner AI system. "
        "When the AI flags a writing issue, refer to this guide for step-by-step solutions.", 
        styles['Normal']
    ))
    story.append(Spacer(1, 20))
    
    # Issue types overview
    if solutions_data.get('issue_types'):
        story.append(Paragraph("Common Issues Detected", styles['Heading3']))
        for issue_type in solutions_data['issue_types']:
            story.append(Paragraph(f"• {issue_type}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Solutions
    story.append(Paragraph("Solutions", styles['Heading2']))
    
    for i, solution in enumerate(solutions_data.get('solutions', []), 1):
        # Solution number and problem
        story.append(Paragraph(f"Solution {i}: {solution['problem']}", solution_heading_style))
        
        # Problem description
        if solution.get('description'):
            story.append(Paragraph(f"<b>Issue:</b> {solution['description']}", problem_style))
            story.append(Spacer(1, 10))
        
        # Solution
        story.append(Paragraph(f"<b>Solution:</b> {solution['solution']}", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Before/After examples
        if solution.get('before_example') and solution.get('after_example'):
            story.append(Paragraph("<b>Before (Incorrect):</b>", styles['Normal']))
            story.append(Paragraph(f"<font name='Courier' color='red'>{solution['before_example']}</font>", styles['Code']))
            story.append(Spacer(1, 5))
            
            story.append(Paragraph("<b>After (Correct):</b>", styles['Normal']))
            story.append(Paragraph(f"<font name='Courier' color='green'>{solution['after_example']}</font>", styles['Code']))
            story.append(Spacer(1, 10))
        
        # Best practice
        if solution.get('best_practice'):
            story.append(Paragraph(f"<b>Best Practice:</b> {solution['best_practice']}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Why it's important
        if solution.get('why_important'):
            story.append(Paragraph(f"<b>Why This Matters:</b> {solution['why_important']}", styles['BodyText']))
        
        story.append(Spacer(1, 25))
    
    # Quick reference section
    story.append(PageBreak())
    story.append(Paragraph("Quick Reference", styles['Heading2']))
    story.append(Paragraph("Use this section for quick lookup when fixing issues:", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Create quick reference table
    quick_ref_data = [['Problem', 'Quick Fix']]
    for solution in solutions_data.get('solutions', []):
        problem = solution['problem']
        quick_fix = solution['solution']
        if len(quick_fix) > 80:
            quick_fix = quick_fix[:77] + "..."
        quick_ref_data.append([problem, quick_fix])
    
    if len(quick_ref_data) > 1:
        table = Table(quick_ref_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(table)
    
    # Footer
    story.append(Spacer(1, 50))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph("DocScanner AI - Writing Quality Enhancement System", styles['Normal']))
    story.append(Paragraph("Upload this PDF to your knowledge base for AI-powered solution lookup", styles['BodyText']))
    
    # Build PDF
    try:
        doc.build(story)
        return True
    except Exception as e:
        print(f"❌ Failed to create solution PDF for {rule_name}: {e}")
        return False

def create_master_solutions_index(all_rules, output_dir):
    """Create a master index of all solution PDFs"""
    if not PDF_AVAILABLE:
        return False
    
    filepath = os.path.join(output_dir, "00_Master_Solutions_Index.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Title'], 
                                fontSize=24, alignment=TA_CENTER)
    story.append(Paragraph("DocScanner AI Writing Solutions", title_style))
    story.append(Paragraph("Complete Solution Database", styles['Heading2']))
    story.append(Spacer(1, 30))
    
    # Introduction
    story.append(Paragraph("About This Solution Database", styles['Heading3']))
    story.append(Paragraph(
        "This collection contains solution-focused guides for all writing rules implemented in DocScanner AI. "
        "Each PDF provides specific solutions for writing issues that can be uploaded to your knowledge base "
        "for AI-powered solution lookup and recommendations.", 
        styles['Normal']
    ))
    story.append(Spacer(1, 20))
    
    # How to use
    story.append(Paragraph("How to Use", styles['Heading3']))
    story.append(Paragraph("1. Upload all solution PDFs to your DocScanner AI knowledge base", styles['Normal']))
    story.append(Paragraph("2. When the AI detects writing issues, it will search these solutions", styles['Normal']))
    story.append(Paragraph("3. The AI will provide context-aware solutions from your uploaded documentation", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Summary table
    data = [['Rule Category', 'Solution PDF', 'Primary Issues Addressed']]
    for rule in all_rules:
        rule_display = rule.replace('_', ' ').title()
        solutions_data = get_rule_solutions(rule)
        primary_issues = ', '.join(solutions_data.get('issue_types', ['General'])[:2])
        if len(primary_issues) > 50:
            primary_issues = primary_issues[:47] + "..."
        data.append([rule_display, f"{rule}_solutions.pdf", primary_issues])
    
    table = Table(data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Statistics
    story.append(Paragraph("Database Statistics", styles['Heading3']))
    story.append(Paragraph(f"Total Solution Guides: {len(all_rules)}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Upload instructions
    story.append(Paragraph("Upload Instructions", styles['Heading3']))
    story.append(Paragraph(
        "To enable AI-powered solution lookup, upload all PDF files to your DocScanner AI knowledge base. "
        "The AI will then reference these solutions when providing writing improvement suggestions.", 
        styles['BodyText']
    ))
    
    doc.build(story)
    return True

def generate_solution_documentation():
    """Main function to generate solution-focused PDF documentation"""
    print("📚 DocScanner AI Solution Documentation Generator")
    print("=" * 70)
    print("🎯 Creating solution-focused PDFs for AI knowledge base upload")
    
    # Create output directory
    output_dir = "rule_solutions_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    
    # Define the rules we want to create solutions for
    rules_to_document = [
        'consistency_rules',
        'passive_voice', 
        'long_sentence',
        'style_rules',
        'grammar_rules',
        'terminology_rules',
        'vague_terms'
    ]
    
    print(f"📋 Creating solution guides for {len(rules_to_document)} rule categories")
    
    # Generate solution PDFs
    successful_pdfs = 0
    
    for rule_name in rules_to_document:
        print(f"📖 Creating solution guide for {rule_name}...")
        if create_solution_pdf(rule_name, output_dir):
            successful_pdfs += 1
            print(f"   ✅ Solution PDF created successfully")
        else:
            print(f"   ❌ Solution PDF creation failed")
    
    # Create master index
    print("📚 Creating master solutions index...")
    if create_master_solutions_index(rules_to_document, output_dir):
        print("   ✅ Master index created")
    else:
        print("   ❌ Master index creation failed")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SOLUTION DOCUMENTATION GENERATION COMPLETE")
    print(f"✅ Successfully created {successful_pdfs}/{len(rules_to_document)} solution PDFs")
    print(f"📁 Output location: {os.path.abspath(output_dir)}")
    print("\n📚 Generated Solution Files:")
    
    if os.path.exists(output_dir):
        for file in sorted(os.listdir(output_dir)):
            if file.endswith('.pdf'):
                print(f"   📄 {file}")
    
    print("\n🎯 Next Steps:")
    print("1. 📤 Upload all PDF files to your DocScanner AI knowledge base")
    print("2. 🔍 The AI will search these solutions when writing issues are detected")
    print("3. 💡 Users will receive specific, actionable solutions from your documentation")
    
    return successful_pdfs > 0

if __name__ == "__main__":
    success = generate_solution_documentation()
    if success:
        print("\n🎉 Solution documentation generation completed successfully!")
        print("📚 Your PDFs contain actionable solutions ready for knowledge base upload!")
    else:
        print("\n❌ Solution documentation generation failed!")