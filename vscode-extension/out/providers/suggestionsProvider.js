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
exports.SuggestionItem = exports.SuggestionsProvider = void 0;
const vscode = __importStar(require("vscode"));
class SuggestionsProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.suggestions = [];
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    addSuggestion(suggestion) {
        this.suggestions.unshift(suggestion); // Add to beginning
        // Keep only the last 50 suggestions
        if (this.suggestions.length > 50) {
            this.suggestions = this.suggestions.slice(0, 50);
        }
        this.refresh();
    }
    clearAll() {
        this.suggestions = [];
        this.refresh();
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren(element) {
        if (!element) {
            // Root level - show all suggestions
            return this.suggestions.map((suggestion, index) => new SuggestionItem(suggestion.issue.substring(0, 50) + (suggestion.issue.length > 50 ? '...' : ''), suggestion.confidence, vscode.TreeItemCollapsibleState.Collapsed, this.getConfidenceIcon(suggestion.confidence), suggestion, index));
        }
        else if (element.suggestion) {
            // Show details for a specific suggestion
            const suggestion = element.suggestion;
            const items = [];
            items.push(new SuggestionItem('Issue', suggestion.issue, vscode.TreeItemCollapsibleState.None, 'warning'));
            items.push(new SuggestionItem('Suggestion', suggestion.suggestion, vscode.TreeItemCollapsibleState.None, 'lightbulb'));
            items.push(new SuggestionItem('Confidence', suggestion.confidence, vscode.TreeItemCollapsibleState.None, this.getConfidenceIcon(suggestion.confidence)));
            items.push(new SuggestionItem('Method', suggestion.method, vscode.TreeItemCollapsibleState.None, 'gear'));
            if (suggestion.context) {
                items.push(new SuggestionItem('Context', suggestion.context.substring(0, 100) + (suggestion.context.length > 100 ? '...' : ''), vscode.TreeItemCollapsibleState.None, 'quote'));
            }
            return items;
        }
        return [];
    }
    getConfidenceIcon(confidence) {
        switch (confidence.toLowerCase()) {
            case 'high':
                return 'check-all';
            case 'medium':
                return 'check';
            case 'low':
                return 'question';
            default:
                return 'circle-outline';
        }
    }
}
exports.SuggestionsProvider = SuggestionsProvider;
class SuggestionItem extends vscode.TreeItem {
    constructor(label, value, collapsibleState, iconName, suggestion, index) {
        super(label, collapsibleState);
        this.label = label;
        this.value = value;
        this.collapsibleState = collapsibleState;
        this.suggestion = suggestion;
        this.index = index;
        if (value && value !== label) {
            this.description = value.length > 50 ? value.substring(0, 50) + '...' : value;
        }
        this.tooltip = suggestion
            ? `${suggestion.issue}\n\nSuggestion: ${suggestion.suggestion}\nConfidence: ${suggestion.confidence}`
            : `${label}: ${value}`;
        if (iconName) {
            this.iconPath = new vscode.ThemeIcon(iconName);
        }
        // Add context menu for suggestions
        if (suggestion && index !== undefined) {
            this.contextValue = 'suggestion';
        }
    }
}
exports.SuggestionItem = SuggestionItem;
//# sourceMappingURL=suggestionsProvider.js.map