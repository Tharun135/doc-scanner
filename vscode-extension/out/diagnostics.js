"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DiagnosticsManager = void 0;
const vscode = __importStar(require("vscode"));
class DiagnosticsManager {
    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('document-review-agent');
    }
    updateDiagnostics(uri, analysisResult) {
        const config = vscode.workspace.getConfiguration('documentReviewAgent');
        const enableDiagnostics = config.get('enableDiagnostics', true);
        if (!enableDiagnostics) {
            return;
        }
        const severity = this.getSeverityFromConfig(config.get('diagnosticSeverity', 'Information'));
        const diagnostics = [];
        // Process suggestions to create diagnostics
        if (analysisResult.suggestions && Array.isArray(analysisResult.suggestions)) {
            for (const suggestion of analysisResult.suggestions) {
                if (suggestion.sentence_index !== undefined && suggestion.issue) {
                    // Create a diagnostic for each issue
                    const diagnostic = new vscode.Diagnostic(this.getRange(suggestion.sentence_index, suggestion.sentence || ''), suggestion.issue, severity);
                    diagnostic.source = 'Document Review Agent';
                    diagnostic.code = this.getIssueCode(suggestion.issue);
                    // Add suggestion as a related information
                    if (suggestion.suggestion) {
                        diagnostic.relatedInformation = [
                            new vscode.DiagnosticRelatedInformation(new vscode.Location(uri, diagnostic.range), `Suggestion: ${suggestion.suggestion}`)
                        ];
                    }
                    diagnostics.push(diagnostic);
                }
            }
        }
        this.diagnosticCollection.set(uri, diagnostics);
    }
    clearDiagnostics(uri) {
        this.diagnosticCollection.set(uri, []);
    }
    clearAll() {
        this.diagnosticCollection.clear();
    }
    dispose() {
        this.diagnosticCollection.dispose();
    }
    getSeverityFromConfig(severityString) {
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
    getRange(sentenceIndex, sentence) {
        // For now, create a range for the entire line
        // In a more sophisticated implementation, we could parse the document
        // to find the exact position of the sentence
        const line = sentenceIndex || 0;
        const startPos = new vscode.Position(line, 0);
        const endPos = new vscode.Position(line, sentence.length || 100);
        return new vscode.Range(startPos, endPos);
    }
    getIssueCode(issue) {
        // Generate a code based on the issue type
        const lowerIssue = issue.toLowerCase();
        if (lowerIssue.includes('passive voice')) {
            return 'PASSIVE_VOICE';
        }
        else if (lowerIssue.includes('long sentence')) {
            return 'LONG_SENTENCE';
        }
        else if (lowerIssue.includes('may')) {
            return 'MODAL_VERB';
        }
        else if (lowerIssue.includes('backup') || lowerIssue.includes('back up')) {
            return 'WORD_USAGE';
        }
        else if (lowerIssue.includes('repeated')) {
            return 'REPETITION';
        }
        else if (lowerIssue.includes('capitalize')) {
            return 'CAPITALIZATION';
        }
        else {
            return 'GENERAL';
        }
    }
}
exports.DiagnosticsManager = DiagnosticsManager;
//# sourceMappingURL=diagnostics.js.map