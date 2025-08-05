import * as vscode from 'vscode';

export class DocumentResultsProvider implements vscode.TreeDataProvider<ResultItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ResultItem | undefined | null | void> = new vscode.EventEmitter<ResultItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ResultItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private results: { [filePath: string]: any } = {};

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    addResult(filePath: string, result: any): void {
        this.results[filePath] = result;
        this.refresh();
    }

    clearAll(): void {
        this.results = {};
        this.refresh();
    }

    getAllResults(): { [filePath: string]: any } {
        return this.results;
    }

    getTreeItem(element: ResultItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: ResultItem): Promise<ResultItem[]> {
        if (!element) {
            // Root level - show all analyzed files
            const items: ResultItem[] = [];
            
            for (const [filePath, result] of Object.entries(this.results)) {
                const fileName = filePath.split(/[/\\]/).pop() || filePath;
                const issueCount = result.total_issues || 0;
                const qualityScore = result.quality_score || 0;
                
                items.push(new ResultItem(
                    fileName,
                    `${issueCount} issues, score: ${qualityScore}`,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'file',
                    filePath
                ));
            }
            
            return items.sort((a, b) => (a.label as string).localeCompare(b.label as string));
        } else if (element.filePath) {
            // Show details for a specific file
            const result = this.results[element.filePath];
            if (!result) return [];
            
            const items: ResultItem[] = [];
            
            // Add summary items
            items.push(new ResultItem(
                'Total Sentences',
                (result.total_sentences || 0).toString(),
                vscode.TreeItemCollapsibleState.None,
                'symbol-number'
            ));
            
            items.push(new ResultItem(
                'Total Issues',
                (result.total_issues || 0).toString(),
                vscode.TreeItemCollapsibleState.None,
                'warning'
            ));
            
            items.push(new ResultItem(
                'Quality Score',
                (result.quality_score || 0).toString(),
                vscode.TreeItemCollapsibleState.None,
                'star'
            ));
            
            // Add processing time if available
            if (result.processing_time) {
                items.push(new ResultItem(
                    'Processing Time',
                    `${result.processing_time}s`,
                    vscode.TreeItemCollapsibleState.None,
                    'clock'
                ));
            }
            
            return items;
        }
        
        return [];
    }
}

class ResultItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly value: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        iconName?: string,
        public readonly filePath?: string
    ) {
        super(`${label}`, collapsibleState);
        
        if (value) {
            (this as any).description = value;
        }
        
        (this as any).tooltip = filePath ? `${label} - ${filePath}` : `${label}: ${value}`;
        
        if (iconName) {
            (this as any).iconPath = new vscode.ThemeIcon(iconName);
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
