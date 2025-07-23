import * as vscode from 'vscode';
import { DocumentReviewAgent, AgentStatus } from '../agent';

export class AgentStatusProvider implements vscode.TreeDataProvider<StatusItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<StatusItem | undefined | null | void> = new vscode.EventEmitter<StatusItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<StatusItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private agent: DocumentReviewAgent) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: StatusItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: StatusItem): Promise<StatusItem[]> {
        if (!element) {
            // Root level - get agent status
            try {
                const status = await this.agent.getStatus();
                return [
                    new StatusItem(
                        'Agent Status',
                        status.is_running ? 'Running' : 'Stopped',
                        vscode.TreeItemCollapsibleState.Expanded,
                        status.is_running ? 'check' : 'close'
                    ),
                    new StatusItem(
                        'Connection',
                        this.agent.isAgentConnected() ? 'Connected' : 'Disconnected',
                        vscode.TreeItemCollapsibleState.None,
                        this.agent.isAgentConnected() ? 'plug' : 'debug-disconnect'
                    ),
                    new StatusItem(
                        'Queue Size',
                        status.queue_size.toString(),
                        vscode.TreeItemCollapsibleState.None,
                        'list-ordered'
                    ),
                    new StatusItem(
                        'Cached Results',
                        status.cached_results.toString(),
                        vscode.TreeItemCollapsibleState.None,
                        'database'
                    ),
                    new StatusItem(
                        'Version',
                        status.version,
                        vscode.TreeItemCollapsibleState.None,
                        'info'
                    )
                ];
            } catch (error) {
                return [
                    new StatusItem(
                        'Error',
                        'Failed to get status',
                        vscode.TreeItemCollapsibleState.None,
                        'error'
                    )
                ];
            }
        }
        return [];
    }
}

class StatusItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly value: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        iconName?: string
    ) {
        super(`${label}: ${value}`, collapsibleState);
        this.tooltip = `${this.label}: ${this.value}`;
        this.description = this.value;
        
        if (iconName) {
            this.iconPath = new vscode.ThemeIcon(iconName);
        }
    }
}
