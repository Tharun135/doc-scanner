import * as vscode from 'vscode';

export class SuggestionsProvider implements vscode.TreeDataProvider<SuggestionItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<SuggestionItem | undefined | null | void> = new vscode.EventEmitter<SuggestionItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<SuggestionItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private suggestions: SuggestionData[] = [];

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    addSuggestion(suggestion: SuggestionData): void {
        this.suggestions.unshift(suggestion); // Add to beginning
        // Keep only the last 50 suggestions
        if (this.suggestions.length > 50) {
            this.suggestions = this.suggestions.slice(0, 50);
        }
        this.refresh();
    }

    clearAll(): void {
        this.suggestions = [];
        this.refresh();
    }

    getTreeItem(element: SuggestionItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: SuggestionItem): Promise<SuggestionItem[]> {
        if (!element) {
            // Root level - show all suggestions
            return this.suggestions.map((suggestion, index) => 
                new SuggestionItem(
                    suggestion.issue.substring(0, 50) + (suggestion.issue.length > 50 ? '...' : ''),
                    suggestion.confidence,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    this.getConfidenceIcon(suggestion.confidence),
                    suggestion,
                    index
                )
            );
        } else if (element.suggestion) {
            // Show details for a specific suggestion
            const suggestion = element.suggestion;
            const items: SuggestionItem[] = [];
            
            items.push(new SuggestionItem(
                'Issue',
                suggestion.issue,
                vscode.TreeItemCollapsibleState.None,
                'warning'
            ));
            
            items.push(new SuggestionItem(
                'Suggestion',
                suggestion.suggestion,
                vscode.TreeItemCollapsibleState.None,
                'lightbulb'
            ));
            
            items.push(new SuggestionItem(
                'Confidence',
                suggestion.confidence,
                vscode.TreeItemCollapsibleState.None,
                this.getConfidenceIcon(suggestion.confidence)
            ));
            
            items.push(new SuggestionItem(
                'Method',
                suggestion.method,
                vscode.TreeItemCollapsibleState.None,
                'gear'
            ));
            
            if (suggestion.context) {
                items.push(new SuggestionItem(
                    'Context',
                    suggestion.context.substring(0, 100) + (suggestion.context.length > 100 ? '...' : ''),
                    vscode.TreeItemCollapsibleState.None,
                    'quote'
                ));
            }
            
            return items;
        }
        
        return [];
    }

    private getConfidenceIcon(confidence: string): string {
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

interface SuggestionData {
    issue: string;
    suggestion: string;
    confidence: string;
    method: string;
    context?: string;
    timestamp: Date;
}

class SuggestionItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly value: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        iconName?: string,
        public readonly suggestion?: SuggestionData,
        public readonly index?: number
    ) {
        super(label, collapsibleState);
        
        if (value && value !== label) {
            (this as any).description = value.length > 50 ? value.substring(0, 50) + '...' : value;
        }
        
        (this as any).tooltip = suggestion 
            ? `${suggestion.issue}\n\nSuggestion: ${suggestion.suggestion}\nConfidence: ${suggestion.confidence}`
            : `${label}: ${value}`;
        
        if (iconName) {
            (this as any).iconPath = new vscode.ThemeIcon(iconName);
        }
        
        // Add context menu for suggestions
        if (suggestion && index !== undefined) {
            this.contextValue = 'suggestion';
        }
    }
}

export { SuggestionData, SuggestionItem };
