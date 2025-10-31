
// WebSocket Fallback Fix for Document Upload
// This code provides graceful fallback when WebSocket (Flask-SocketIO) is not available

// Enhanced socket connection with better error handling
function initializeSocketWithFallback() {
    const socket = io({
        transports: ['polling', 'websocket'],
        timeout: 5000,
        forceNew: true
    });
    
    let socketConnected = false;
    let fallbackMode = false;
    
    socket.on('connect', () => {
        console.log('✅ WebSocket connected successfully');
        socketConnected = true;
        fallbackMode = false;
    });
    
    socket.on('disconnect', () => {
        console.log('⚠️ WebSocket disconnected');
        socketConnected = false;
    });
    
    socket.on('connect_error', (error) => {
        console.warn('⚠️ WebSocket connection failed, using fallback mode:', error.message);
        socketConnected = false;
        fallbackMode = true;
    });
    
    // Override emit function to handle failures gracefully
    const originalEmit = socket.emit.bind(socket);
    socket.emit = function(...args) {
        if (socketConnected) {
            return originalEmit(...args);
        } else {
            console.log('🔄 Socket emit ignored (fallback mode):', args[0]);
        }
    };
    
    // Add fallback progress simulation when WebSocket is not available
    socket.simulateProgress = function(roomId, callback) {
        if (!fallbackMode) return;
        
        console.log('🔄 Starting fallback progress simulation for room:', roomId);
        
        const stages = [
            { percentage: 10, message: "Uploading document...", stage_name: "Upload" },
            { percentage: 30, message: "Parsing content...", stage_name: "Parse" },
            { percentage: 50, message: "Extracting sentences...", stage_name: "Extract" },
            { percentage: 80, message: "Analyzing with rules...", stage_name: "Analyze" },
            { percentage: 100, message: "Generating report...", stage_name: "Report" }
        ];
        
        let currentStage = 0;
        
        const updateProgress = () => {
            if (currentStage < stages.length) {
                const stage = stages[currentStage];
                callback({
                    percentage: stage.percentage,
                    message: stage.message,
                    stage_name: stage.stage_name,
                    elapsed_time: (currentStage + 1) * 0.5,
                    eta_seconds: (stages.length - currentStage - 1) * 0.5,
                    completed: false
                });
                currentStage++;
                setTimeout(updateProgress, 500); // Update every 500ms
            } else {
                // Final completion
                callback({
                    percentage: 100,
                    message: "Analysis complete!",
                    stage_name: "Complete",
                    completed: true,
                    success: true
                });
            }
        };
        
        setTimeout(updateProgress, 100); // Start after 100ms
    };
    
    return { socket, socketConnected: () => socketConnected, fallbackMode: () => fallbackMode };
}

// Enhanced file upload with fallback support
async function processSingleFileWithFallback(file) {
    try {
        showProgressLoader();
        
        // Get room ID for progress tracking
        const roomResponse = await fetch('/start_upload', { method: 'POST' });
        const roomData = await roomResponse.json();
        currentRoomId = roomData.room_id;
        
        console.log('📋 Upload session started:', currentRoomId);
        
        // Set up progress handling
        let progressReceived = false;
        let uploadCompleted = false;
        
        const handleProgressUpdate = (data) => {
            progressReceived = true;
            updateProgressBar(data.percentage, data.message, data.stage_name);
            
            if (data.completed) {
                uploadCompleted = true;
                setTimeout(() => {
                    hideProgressLoader();
                    if (data.success !== false) {
                        console.log('✅ Upload completed successfully via progress update');
                    }
                }, 1000);
            }
        };
        
        // Try WebSocket progress tracking first
        if (typeof socket !== 'undefined' && socket.socketConnected && socket.socketConnected()) {
            console.log('🔌 Using WebSocket for progress tracking');
            socket.emit('join_progress_room', { room_id: currentRoomId });
            socket.on('progress_update', handleProgressUpdate);
        } else {
            console.log('🔄 WebSocket unavailable, using fallback progress simulation');
            if (typeof socket !== 'undefined' && socket.simulateProgress) {
                socket.simulateProgress(currentRoomId, handleProgressUpdate);
            }
        }
        
        // Upload the file
        const formData = new FormData();
        formData.append('file', file);
        formData.append('room_id', currentRoomId);
        
        console.log('📤 Starting file upload...');
        
        const uploadResponse = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        console.log('📨 Upload response received:', uploadResponse.status);
        
        if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.status} ${uploadResponse.statusText}`);
        }
        
        const result = await uploadResponse.json();
        console.log('📊 Upload result:', result);
        
        // Fallback: If no progress updates received and upload is complete, show results
        setTimeout(() => {
            if (!progressReceived || !uploadCompleted) {
                console.log('🔄 No progress updates received, showing results directly');
                hideProgressLoader();
                
                if (result.content) {
                    displayAnalysisResults(result);
                    console.log('✅ Results displayed successfully (fallback mode)');
                } else {
                    console.error('❌ No content in upload result');
                    alert('Upload completed but no results received. Please try again.');
                }
            }
        }, 2000); // Wait 2 seconds for progress updates
        
    } catch (error) {
        console.error('❌ Upload error:', error);
        hideProgressLoader();
        alert('Upload failed: ' + error.message);
    }
}

// Function to display analysis results
function displayAnalysisResults(result) {
    try {
        if (result.content && result.sentences) {
            // Clear previous results
            const analysisResults = document.getElementById('analysisResults');
            if (analysisResults) {
                analysisResults.style.display = 'block';
            }
            
            // Update content display
            const contentDisplay = document.getElementById('contentDisplay');
            if (contentDisplay) {
                contentDisplay.innerHTML = result.content;
            }
            
            // Update statistics
            const report = result.report || {};
            updateStatistics(report);
            
            // Update sentences display
            updateSentencesDisplay(result.sentences);
            
            console.log('📊 Analysis results displayed successfully');
        } else {
            throw new Error('Invalid result format');
        }
    } catch (error) {
        console.error('❌ Error displaying results:', error);
        alert('Error displaying analysis results: ' + error.message);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing WebSocket with fallback support...');
    
    // Initialize socket connection with fallback
    if (typeof io !== 'undefined') {
        const { socket: socketInstance, socketConnected, fallbackMode } = initializeSocketWithFallback();
        window.socket = socketInstance;
        window.socketConnected = socketConnected;
        window.fallbackMode = fallbackMode;
        
        console.log('✅ WebSocket fallback system initialized');
    } else {
        console.warn('⚠️ Socket.IO not available, using direct HTTP mode');
    }
});
