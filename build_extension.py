"""
Simple VS Code Extension Builder
Creates a basic VSIX package without requiring Node.js build tools
"""

import os
import zipfile
import json
import shutil
from pathlib import Path

def create_simple_vsix():
    """Create a simple VSIX package manually."""
    
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
    
    print(f"🔧 Building {vsix_name}...")
    
    # Copy essential files
    essential_files = [
        "package.json",
        # We'll create a minimal main file since TypeScript compilation isn't available
    ]
    
    for file_name in essential_files:
        src = extension_dir / file_name
        if src.exists():
            shutil.copy2(src, extension_content_dir / file_name)
    
    # Create a minimal extension.js file (since we can't compile TypeScript without Node.js)
    minimal_extension = '''
// Minimal Document Review Agent Extension
const vscode = require('vscode');

function activate(context) {
    console.log('Document Review Agent extension is now active!');
    
    // Register a simple command
    let disposable = vscode.commands.registerCommand('document-review-agent.analyze', function () {
        vscode.window.showInformationMessage('Document Review Agent: Please install Python dependencies and start the Flask server at http://localhost:5000');
    });
    
    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
'''
    
    # Write the minimal extension file
    with open(extension_content_dir / "extension.js", 'w') as f:
        f.write(minimal_extension)
    
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
    
    print(f"✅ Created {vsix_path}")
    print(f"📦 VSIX file location: {vsix_path.absolute()}")
    
    return True

if __name__ == "__main__":
    print("🔨 Building VS Code Extension...")
    
    if create_simple_vsix():
        print("\n🎉 VS Code Extension built successfully!")
        print("\n📋 To install:")
        print("1. Open VS Code")
        print("2. Go to Extensions (Ctrl+Shift+X)")
        print("3. Click '...' menu → 'Install from VSIX'")
        print("4. Select the .vsix file from vscode-extension/ folder")
        print("\n⚠️  Note: This is a minimal version. For full functionality:")
        print("   - Install Node.js from https://nodejs.org/")
        print("   - Run 'npm install' in vscode-extension/")
        print("   - Run 'npm run compile' to build the TypeScript source")
    else:
        print("❌ Failed to build extension")
