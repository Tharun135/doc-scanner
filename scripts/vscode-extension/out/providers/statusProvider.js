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
exports.AgentStatusProvider = void 0;
const vscode = __importStar(require("vscode"));
class AgentStatusProvider {
    constructor(agent) {
        this.agent = agent;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren(element) {
        if (!element) {
            // Root level - get agent status
            try {
                const status = await this.agent.getStatus();
                return [
                    new StatusItem('Agent Status', status.is_running ? 'Running' : 'Stopped', vscode.TreeItemCollapsibleState.Expanded, status.is_running ? 'check' : 'close'),
                    new StatusItem('Connection', this.agent.isAgentConnected() ? 'Connected' : 'Disconnected', vscode.TreeItemCollapsibleState.None, this.agent.isAgentConnected() ? 'plug' : 'debug-disconnect'),
                    new StatusItem('Queue Size', status.queue_size.toString(), vscode.TreeItemCollapsibleState.None, 'list-ordered'),
                    new StatusItem('Cached Results', status.cached_results.toString(), vscode.TreeItemCollapsibleState.None, 'database'),
                    new StatusItem('Version', status.version, vscode.TreeItemCollapsibleState.None, 'info')
                ];
            }
            catch (error) {
                return [
                    new StatusItem('Error', 'Failed to get status', vscode.TreeItemCollapsibleState.None, 'error')
                ];
            }
        }
        return [];
    }
}
exports.AgentStatusProvider = AgentStatusProvider;
class StatusItem extends vscode.TreeItem {
    constructor(label, value, collapsibleState, iconName) {
        super(`${label}: ${value}`, collapsibleState);
        this.label = label;
        this.value = value;
        this.collapsibleState = collapsibleState;
        this.tooltip = `${this.label}: ${this.value}`;
        this.description = this.value;
        if (iconName) {
            this.iconPath = new vscode.ThemeIcon(iconName);
        }
    }
}
//# sourceMappingURL=statusProvider.js.map