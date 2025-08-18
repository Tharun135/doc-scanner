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
exports.DocumentResultsProvider = void 0;
const vscode = __importStar(require("vscode"));
class DocumentResultsProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.results = {};
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    addResult(filePath, result) {
        this.results[filePath] = result;
        this.refresh();
    }
    clearAll() {
        this.results = {};
        this.refresh();
    }
    getAllResults() {
        return this.results;
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren(element) {
        if (!element) {
            // Root level - show all analyzed files
            const items = [];
            for (const [filePath, result] of Object.entries(this.results)) {
                const fileName = filePath.split(/[/\\]/).pop() || filePath;
                const issueCount = result.total_issues || 0;
                const qualityScore = result.quality_score || 0;
                items.push(new ResultItem(fileName, `${issueCount} issues, score: ${qualityScore}`, vscode.TreeItemCollapsibleState.Collapsed, 'file', filePath));
            }
            return items.sort((a, b) => a.label.localeCompare(b.label));
        }
        else if (element.filePath) {
            // Show details for a specific file
            const result = this.results[element.filePath];
            if (!result)
                return [];
            const items = [];
            // Add summary items
            items.push(new ResultItem('Total Sentences', (result.total_sentences || 0).toString(), vscode.TreeItemCollapsibleState.None, 'symbol-number'));
            items.push(new ResultItem('Total Issues', (result.total_issues || 0).toString(), vscode.TreeItemCollapsibleState.None, 'warning'));
            items.push(new ResultItem('Quality Score', (result.quality_score || 0).toString(), vscode.TreeItemCollapsibleState.None, 'star'));
            // Add processing time if available
            if (result.processing_time) {
                items.push(new ResultItem('Processing Time', `${result.processing_time}s`, vscode.TreeItemCollapsibleState.None, 'clock'));
            }
            return items;
        }
        return [];
    }
}
exports.DocumentResultsProvider = DocumentResultsProvider;
class ResultItem extends vscode.TreeItem {
    constructor(label, value, collapsibleState, iconName, filePath) {
        super(`${label}`, collapsibleState);
        this.label = label;
        this.value = value;
        this.collapsibleState = collapsibleState;
        this.filePath = filePath;
        if (value) {
            this.description = value;
        }
        this.tooltip = filePath ? `${label} - ${filePath}` : `${label}: ${value}`;
        if (iconName) {
            this.iconPath = new vscode.ThemeIcon(iconName);
        }
        // Add command to open file when clicked
        if (filePath) {
            this.command = {
                command: 'vscode.open',
                title: 'Open File',
                arguments: [vscode.Uri.file(filePath)]
            };
        }
    }
}
//# sourceMappingURL=resultsProvider.js.map