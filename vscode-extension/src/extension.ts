import * as vscode from 'vscode';
import { DocumentReviewAgent } from './agent';
import { AgentStatusProvider } from './providers/statusProvider';
import { DocumentResultsProvider } from './providers/resultsProvider';
import { SuggestionsProvider } from './providers/suggestionsProvider';
import { DiagnosticsManager } from './diagnostics';

let agent: DocumentReviewAgent;
let statusProvider: AgentStatusProvider;
let resultsProvider: DocumentResultsProvider;
let suggestionsProvider: SuggestionsProvider;
let diagnosticsManager: DiagnosticsManager;

export function activate(context: vscode.ExtensionContext) {
    console.log('Document Review Agent extension is now active!');

    // Initialize the agent
    agent = new DocumentReviewAgent();
    
    // Initialize providers
    statusProvider = new AgentStatusProvider(agent);
    resultsProvider = new DocumentResultsProvider();
    suggestionsProvider = new SuggestionsProvider();
    
    // Initialize diagnostics manager
    diagnosticsManager = new DiagnosticsManager();
    
    // Register tree data providers
    vscode.window.registerTreeDataProvider('agentStatus', statusProvider);
    vscode.window.registerTreeDataProvider('documentResults', resultsProvider);
    vscode.window.registerTreeDataProvider('suggestions', suggestionsProvider);
    
    // Set context for views
    vscode.commands.executeCommand('setContext', 'document-review-agent:activated', true);

    // Register commands
    registerCommands(context);
    
    // Auto-start agent if configured
    const config = vscode.workspace.getConfiguration('documentReviewAgent');
    if (config.get('autoStart', true)) {
        vscode.commands.executeCommand('document-review-agent.startAgent');
    }
    
    // Set up file watchers for auto-analysis
    setupFileWatchers(context);
}

function registerCommands(context: vscode.ExtensionContext) {
    // Register all commands
    const commands = [
        vscode.commands.registerCommand('document-review-agent.analyze', analyzeDocument),
        vscode.commands.registerCommand('document-review-agent.analyzeSelection', analyzeSelection),
        vscode.commands.registerCommand('document-review-agent.getSuggestion', getSuggestion),
        vscode.commands.registerCommand('document-review-agent.batchAnalyze', batchAnalyze),
        vscode.commands.registerCommand('document-review-agent.showDashboard', showDashboard),
        vscode.commands.registerCommand('document-review-agent.startAgent', startAgent),
        vscode.commands.registerCommand('document-review-agent.stopAgent', stopAgent),
        vscode.commands.registerCommand('document-review-agent.refreshStatus', refreshStatus),
        vscode.commands.registerCommand('document-review-agent.clearResults', clearResults),
        vscode.commands.registerCommand('document-review-agent.exportResults', exportResults)
    ];
    
    commands.forEach(command => context.subscriptions.push(command));
}

function setupFileWatchers(context: vscode.ExtensionContext) {
    // Watch for file changes and auto-analyze if enabled
    const watcher = vscode.workspace.createFileSystemWatcher('**/*.{md,txt,html,adoc}');
    
    watcher.onDidChange(async (uri) => {
        const config = vscode.workspace.getConfiguration('documentReviewAgent');
        if (config.get('autoAnalyze', false)) {
            await analyzeDocument(uri);
        }
    });
    
    context.subscriptions.push(watcher);
}

// Command implementations

async function analyzeDocument(uri?: vscode.Uri) {
    try {
        let documentUri: vscode.Uri;
        
        if (uri) {
            documentUri = uri;
        } else {
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor) {
                vscode.window.showErrorMessage('No active document to analyze');
                return;
            }
            documentUri = activeEditor.document.uri;
        }
        
        // Show progress
        const result = await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Analyzing document...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0, message: 'Starting analysis...' });
            
            const analysis = await agent.analyzeDocument(documentUri.fsPath);
            
            progress.report({ increment: 100, message: 'Analysis complete!' });
            return analysis;
        });
        
        if (result.success) {
            // Update results provider
            resultsProvider.addResult(documentUri.fsPath, result.data);
            
            // Update diagnostics
            if (vscode.workspace.getConfiguration('documentReviewAgent').get('enableDiagnostics', true)) {
                diagnosticsManager.updateDiagnostics(documentUri, result.data);
            }
            
            // Show success message
            vscode.window.showInformationMessage(
                `Analysis complete: ${result.data.total_issues} issues found`,
                'View Results'
            ).then(selection => {
                if (selection === 'View Results') {
                    vscode.commands.executeCommand('document-review-agent.showDashboard');
                }
            });
            
            // Update context
            vscode.commands.executeCommand('setContext', 'document-review-agent:hasResults', true);
        } else {
            vscode.window.showErrorMessage(`Analysis failed: ${result.error}`);
        }
        
    } catch (error) {
        vscode.window.showErrorMessage(`Analysis error: ${error}`);
    }
}

async function analyzeSelection() {
    const activeEditor = vscode.window.activeTextEditor;
    if (!activeEditor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }
    
    const selection = activeEditor.selection;
    if (selection.isEmpty) {
        vscode.window.showErrorMessage('No text selected');
        return;
    }
    
    const selectedText = activeEditor.document.getText(selection);
    
    try {
        const result = await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Analyzing selection...',
            cancellable: false
        }, async () => {
            return await agent.analyzeText(selectedText);
        });
        
        if (result.success) {
            // Show results in a new panel
            const panel = vscode.window.createWebviewPanel(
                'selectionAnalysis',
                'Selection Analysis',
                vscode.ViewColumn.Beside,
                { enableScripts: true }
            );
            
            panel.webview.html = generateAnalysisHTML(result.data, selectedText);
        } else {
            vscode.window.showErrorMessage(`Selection analysis failed: ${result.error}`);
        }
        
    } catch (error) {
        vscode.window.showErrorMessage(`Selection analysis error: ${error}`);
    }
}

async function getSuggestion() {
    const activeEditor = vscode.window.activeTextEditor;
    if (!activeEditor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }
    
    // Get cursor position or selection
    const selection = activeEditor.selection;
    const position = selection.active;
    
    // For now, let user input the issue they want help with
    const issue = await vscode.window.showInputBox({
        prompt: 'Describe the writing issue you need help with',
        placeHolder: 'e.g., "passive voice", "long sentence", "unclear meaning"'
    });
    
    if (!issue) {
        return;
    }
    
    // Get context (current line or selection)
    const context = selection.isEmpty 
        ? activeEditor.document.lineAt(position.line).text
        : activeEditor.document.getText(selection);
    
    try {
        const suggestion = await agent.getSuggestion(issue, context);
        
        if (suggestion.success) {
            // Show suggestion in a quick pick or panel
            const action = await vscode.window.showQuickPick([
                'Apply Suggestion',
                'View Details',
                'Dismiss'
            ], {
                placeHolder: suggestion.data.suggestion
            });
            
            if (action === 'Apply Suggestion') {
                // Try to apply the suggestion automatically
                await applySuggestion(activeEditor, selection, suggestion.data);
            } else if (action === 'View Details') {
                showSuggestionDetails(suggestion.data);
            }
        } else {
            vscode.window.showErrorMessage(`Could not generate suggestion: ${suggestion.error}`);
        }
        
    } catch (error) {
        vscode.window.showErrorMessage(`Suggestion error: ${error}`);
    }
}

async function batchAnalyze() {
    // Get all relevant files in workspace
    const files = await vscode.workspace.findFiles('**/*.{md,txt,html,adoc}', '**/node_modules/**');
    
    if (files.length === 0) {
        vscode.window.showInformationMessage('No documents found to analyze');
        return;
    }
    
    const confirmed = await vscode.window.showWarningMessage(
        `Analyze ${files.length} documents? This may take a while.`,
        'Yes', 'No'
    );
    
    if (confirmed !== 'Yes') {
        return;
    }
    
    try {
        const results = await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Batch analyzing documents...',
            cancellable: true
        }, async (progress, token) => {
            const filePaths = files.map(file => file.fsPath);
            
            return await agent.batchAnalyze(filePaths, (processed, total) => {
                const percentage = (processed / total) * 100;
                progress.report({ 
                    increment: percentage / total,
                    message: `${processed}/${total} documents processed`
                });
            });
        });
        
        if (results.success) {
            // Update results
            results.data.results.forEach((result: any, index: number) => {
                if (!result.error) {
                    resultsProvider.addResult(files[index].fsPath, result);
                }
            });
            
            vscode.window.showInformationMessage(
                `Batch analysis complete: ${results.data.successful_files}/${results.data.total_files} files processed`,
                'View Results'
            ).then(selection => {
                if (selection === 'View Results') {
                    vscode.commands.executeCommand('document-review-agent.showDashboard');
                }
            });
        } else {
            vscode.window.showErrorMessage(`Batch analysis failed: ${results.error}`);
        }
        
    } catch (error) {
        vscode.window.showErrorMessage(`Batch analysis error: ${error}`);
    }
}

async function showDashboard() {
    // Create dashboard webview panel
    const panel = vscode.window.createWebviewPanel(
        'documentReviewDashboard',
        'Document Review Dashboard',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );
    
    // Get current results and status
    const status = await agent.getStatus();
    const results = resultsProvider.getAllResults();
    
    panel.webview.html = generateDashboardHTML(status, results);
    
    // Handle messages from webview
    panel.webview.onDidReceiveMessage(async (message) => {
        switch (message.command) {
            case 'refreshData':
                const newStatus = await agent.getStatus();
                const newResults = resultsProvider.getAllResults();
                panel.webview.postMessage({
                    command: 'updateData',
                    status: newStatus,
                    results: newResults
                });
                break;
                
            case 'analyzeFile':
                await analyzeDocument(vscode.Uri.file(message.filePath));
                break;
        }
    });
}

async function startAgent() {
    try {
        await agent.start();
        statusProvider.refresh();
        vscode.window.showInformationMessage('Document Review Agent started');
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to start agent: ${error}`);
    }
}

async function stopAgent() {
    try {
        await agent.stop();
        statusProvider.refresh();
        vscode.window.showInformationMessage('Document Review Agent stopped');
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to stop agent: ${error}`);
    }
}

function refreshStatus() {
    statusProvider.refresh();
}

function clearResults() {
    resultsProvider.clearAll();
    diagnosticsManager.clearAll();
    vscode.commands.executeCommand('setContext', 'document-review-agent:hasResults', false);
    vscode.window.showInformationMessage('Results cleared');
}

async function exportResults() {
    const results = resultsProvider.getAllResults();
    
    if (Object.keys(results).length === 0) {
        vscode.window.showInformationMessage('No results to export');
        return;
    }
    
    const uri = await vscode.window.showSaveDialog({
        defaultUri: vscode.Uri.file('document-review-results.json'),
        filters: {
            'JSON Files': ['json']
        }
    });
    
    if (uri) {
        try {
            const content = JSON.stringify(results, null, 2);
            await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf8'));
            vscode.window.showInformationMessage('Results exported successfully');
        } catch (error) {
            vscode.window.showErrorMessage(`Export failed: ${error}`);
        }
    }
}

// Helper functions

async function applySuggestion(editor: vscode.TextEditor, selection: vscode.Selection, suggestion: any) {
    // Try to parse the suggestion and apply it
    // This is a basic implementation - could be more sophisticated
    
    if (suggestion.suggestion && suggestion.suggestion.includes('CORRECTED TEXT:')) {
        const match = suggestion.suggestion.match(/CORRECTED TEXT:\s*"([^"]*)"/);
        if (match) {
            const correctedText = match[1];
            await editor.edit(editBuilder => {
                editBuilder.replace(selection, correctedText);
            });
            vscode.window.showInformationMessage('Suggestion applied');
        }
    } else {
        vscode.window.showInformationMessage('Could not automatically apply this suggestion');
    }
}

function showSuggestionDetails(suggestion: any) {
    const panel = vscode.window.createWebviewPanel(
        'suggestionDetails',
        'Suggestion Details',
        vscode.ViewColumn.Beside,
        { enableScripts: true }
    );
    
    panel.webview.html = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Suggestion Details</title>
            <style>
                body { font-family: var(--vscode-font-family); padding: 20px; }
                .suggestion { background: var(--vscode-editor-background); padding: 15px; border-radius: 5px; margin: 10px 0; }
                .confidence { color: var(--vscode-textLink-foreground); font-weight: bold; }
                .method { color: var(--vscode-descriptionForeground); font-style: italic; }
            </style>
        </head>
        <body>
            <h2>AI Suggestion</h2>
            <div class="suggestion">
                <p><strong>Suggestion:</strong></p>
                <p>${suggestion.suggestion}</p>
                <p><strong>Confidence:</strong> <span class="confidence">${suggestion.confidence}</span></p>
                <p><strong>Method:</strong> <span class="method">${suggestion.method}</span></p>
            </div>
        </body>
        </html>
    `;
}

function generateAnalysisHTML(analysis: any, text: string): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Analysis Results</title>
            <style>
                body { font-family: var(--vscode-font-family); padding: 20px; }
                .text { background: var(--vscode-editor-background); padding: 15px; border-radius: 5px; margin: 10px 0; }
                .issue { background: var(--vscode-inputValidation-warningBackground); padding: 10px; margin: 5px 0; border-radius: 3px; }
                .summary { background: var(--vscode-textBlockQuote-background); padding: 15px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h2>Selection Analysis</h2>
            <div class="text">
                <h3>Analyzed Text:</h3>
                <p>${text}</p>
            </div>
            <div class="summary">
                <h3>Summary:</h3>
                <p>Total Issues: ${analysis.total_issues || 0}</p>
                <p>Quality Score: ${analysis.quality_score || 'N/A'}</p>
            </div>
            <h3>Issues Found:</h3>
            ${(analysis.suggestions || []).map((suggestion: any) => `
                <div class="issue">
                    <p><strong>Issue:</strong> ${suggestion.issue}</p>
                    <p><strong>Suggestion:</strong> ${suggestion.suggestion}</p>
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function generateDashboardHTML(status: any, results: any): string {
    const resultEntries = Object.entries(results);
    
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document Review Dashboard</title>
            <style>
                body { 
                    font-family: var(--vscode-font-family); 
                    padding: 20px; 
                    background: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                }
                .status { 
                    background: var(--vscode-textBlockQuote-background); 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin-bottom: 20px; 
                }
                .results { margin-top: 20px; }
                .result-item { 
                    background: var(--vscode-editor-background); 
                    border: 1px solid var(--vscode-panel-border);
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px; 
                }
                .metric { display: inline-block; margin-right: 20px; }
                .file-path { color: var(--vscode-textLink-foreground); cursor: pointer; }
                button { 
                    background: var(--vscode-button-background); 
                    color: var(--vscode-button-foreground); 
                    border: none; 
                    padding: 8px 12px; 
                    border-radius: 3px; 
                    cursor: pointer; 
                    margin: 5px;
                }
                button:hover { background: var(--vscode-button-hoverBackground); }
            </style>
        </head>
        <body>
            <h1>Document Review Dashboard</h1>
            
            <div class="status">
                <h2>Agent Status</h2>
                <div class="metric">Status: ${status?.is_running ? 'Running' : 'Stopped'}</div>
                <div class="metric">Queue Size: ${status?.queue_size || 0}</div>
                <div class="metric">Cached Results: ${status?.cached_results || 0}</div>
                <button onclick="refreshData()">Refresh</button>
            </div>
            
            <div class="results">
                <h2>Analysis Results (${resultEntries.length} files)</h2>
                ${resultEntries.map(([filePath, result]: [string, any]) => `
                    <div class="result-item">
                        <div class="file-path" onclick="analyzeFile('${filePath}')">${filePath}</div>
                        <div class="metric">Sentences: ${result.total_sentences || 0}</div>
                        <div class="metric">Issues: ${result.total_issues || 0}</div>
                        <div class="metric">Quality: ${result.quality_score || 'N/A'}</div>
                        <div class="metric">Suggestions: ${(result.suggestions || []).length}</div>
                    </div>
                `).join('')}
            </div>
            
            <script>
                const vscode = acquireVsCodeApi();
                
                function refreshData() {
                    vscode.postMessage({ command: 'refreshData' });
                }
                
                function analyzeFile(filePath) {
                    vscode.postMessage({ command: 'analyzeFile', filePath: filePath });
                }
                
                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.command === 'updateData') {
                        location.reload();
                    }
                });
            </script>
        </body>
        </html>
    `;
}

export function deactivate() {
    if (agent) {
        agent.stop();
    }
}
