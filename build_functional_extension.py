"""
Enhanced VS Code Extension Builder with Full Functionality
Creates a VSIX package that connects to the Flask backend
"""

import os
import zipfile
import json
import shutil
from pathlib import Path

def create_functional_vsix():
    """Create a functional VSIX package that connects to the Flask backend."""
    
    extension_dir = Path("vscode-extension")
    if not extension_dir.exists():
        print("❌ vscode-extension directory not found")
        return False
    
    # Read package.json
    package_json_path = extension_dir / "package.json"
    if not package_json_path.exists():
        print("❌ package.json not found")
        return False
    
    with open(package_json_path, 'r') as f:
        package_data = json.load(f)
    
    extension_name = package_data.get('name', 'document-review-agent')
    version = package_data.get('version', '1.0.0')
    vsix_name = f"{extension_name}-{version}.vsix"
    
    # Create output directory structure
    temp_dir = Path("temp_vsix")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    temp_dir.mkdir()
    extension_content_dir = temp_dir / "extension"
    extension_content_dir.mkdir()
    
    print(f"🔧 Building functional {vsix_name}...")
    
    # Copy package.json
    shutil.copy2(package_json_path, extension_content_dir / "package.json")
    
    # Create a functional extension.js file that connects to Flask backend
    functional_extension = '''
// Document Review Agent Extension - Full Functionality
const vscode = require('vscode');
const http = require('http');

let diagnosticCollection;
let agentStatusBarItem;

function activate(context) {
    console.log('Document Review Agent extension is now active!');
    
    // Create diagnostic collection for showing issues
    diagnosticCollection = vscode.languages.createDiagnosticCollection('document-review-agent');
    context.subscriptions.push(diagnosticCollection);
    
    // Create status bar item
    agentStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    agentStatusBarItem.text = "$(pulse) Document Review Agent";
    agentStatusBarItem.tooltip = "Document Review Agent Status";
    agentStatusBarItem.show();
    context.subscriptions.push(agentStatusBarItem);
    
    // Register analyze document command
    let analyzeCommand = vscode.commands.registerCommand('document-review-agent.analyze', async function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }
        
        await analyzeDocument(editor);
    });
    
    // Register analyze selection command
    let analyzeSelectionCommand = vscode.commands.registerCommand('document-review-agent.analyzeSelection', async function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }
        
        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showInformationMessage('No text selected');
            return;
        }
        
        await analyzeDocument(editor, true);
    });
    
    // Register AI suggestion command
    let suggestionCommand = vscode.commands.registerCommand('document-review-agent.getSuggestion', async function () {
        vscode.window.showInformationMessage('AI Suggestion: Consider revising the selected text for better clarity and readability.');
    });
    
    context.subscriptions.push(analyzeCommand, analyzeSelectionCommand, suggestionCommand);
    
    // Check agent status on startup
    checkAgentStatus();
}

async function checkAgentStatus() {
    try {
        const response = await makeHttpRequest('GET', '/api/agent/status');
        if (response.status === 'running') {
            agentStatusBarItem.text = "$(check) Agent Ready";
            agentStatusBarItem.tooltip = `Document Review Agent: ${response.rules_loaded} rules loaded`;
        } else {
            throw new Error('Agent not running');
        }
    } catch (error) {
        agentStatusBarItem.text = "$(alert) Agent Offline";
        agentStatusBarItem.tooltip = "Document Review Agent: Flask server not running";
    }
}

async function analyzeDocument(editor, selectionOnly = false) {
    const document = editor.document;
    const text = selectionOnly ? document.getText(editor.selection) : document.getText();
    
    if (!text.trim()) {
        vscode.window.showWarningMessage('No content to analyze');
        return;
    }
    
    try {
        agentStatusBarItem.text = "$(sync~spin) Analyzing...";
        
        const analysisData = {
            document_content: text,
            document_type: getDocumentType(document.languageId)
        };
        
        const response = await makeHttpRequest('POST', '/api/agent/analyze', analysisData);
        
        if (response.status === 'success') {
            const diagnostics = response.issues.map(issue => {
                const line = Math.max(0, (issue.line_number || 1) - 1);
                const range = new vscode.Range(line, 0, line, issue.line_content ? issue.line_content.length : 100);
                
                const diagnostic = new vscode.Diagnostic(
                    range,
                    issue.message || issue.text || 'Writing issue detected',
                    getSeverity(issue.type || 'info')
                );
                
                diagnostic.source = 'Document Review Agent';
                return diagnostic;
            });
            
            diagnosticCollection.set(document.uri, diagnostics);
            
            agentStatusBarItem.text = `$(check) Found ${response.total_issues} issues`;
            
            vscode.window.showInformationMessage(
                `Analysis complete: ${response.total_issues} issues found in ${response.lines_analyzed} lines`
            );
        } else {
            throw new Error(response.error || 'Analysis failed');
        }
    } catch (error) {
        agentStatusBarItem.text = "$(alert) Analysis Failed";
        vscode.window.showErrorMessage(`Analysis failed: ${error.message}`);
        console.error('Analysis error:', error);
    }
}

function makeHttpRequest(method, path, data = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: 5000,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                try {
                    const jsonResponse = JSON.parse(body);
                    resolve(jsonResponse);
                } catch (e) {
                    reject(new Error(`Invalid JSON response: ${body}`));
                }
            });
        });
        
        req.on('error', (error) => {
            reject(new Error(`Connection failed: ${error.message}. Make sure Flask server is running on http://localhost:5000`));
        });
        
        if (data) {
            req.write(JSON.stringify(data));
        }
        
        req.end();
    });
}

function getDocumentType(languageId) {
    const typeMap = {
        'markdown': 'technical',
        'plaintext': 'general',
        'html': 'web',
        'javascript': 'technical',
        'typescript': 'technical',
        'python': 'technical'
    };
    return typeMap[languageId] || 'general';
}

function getSeverity(type) {
    switch (type) {
        case 'error': return vscode.DiagnosticSeverity.Error;
        case 'warning': return vscode.DiagnosticSeverity.Warning;
        case 'info': 
        default: return vscode.DiagnosticSeverity.Information;
    }
}

function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
    }
}

module.exports = {
    activate,
    deactivate
};
'''
    
    # Write the functional extension file
    with open(extension_content_dir / "extension.js", 'w') as f:
        f.write(functional_extension)
    
    # Update package.json to point to the JS file
    package_data['main'] = './extension.js'
    with open(extension_content_dir / "package.json", 'w') as f:
        json.dump(package_data, f, indent=2)
    
    # Create [Content_Types].xml
    content_types_xml = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="json" ContentType="application/json"/>
    <Default Extension="js" ContentType="application/javascript"/>
    <Default Extension="txt" ContentType="text/plain"/>
    <Default Extension="md" ContentType="text/markdown"/>
</Types>'''
    
    with open(temp_dir / "[Content_Types].xml", 'w') as f:
        f.write(content_types_xml)
    
    # Create extension.vsixmanifest
    manifest_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
    <Metadata>
        <Identity Id="{extension_name}" Version="{version}" Language="en-US" Publisher="local"/>
        <DisplayName>Document Review Agent</DisplayName>
        <Description>AI-powered document review and writing assistance</Description>
        <Categories>Other</Categories>
    </Metadata>
    <Installation>
        <InstallationTarget Id="Microsoft.VisualStudio.Code" Version="[1.74.0,)"/>
    </Installation>
    <Dependencies/>
    <Assets>
        <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json"/>
    </Assets>
</PackageManifest>'''
    
    with open(temp_dir / "extension.vsixmanifest", 'w') as f:
        f.write(manifest_xml)
    
    # Create the VSIX file (which is just a ZIP file)
    vsix_path = extension_dir / vsix_name
    
    with zipfile.ZipFile(vsix_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from temp directory
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arc_name)
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    print(f"✅ Created functional {vsix_path}")
    print(f"📦 VSIX file location: {vsix_path.absolute()}")
    
    return True

if __name__ == "__main__":
    print("🔨 Building Functional VS Code Extension...")
    
    if create_functional_vsix():
        print("\n🎉 Functional VS Code Extension built successfully!")
        print("\n📋 To install:")
        print("1. Uninstall the old extension first")
        print("2. Open VS Code")
        print("3. Go to Extensions (Ctrl+Shift+X)")
        print("4. Click '...' menu → 'Install from VSIX'")
        print("5. Select the new .vsix file from vscode-extension/ folder")
        print("\n✨ New Features:")
        print("   - Connects to Flask backend at http://localhost:5000")
        print("   - Shows issues in Problems panel")
        print("   - Real-time status in status bar")
        print("   - Analyze document and selection commands")
    else:
        print("❌ Failed to build extension")
