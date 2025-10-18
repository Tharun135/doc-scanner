"""
PDF Documentation Generator for Writing Rules
This creates professional PDF documentation for each rule in the rules folder
"""

import os
import sys
import re
import ast
import importlib.util
from pathlib import Path
from datetime import datetime

# PDF generation libraries
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
        from reportlab.lib.pagesizes import letter, A4 as _A4
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

def install_pdf_dependencies():
    """Install required PDF generation libraries"""
    print("📦 Installing PDF generation dependencies...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        print("✅ ReportLab installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def extract_rule_info(rule_file_path):
    """Extract comprehensive information from a rule file"""
    rule_info = {
        'name': Path(rule_file_path).stem,
        'description': '',
        'purpose': '',
        'examples': [],
        'patterns': [],
        'functions': [],
        'imports': [],
        'checks': [],
        'file_path': rule_file_path
    }
    
    try:
        with open(rule_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to extract function definitions and docstrings
        try:
            tree = ast.parse(content)
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or '',
                        'args': [arg.arg for arg in node.args.args]
                    }
                    rule_info['functions'].append(func_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        rule_info['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        rule_info['imports'].append(f"{module}.{alias.name}")
        
        except SyntaxError:
            pass  # Continue even if AST parsing fails
        
        # Extract regex patterns
        regex_patterns = re.findall(r'r["\']([^"\']+)["\']', content)
        rule_info['patterns'] = regex_patterns
        
        # Extract comments that might describe the rule
        comments = re.findall(r'#\s*(.+)', content)
        rule_info['comments'] = comments[:10]  # First 10 comments
        
        # Look for specific check patterns
        if 'passive voice' in content.lower():
            rule_info['checks'].append('Passive Voice Detection')
        if 'long sentence' in content.lower():
            rule_info['checks'].append('Long Sentence Detection')
        if 'adverb' in content.lower():
            rule_info['checks'].append('Adverb Usage')
        if 'modal' in content.lower():
            rule_info['checks'].append('Modal Verb Usage')
        if 'consistency' in content.lower():
            rule_info['checks'].append('Consistency Checking')
        
        # Extract potential examples from strings
        string_literals = re.findall(r'["\']([^"\']{20,100})["\']', content)
        rule_info['examples'] = string_literals[:5]  # First 5 examples
        
        # Generate description based on file name and content
        name = rule_info['name'].replace('_', ' ').title()
        if 'passive' in rule_info['name']:
            rule_info['description'] = 'Detects and suggests alternatives for passive voice constructions'
            rule_info['purpose'] = 'Improve clarity and directness by promoting active voice'
        elif 'long_sentence' in rule_info['name']:
            rule_info['description'] = 'Identifies sentences that exceed recommended length limits'
            rule_info['purpose'] = 'Enhance readability by encouraging concise sentences'
        elif 'style' in rule_info['name']:
            rule_info['description'] = 'Enforces consistent writing style and formatting guidelines'
            rule_info['purpose'] = 'Maintain professional and consistent documentation standards'
        elif 'grammar' in rule_info['name']:
            rule_info['description'] = 'Checks for common grammatical errors and inconsistencies'
            rule_info['purpose'] = 'Ensure grammatical correctness and professional quality'
        elif 'terminology' in rule_info['name']:
            rule_info['description'] = 'Validates technical terminology and preferred word usage'
            rule_info['purpose'] = 'Maintain consistent technical vocabulary and terminology'
        elif 'consistency' in rule_info['name']:
            rule_info['description'] = 'Ensures consistent formatting and style throughout documents'
            rule_info['purpose'] = 'Maintain uniform presentation and professional appearance'
        elif 'vague' in rule_info['name']:
            rule_info['description'] = 'Identifies vague or imprecise language that should be clarified'
            rule_info['purpose'] = 'Improve precision and clarity in technical documentation'
        else:
            rule_info['description'] = f'Implements {name} checking and validation'
            rule_info['purpose'] = f'Ensures compliance with {name} guidelines'
    
    except Exception as e:
        print(f"⚠️ Error analyzing {rule_file_path}: {e}")
    
    return rule_info

def create_rule_pdf(rule_info, output_dir):
    """Create a PDF document for a single rule"""
    if not PDF_AVAILABLE:
        return False
    
    filename = f"{rule_info['name']}_documentation.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4, 
                          rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
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
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.darkblue
    )
    
    # Story container
    story = []
    
    # Title page
    rule_name = rule_info['name'].replace('_', ' ').title()
    story.append(Paragraph(f"{rule_name} Rule", title_style))
    story.append(Spacer(1, 20))
    
    # Subtitle
    story.append(Paragraph("DocScanner AI Writing Rule Documentation", styles['Heading3']))
    story.append(Spacer(1, 30))
    
    # Rule overview
    story.append(Paragraph("Rule Overview", heading_style))
    story.append(Paragraph(f"<b>Name:</b> {rule_name}", styles['Normal']))
    story.append(Paragraph(f"<b>File:</b> {rule_info['name']}.py", styles['Normal']))
    story.append(Paragraph(f"<b>Description:</b> {rule_info['description']}", styles['Normal']))
    story.append(Paragraph(f"<b>Purpose:</b> {rule_info['purpose']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Functions
    if rule_info['functions']:
        story.append(Paragraph("Functions", heading_style))
        for func in rule_info['functions']:
            story.append(Paragraph(f"<b>{func['name']}({', '.join(func['args'])})</b>", styles['Normal']))
            if func['docstring']:
                story.append(Paragraph(func['docstring'], styles['BodyText']))
            story.append(Spacer(1, 10))
    
    # Checks performed
    if rule_info['checks']:
        story.append(Paragraph("Checks Performed", heading_style))
        for check in rule_info['checks']:
            story.append(Paragraph(f"• {check}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Patterns
    if rule_info['patterns']:
        story.append(Paragraph("Regular Expression Patterns", heading_style))
        for pattern in rule_info['patterns'][:5]:  # Show first 5 patterns
            story.append(Paragraph(f"<font name='Courier'>{pattern}</font>", styles['Code']))
        story.append(Spacer(1, 20))
    
    # Examples
    if rule_info['examples']:
        story.append(Paragraph("Code Examples", heading_style))
        for example in rule_info['examples'][:3]:  # Show first 3 examples
            story.append(Paragraph(f"<font name='Courier'>{example}</font>", styles['Code']))
        story.append(Spacer(1, 20))
    
    # Dependencies
    if rule_info['imports']:
        story.append(Paragraph("Dependencies", heading_style))
        unique_imports = list(set(rule_info['imports']))[:10]  # Show unique imports
        for imp in unique_imports:
            story.append(Paragraph(f"• {imp}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Comments (insights)
    if rule_info.get('comments'):
        story.append(Paragraph("Implementation Notes", heading_style))
        for comment in rule_info['comments'][:5]:
            if len(comment.strip()) > 10:  # Only meaningful comments
                story.append(Paragraph(f"• {comment.strip()}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 50))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph("DocScanner AI - Writing Quality Enhancement System", styles['Normal']))
    
    # Build PDF
    try:
        doc.build(story)
        return True
    except Exception as e:
        print(f"❌ Failed to create PDF for {rule_info['name']}: {e}")
        return False

def create_master_index_pdf(all_rules, output_dir):
    """Create a master index PDF listing all rules"""
    if not PDF_AVAILABLE:
        return False
    
    filepath = os.path.join(output_dir, "00_Rules_Master_Index.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Title'], 
                                fontSize=24, alignment=TA_CENTER)
    story.append(Paragraph("DocScanner AI Writing Rules", title_style))
    story.append(Paragraph("Master Documentation Index", styles['Heading2']))
    story.append(Spacer(1, 30))
    
    # Summary table
    data = [['Rule Name', 'File', 'Description']]
    for rule in all_rules:
        name = rule['name'].replace('_', ' ').title()
        description = rule['description'][:60] + "..." if len(rule['description']) > 60 else rule['description']
        data.append([name, f"{rule['name']}.py", description])
    
    table = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Statistics
    story.append(Paragraph("Statistics", styles['Heading2']))
    story.append(Paragraph(f"Total Rules: {len(all_rules)}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    
    doc.build(story)
    return True

def generate_rule_documentation():
    """Main function to generate PDF documentation for all rules"""
    print("📚 DocScanner AI Rule Documentation Generator")
    print("=" * 60)
    
    # Check and install PDF dependencies
    global PDF_AVAILABLE
    if not PDF_AVAILABLE:
        print("📦 PDF library not found. Installing...")
        if install_pdf_dependencies():
            # Reload the module
            if import_pdf_libraries():
                print("✅ PDF libraries imported successfully")
            else:
                print("❌ Still unable to import PDF libraries after installation")
                return False
        else:
            print("❌ Unable to install PDF dependencies")
            return False
    
    # Find rules directory
    rules_dir = "app/rules"
    if not os.path.exists(rules_dir):
        print(f"❌ Rules directory not found: {rules_dir}")
        return False
    
    # Create output directory
    output_dir = "rule_documentation_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    
    # Find all Python rule files
    rule_files = []
    for file in os.listdir(rules_dir):
        if file.endswith('.py') and file != '__init__.py':
            rule_files.append(os.path.join(rules_dir, file))
    
    print(f"📋 Found {len(rule_files)} rule files")
    
    # Analyze and document each rule
    all_rules = []
    successful_pdfs = 0
    
    for rule_file in rule_files:
        print(f"📖 Analyzing {os.path.basename(rule_file)}...")
        rule_info = extract_rule_info(rule_file)
        all_rules.append(rule_info)
        
        if create_rule_pdf(rule_info, output_dir):
            successful_pdfs += 1
            print(f"   ✅ PDF created successfully")
        else:
            print(f"   ❌ PDF creation failed")
    
    # Create master index
    print("📚 Creating master index...")
    if create_master_index_pdf(all_rules, output_dir):
        print("   ✅ Master index created")
    else:
        print("   ❌ Master index creation failed")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DOCUMENTATION GENERATION COMPLETE")
    print(f"✅ Successfully created {successful_pdfs}/{len(rule_files)} rule PDFs")
    print(f"📁 Output location: {os.path.abspath(output_dir)}")
    print("\n📚 Generated Files:")
    
    if os.path.exists(output_dir):
        for file in sorted(os.listdir(output_dir)):
            if file.endswith('.pdf'):
                print(f"   📄 {file}")
    
    return successful_pdfs > 0

if __name__ == "__main__":
    success = generate_rule_documentation()
    if success:
        print("\n🎉 Documentation generation completed successfully!")
    else:
        print("\n❌ Documentation generation failed!")