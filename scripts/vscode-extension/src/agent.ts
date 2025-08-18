import axios from 'axios';
import * as vscode from 'vscode';

export interface AnalysisResult {
    success: boolean;
    data?: any;
    error?: string;
    execution_time?: number;
    timestamp?: string;
}

export interface AgentStatus {
    is_running: boolean;
    queue_size: number;
    cached_results: number;
    capabilities: string[];
    version: string;
}

export interface SuggestionResult {
    success: boolean;
    suggestion?: any;
    error?: string;
}

export class DocumentReviewAgent {
    private baseUrl: string;
    private mcpUrl: string;
    private mcpSocket?: WebSocket;
    private isConnected: boolean = false;

    constructor() {
        const config = vscode.workspace.getConfiguration('documentReviewAgent');
        this.baseUrl = config.get('agentUrl', 'http://localhost:5000');
        this.mcpUrl = config.get('mcpUrl', 'ws://localhost:8765');
    }

    async start(): Promise<void> {
        try {
            // First check if the Flask server is running
            await this.checkServerHealth();
            
            // Try to connect to MCP server
            await this.connectMCP();
            
            this.isConnected = true;
        } catch (error) {
            throw new Error(`Failed to start agent: ${error}`);
        }
    }

    async stop(): Promise<void> {
        if (this.mcpSocket) {
            this.mcpSocket.close();
            this.mcpSocket = undefined;
        }
        this.isConnected = false;
    }

    async getStatus(): Promise<AgentStatus> {
        try {
            const response = await axios.get(`${this.baseUrl}/api/agent/status`, {
                timeout: 5000
            });
            
            if (response.data.success) {
                return response.data.status;
            } else {
                throw new Error(response.data.error || 'Failed to get status');
            }
        } catch (error) {
            // Return offline status if request fails
            return {
                is_running: false,
                queue_size: 0,
                cached_results: 0,
                capabilities: [],
                version: 'unknown'
            };
        }
    }

    async analyzeDocument(documentPath: string, documentType: string = 'general'): Promise<AnalysisResult> {
        try {
            const config = vscode.workspace.getConfiguration('documentReviewAgent');
            const writingGoals = config.get('writingGoals', ['clarity', 'conciseness', 'professionalism']);

            const response = await axios.post(`${this.baseUrl}/api/agent/analyze`, {
                document_path: documentPath,
                document_type: documentType,
                writing_goals: writingGoals
            }, {
                timeout: 30000
            });

            return {
                success: response.data.success,
                data: response.data.data,
                error: response.data.error,
                execution_time: response.data.execution_time,
                timestamp: response.data.timestamp
            };
        } catch (error) {
            if (axios.isAxiosError(error)) {
                return {
                    success: false,
                    error: `Network error: ${error.message}`
                };
            }
            return {
                success: false,
                error: `Analysis error: ${error}`
            };
        }
    }

    async analyzeText(text: string, documentType: string = 'general'): Promise<AnalysisResult> {
        // For text analysis, we'll create a temporary file or use a different endpoint
        // For now, let's use the suggestion endpoint to analyze text
        try {
            const response = await axios.post(`${this.baseUrl}/api/agent/suggest`, {
                feedback_text: 'Analyze this text for quality issues',
                sentence_context: text,
                document_type: documentType
            }, {
                timeout: 15000
            });

            return {
                success: response.data.success,
                data: response.data.suggestion,
                error: response.data.error
            };
        } catch (error) {
            if (axios.isAxiosError(error)) {
                return {
                    success: false,
                    error: `Network error: ${error.message}`
                };
            }
            return {
                success: false,
                error: `Text analysis error: ${error}`
            };
        }
    }

    async getSuggestion(feedbackText: string, sentenceContext: string = '', documentType: string = 'general'): Promise<SuggestionResult> {
        try {
            const response = await axios.post(`${this.baseUrl}/api/agent/suggest`, {
                feedback_text: feedbackText,
                sentence_context: sentenceContext,
                document_type: documentType
            }, {
                timeout: 15000
            });

            return {
                success: response.data.success,
                suggestion: response.data.suggestion,
                error: response.data.error
            };
        } catch (error) {
            if (axios.isAxiosError(error)) {
                return {
                    success: false,
                    error: `Network error: ${error.message}`
                };
            }
            return {
                success: false,
                error: `Suggestion error: ${error}`
            };
        }
    }

    async batchAnalyze(filePaths: string[], progressCallback?: (processed: number, total: number) => void): Promise<AnalysisResult> {
        try {
            const response = await axios.post(`${this.baseUrl}/api/agent/batch`, {
                file_paths: filePaths,
                parallel: true
            }, {
                timeout: 120000 // 2 minute timeout for batch processing
            });

            // Simulate progress updates since the current API doesn't support them
            if (progressCallback) {
                progressCallback(filePaths.length, filePaths.length);
            }

            return {
                success: response.data.success,
                data: response.data.data,
                error: response.data.error,
                execution_time: response.data.execution_time,
                timestamp: response.data.timestamp
            };
        } catch (error) {
            if (axios.isAxiosError(error)) {
                return {
                    success: false,
                    error: `Network error: ${error.message}`
                };
            }
            return {
                success: false,
                error: `Batch analysis error: ${error}`
            };
        }
    }

    async assessQuality(documentPath: string): Promise<AnalysisResult> {
        try {
            const response = await axios.post(`${this.baseUrl}/api/agent/quality`, {
                document_path: documentPath
            }, {
                timeout: 30000
            });

            return {
                success: response.data.success,
                data: response.data.quality_assessment,
                error: response.data.error,
                execution_time: response.data.execution_time,
                timestamp: response.data.timestamp
            };
        } catch (error) {
            if (axios.isAxiosError(error)) {
                return {
                    success: false,
                    error: `Network error: ${error.message}`
                };
            }
            return {
                success: false,
                error: `Quality assessment error: ${error}`
            };
        }
    }

    async getCapabilities(): Promise<any[]> {
        try {
            const response = await axios.get(`${this.baseUrl}/api/agent/capabilities`, {
                timeout: 5000
            });

            if (response.data.success) {
                return response.data.capabilities;
            } else {
                throw new Error(response.data.error || 'Failed to get capabilities');
            }
        } catch (error) {
            console.error('Failed to get capabilities:', error);
            return [];
        }
    }

    private async checkServerHealth(): Promise<void> {
        try {
            const response = await axios.get(`${this.baseUrl}/api/agent/health`, {
                timeout: 5000
            });

            if (!response.data.success || !response.data.healthy) {
                throw new Error('Server is not healthy');
            }
        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.code === 'ECONNREFUSED') {
                    throw new Error('Cannot connect to Flask server. Please make sure it\'s running on ' + this.baseUrl);
                }
                throw new Error(`Server health check failed: ${error.message}`);
            }
            throw error;
        }
    }

    private async connectMCP(): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                this.mcpSocket = new WebSocket(this.mcpUrl);
                
                this.mcpSocket.addEventListener('open', () => {
                    console.log('Connected to MCP server');
                    resolve();
                });

                this.mcpSocket.addEventListener('error', (error) => {
                    console.warn('MCP connection failed:', error);
                    // Don't reject - MCP is optional
                    resolve();
                });

                this.mcpSocket.addEventListener('close', () => {
                    console.log('MCP connection closed');
                });

                this.mcpSocket.addEventListener('message', (data) => {
                    try {
                        const message = JSON.parse(data.toString());
                        this.handleMCPMessage(message);
                    } catch (error) {
                        console.error('Failed to parse MCP message:', error);
                    }
                });

                // Timeout for connection
                setTimeout(() => {
                    if (this.mcpSocket?.readyState !== WebSocket.OPEN) {
                        console.warn('MCP connection timeout');
                        resolve(); // Don't fail if MCP is unavailable
                    }
                }, 5000);

            } catch (error) {
                console.warn('MCP setup failed:', error);
                resolve(); // Don't fail if MCP is unavailable
            }
        });
    }

    private handleMCPMessage(message: any): void {
        // Handle MCP protocol messages
        console.log('Received MCP message:', message);
        
        // This would handle various MCP message types
        // For now, just log them
    }

    async sendMCPRequest(method: string, params: any): Promise<any> {
        if (!this.mcpSocket || this.mcpSocket.readyState !== WebSocket.OPEN) {
            throw new Error('MCP connection not available');
        }

        return new Promise((resolve, reject) => {
            const id = Math.random().toString(36).substr(2, 9);
            const message = {
                id,
                type: 'request',
                method,
                params
            };

            // Set up response handler
            const timeout = setTimeout(() => {
                reject(new Error('MCP request timeout'));
            }, 10000);

            const handleResponse = (data: any) => {
                try {
                    const response = JSON.parse(data.toString());
                    if (response.id === id) {
                        clearTimeout(timeout);
                        this.mcpSocket?.removeEventListener('message', handleResponse);
                        
                        if (response.error) {
                            reject(new Error(response.error.message));
                        } else {
                            resolve(response.result);
                        }
                    }
                } catch (error) {
                    // Ignore parsing errors for other messages
                }
            };

            this.mcpSocket.addEventListener('message', handleResponse);
            this.mcpSocket.send(JSON.stringify(message));
            this.mcpSocket = new WebSocket(this.mcpUrl);
        });
    }

    isAgentConnected(): boolean {
        return this.isConnected;
    }

    isMCPConnected(): boolean {
        return this.mcpSocket?.readyState === WebSocket.OPEN;
    }
}
