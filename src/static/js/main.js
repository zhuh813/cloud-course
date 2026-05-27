document.addEventListener('DOMContentLoaded', () => {
    console.log('⚡ Antigravity Frontend Loaded.');
    
    // Core Elements
    const uptimeVal = document.getElementById('val-uptime');
    const pythonVal = document.getElementById('val-python');
    const platformVal = document.getElementById('val-platform');
    const portVal = document.getElementById('val-port');
    const serverTimeVal = document.getElementById('val-time');
    
    const consoleOutput = document.getElementById('console-output');
    const btnHealth = document.getElementById('btn-test-health');
    const btnStatus = document.getElementById('btn-test-status');
    
    const echoForm = document.getElementById('echo-form');
    const inputName = document.getElementById('input-name');
    const inputMessage = document.getElementById('input-message');

    // Telemetry Elements
    const valCpu = document.getElementById('val-cpu');
    const valMemory = document.getElementById('val-memory');
    const valSockets = document.getElementById('val-sockets');
    const barCpu = document.getElementById('bar-cpu');
    const barMemory = document.getElementById('bar-memory');
    const btnStressTest = document.getElementById('btn-stress-test');
    const stressBanner = document.getElementById('stress-banner');
    const stressTimer = document.getElementById('stress-timer');

    // File Explorer Elements
    const explorerFileList = document.getElementById('explorer-file-list');

    // Utility to format JSON nicely
    function writeToConsole(title, data, type = 'success') {
        const timestamp = new Date().toLocaleTimeString();
        let content = `[${timestamp}] // ${title}\n`;
        content += JSON.stringify(data, null, 2);
        
        consoleOutput.textContent = content;
        
        // Dynamic console colors
        if (type === 'error') {
            consoleOutput.style.color = '#ef4444';
        } else if (type === 'info') {
            consoleOutput.style.color = '#eab308';
        } else {
            consoleOutput.style.color = '#38bdf8';
        }
    }

    // Custom Code Inspector Formatter
    function writeCodeToConsole(filepath, content) {
        const timestamp = new Date().toLocaleTimeString();
        const lines = content.split('\n');
        let formatted = `[${timestamp}] // File Inspector // ${filepath}\n`;
        formatted += `// Total Lines: ${lines.length} // Encoding: UTF-8\n`;
        formatted += `// --------------------------------------------------\n\n`;
        
        lines.forEach((line, index) => {
            const lineNum = String(index + 1).padStart(3, ' ');
            formatted += `${lineNum} | ${line}\n`;
        });
        
        consoleOutput.textContent = formatted;
        consoleOutput.style.color = '#f1f5f9'; // Premium white code color
    }

    // Function to fetch system status
    async function updateSystemStatus(isInitial = false) {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            
            // Update UI elements
            if (uptimeVal) uptimeVal.textContent = `${data.uptime_seconds}s`;
            if (serverTimeVal) serverTimeVal.textContent = data.server_time;
            
            if (isInitial) {
                if (pythonVal) {
                    // Extract version summary
                    const mainVer = data.python_version.split(' ')[0];
                    pythonVal.textContent = mainVer;
                    pythonVal.title = data.python_version;
                }
                if (platformVal) platformVal.textContent = data.platform;
                if (portVal) portVal.textContent = data.port;
            }
        } catch (error) {
            console.error('Failed to fetch status:', error);
            if (uptimeVal) uptimeVal.textContent = 'Disconnected';
        }
    }

    // Function to update Cloud Metrics gauges
    async function updateMetrics() {
        try {
            const res = await fetch('/api/metrics');
            if (!res.ok) throw new Error('Failed to fetch metrics');
            const data = await res.json();

            // Update CPU metrics
            if (valCpu) valCpu.textContent = `${data.cpu_percentage}%`;
            if (barCpu) {
                barCpu.style.width = `${data.cpu_percentage}%`;
                // Color boundaries
                barCpu.className = 'gauge-bar-fill';
                if (data.cpu_percentage >= 80) {
                    barCpu.classList.add('danger');
                } else if (data.cpu_percentage >= 50) {
                    barCpu.classList.add('warning');
                }
            }

            // Update Memory metrics
            if (valMemory) valMemory.textContent = `${data.memory_percentage}%`;
            if (barMemory) {
                barMemory.style.width = `${data.memory_percentage}%`;
                barMemory.className = 'gauge-bar-fill';
                if (data.memory_percentage >= 80) {
                    barMemory.classList.add('danger');
                } else if (data.memory_percentage >= 50) {
                    barMemory.classList.add('warning');
                }
            }

            // Update Sockets
            if (valSockets) valSockets.textContent = data.active_sockets;

            // Handle stress alert decay banners
            if (stressBanner && stressTimer) {
                if (data.stress_active) {
                    stressBanner.style.display = 'flex';
                    stressTimer.textContent = `${data.stress_time_remaining}s`;
                } else {
                    stressBanner.style.display = 'none';
                }
            }
        } catch (err) {
            console.error('Metrics updating error:', err);
        }
    }

    // Function to load project files into explorer
    async function loadProjectFiles() {
        try {
            const res = await fetch('/api/files');
            if (!res.ok) throw new Error('Files query failed');
            const data = await res.json();
            
            if (explorerFileList) {
                explorerFileList.innerHTML = '';
                
                data.files.forEach(filepath => {
                    const item = document.createElement('div');
                    item.className = 'file-item';
                    item.setAttribute('data-filepath', filepath);

                    // Determine modern file icon
                    let icon = '📄';
                    if (filepath.endsWith('.py')) icon = '🐍';
                    else if (filepath.endsWith('.html')) icon = '🌐';
                    else if (filepath.endsWith('.css')) icon = '🎨';
                    else if (filepath.endsWith('.js')) icon = '⚡';
                    
                    item.innerHTML = `<span class="file-icon">${icon}</span> ${filepath}`;
                    
                    // Click handler to inspect code
                    item.addEventListener('click', async () => {
                        // Toggle active state classes
                        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
                        item.classList.add('active');

                        try {
                            const fileRes = await fetch(`/api/files/content?filepath=${encodeURIComponent(filepath)}`);
                            if (!fileRes.ok) throw new Error('File read failure');
                            const fileData = await fileRes.json();
                            
                            if (fileData.success) {
                                writeCodeToConsole(filepath, fileData.content);
                            } else {
                                writeToConsole(`FILE LOAD FAILED: ${filepath}`, fileData, 'error');
                            }
                        } catch (err) {
                            writeToConsole(`FILE READ ERROR`, { error: err.message, filepath }, 'error');
                        }
                    });
                    
                    explorerFileList.appendChild(item);
                });
            }
        } catch (err) {
            console.error('File explorer listing failure:', err);
            if (explorerFileList) {
                explorerFileList.innerHTML = `<div style="color: #ef4444; font-size: 0.85rem;">Failed to load workspace tree.</div>`;
            }
        }
    }

    // Event Listeners for Quick Action Buttons
    if (btnHealth) {
        btnHealth.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/health');
                const data = await res.json();
                writeToConsole('GET /api/health', data);
            } catch (err) {
                writeToConsole('GET /api/health ERROR', { error: err.message }, 'error');
            }
        });
    }

    if (btnStatus) {
        btnStatus.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                writeToConsole('GET /api/status', data);
            } catch (err) {
                writeToConsole('GET /api/status ERROR', { error: err.message }, 'error');
            }
        });
    }

    // Interactive Peak Cloud Load Trigger
    if (btnStressTest) {
        btnStressTest.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/metrics/stress', { method: 'POST' });
                const data = await res.json();
                writeToConsole('POST /api/metrics/stress', data, 'info');
                // Surge metrics immediately
                updateMetrics();
            } catch (err) {
                writeToConsole('POST /api/metrics/stress ERROR', { error: err.message }, 'error');
            }
        });
    }

    // Interactive echo test submission
    if (echoForm) {
        echoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = inputName.value.trim() || 'Guest';
            const message = inputMessage.value.trim() || 'Hello from the browser!';
            
            try {
                const res = await fetch('/api/echo', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, message })
                });
                
                if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
                const data = await res.json();
                writeToConsole('POST /api/echo', data, 'success');
            } catch (err) {
                writeToConsole('POST /api/echo ERROR', { error: err.message }, 'error');
            }
        });
    }

    // Initial loads
    updateSystemStatus(true);
    updateMetrics();
    loadProjectFiles();
    
    // Auto-refresh stats every 3 seconds
    setInterval(() => {
        updateSystemStatus(false);
    }, 3000);

    // Auto-refresh cloud telemetry metrics every 2 seconds
    setInterval(() => {
        updateMetrics();
    }, 2000);
});
