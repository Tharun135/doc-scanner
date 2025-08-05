import * as vscode from 'vscode';

export class DiagnosticsManager {
    private diagnosticCollection: vscode.DiagnosticCollection;

    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('document-review-agent');
    }

    updateDiagnostics(uri: vscode.Uri, analysisResult: any): void {
        const config = vscode.workspace.getConfiguration('documentReviewAgent');
        const enableDiagnostics = config.get('enableDiagnostics', true);
        
        if (!enableDiagnostics) {
            return;
        }

        const severity = this.getSeverityFromConfig(config.get('diagnosticSeverity', 'Information'));
        const diagnostics: vscode.Diagnostic[] = [];

        // Process suggestions to create diagnostics
        if (analysisResult.suggestions && Array.isArray(analysisResult.suggestions)) {
            for (const suggestion of analysisResult.suggestions) {
                if (suggestion.sentence_index !== undefined && suggestion.issue) {
                    // Create a diagnostic for each issue
                    const diagnostic = new vscode.Diagnostic(
                        this.getRange(suggestion.sentence_index, suggestion.sentence || ''),
                        suggestion.issue,
                        severity
                    );

                    diagnostic.source = 'Document Review Agent';
                    diagnostic.code = this.getIssueCode(suggestion.issue);
                    
                    // Add suggestion as a related information
                    if (suggestion.suggestion) {
                        diagnostic.relatedInformation = [
                            new vscode.DiagnosticRelatedInformation(
                                new vscode.Location(uri, diagnostic.range),
                                `Suggestion: ${suggestion.suggestion}`
                            )
                        ];
                    }

                    diagnostics.push(diagnostic);
                }
            }
        }

        this.diagnosticCollection.set(uri, diagnostics);
    }

    clearDiagnostics(uri: vscode.Uri): void {
        this.diagnosticCollection.set(uri, []);
    }

    clearAll(): void {
        this.diagnosticCollection.clear();
    }

    dispose(): void {
        this.diagnosticCollection.dispose();
    }

    private getSeverityFromConfig(severityString: string): vscode.DiagnosticSeverity {
        switch (severityString) {
            case 'Error':
                return vscode.DiagnosticSeverity.Error;
            case 'Warning':
                return vscode.DiagnosticSeverity.Warning;
            case 'Information':
                return vscode.DiagnosticSeverity.Information;
            case 'Hint':
                return vscode.DiagnosticSeverity.Hint;
            default:
                return vscode.DiagnosticSeverity.Information;
        }
    }

    private getRange(sentenceIndex: number, sentence: string): vscode.Range {
        // For now, create a range for the entire line
        // In a more sophisticated implementation, we could parse the document
        // to find the exact position of the sentence
        const line = sentenceIndex || 0;
        const startPos = new vscode.Position(line, 0);
        const endPos = new vscode.Position(line, sentence.length || 100);
        return new vscode.Range(startPos, endPos);
    }

    private getIssueCode(issue: string): string {
        // Generate a code based on the issue type
        const lowerIssue = issue.toLowerCase();
        
        if (lowerIssue.includes('passive voice')) {
            return 'PASSIVE_VOICE';
        } else if (lowerIssue.includes('long sentence')) {
            return 'LONG_SENTENCE';
        } else if (lowerIssue.includes('may')) {
            return 'MODAL_VERB';
        } else if (lowerIssue.includes('backup') || lowerIssue.includes('back up')) {
            return 'WORD_USAGE';
        } else if (lowerIssue.includes('repeated')) {
            return 'REPETITION';
        } else if (lowerIssue.includes('capitalize')) {
            return 'CAPITALIZATION';
        } else {
            return 'GENERAL';
        }
    }
}
