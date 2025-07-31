/**
 * OSINT Geolocation Analyzer - Frontend Application
 * Real implementation with OpenStreetMap integration
 */

class GeolocationAnalyzer {
    constructor() {
        this.apiBase = '/api';
        this.map = null;
        this.currentMarkers = [];
        this.currentImageId = null;
        this.init();
    }

    init() {
        // Initialize UI event handlers
        this.setupFileUpload();
        this.setupControlHandlers();
        this.setupResultHandlers();
        this.initializeMap();
    }

    setupFileUpload() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');

        // Click to browse
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });

        // Drag and drop handlers
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });
    }

    setupControlHandlers() {
        // Analysis button
        document.getElementById('analyze-btn').addEventListener('click', () => {
            if (this.currentImageId) {
                this.startAnalysis();
            }
        });

        // Reset button
        document.getElementById('reset-analysis')?.addEventListener('click', () => {
            this.resetInterface();
        });

        // Retry button
        document.getElementById('retry-btn')?.addEventListener('click', () => {
            if (this.currentImageId) {
                this.startAnalysis();
            }
        });
    }

    setupResultHandlers() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });

        // Report generation buttons
        document.getElementById('generate-report-btn')?.addEventListener('click', () => {
            if (this.currentImageId) {
                this.generateReport('markdown');
            }
        });

        document.getElementById('download-report-btn')?.addEventListener('click', () => {
            if (this.currentImageId) {
                this.downloadReport('markdown');
            }
        });

        document.getElementById('view-html-report-btn')?.addEventListener('click', () => {
            if (this.currentImageId) {
                this.viewHTMLReport();
            }
        });

        // Map controls
        document.getElementById('center-map')?.addEventListener('click', () => {
            this.centerMapOnResults();
        });

        // Export buttons
        document.getElementById('export-json')?.addEventListener('click', () => {
            this.exportResults('json');
        });

        // Legacy report button (if exists)
        document.getElementById('export-report')?.addEventListener('click', () => {
            this.exportResults('report');
        });
    }

    initializeMap() {
        // Initialize Leaflet map centered on world view
        this.map = L.map('map').setView([20, 0], 2);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);

        // Add satellite toggle functionality
        const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: '© Esri',
            maxZoom: 19
        });

        let usingSatellite = false;
        document.getElementById('satellite-toggle')?.addEventListener('click', () => {
            if (usingSatellite) {
                this.map.removeLayer(satelliteLayer);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors',
                    maxZoom: 19
                }).addTo(this.map);
                usingSatellite = false;
            } else {
                this.map.eachLayer((layer) => {
                    if (layer instanceof L.TileLayer) {
                        this.map.removeLayer(layer);
                    }
                });
                satelliteLayer.addTo(this.map);
                usingSatellite = true;
            }
        });
    }

    async handleFileSelect(file) {
        try {
            // Validate file
            if (!this.validateFile(file)) {
                return;
            }

            // Show preview
            this.showImagePreview(file);

            // Upload file
            const formData = new FormData();
            formData.append('file', file);

            this.showProgress('Uploading image...', 10);

            const response = await fetch(`${this.apiBase}/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.currentImageId = data.image_id;
                this.showControls();
                this.showProgress('Upload complete!', 20);
                this.hideProgress();
            } else {
                this.showError(data.error || 'Upload failed');
            }

        } catch (error) {
            this.showError(`Upload error: ${error.message}`);
        }
    }

    validateFile(file) {
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (!allowedTypes.includes(file.type)) {
            this.showError('Invalid file type. Please upload a JPEG, PNG, or WebP image.');
            return false;
        }

        if (file.size > maxSize) {
            this.showError('File too large. Maximum size is 10MB.');
            return false;
        }

        return true;
    }

    showImagePreview(file) {
        const preview = document.getElementById('image-preview');
        const img = document.getElementById('preview-img');
        const filename = document.getElementById('image-filename');
        const details = document.getElementById('image-details');

        const reader = new FileReader();
        reader.onload = (e) => {
            img.src = e.target.result;
            filename.textContent = file.name;
            details.textContent = `Size: ${(file.size / 1024 / 1024).toFixed(2)} MB • Type: ${file.type}`;
            preview.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    showControls() {
        document.getElementById('controls-section').classList.remove('hidden');
    }

    async startAnalysis() {
        try {
            this.hideError();
            this.showProgress('Starting analysis...', 25);
            this.updateProgressStep('step-upload', 'completed');
            this.updateProgressStep('step-exif', 'active');

            const response = await fetch(`${this.apiBase}/analyze/${this.currentImageId}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.simulateProgressSteps();
                // Poll for results
                setTimeout(() => this.pollResults(), 2000);
            } else {
                this.showError(data.error || 'Analysis failed');
            }

        } catch (error) {
            this.showError(`Analysis error: ${error.message}`);
        }
    }

    simulateProgressSteps() {
        // Simulate progress through analysis steps
        const steps = [
            { id: 'step-exif', progress: 40, delay: 1000 },
            { id: 'step-ocr', progress: 60, delay: 2000 },
            { id: 'step-vision', progress: 80, delay: 1000 },
            { id: 'step-scoring', progress: 95, delay: 1000 }
        ];

        steps.forEach((step, index) => {
            setTimeout(() => {
                if (index > 0) {
                    this.updateProgressStep(steps[index - 1].id, 'completed');
                }
                this.updateProgressStep(step.id, 'active');
                this.showProgress(`Processing step ${index + 2}...`, step.progress);
            }, step.delay);
        });
    }

    async pollResults() {
        try {
            const response = await fetch(`${this.apiBase}/results/${this.currentImageId}`);
            const data = await response.json();

            if (response.ok && data.success) {
                this.updateProgressStep('step-scoring', 'completed');
                this.showProgress('Analysis complete!', 100);
                setTimeout(() => {
                    this.hideProgress();
                    this.showResults(data);
                }, 1000);
            } else {
                this.showError(data.error || 'Failed to get results');
            }

        } catch (error) {
            this.showError(`Results error: ${error.message}`);
        }
    }

    showResults(data) {
        const resultsSection = document.getElementById('results-section');
        resultsSection.classList.remove('hidden');

        // Update confidence display
        const bestEstimate = data.best_estimate;
        const overallConfidence = bestEstimate ? Math.round(bestEstimate.confidence * 100) : 0;
        
        this.updateConfidenceDisplay(overallConfidence);

        // Update location info
        if (bestEstimate && bestEstimate.latitude && bestEstimate.longitude) {
            document.getElementById('location-name').textContent = 'Location Found';
            document.getElementById('coordinates').textContent = 
                `${bestEstimate.latitude.toFixed(6)}, ${bestEstimate.longitude.toFixed(6)}`;
            document.getElementById('accuracy').textContent = 
                `Accuracy: ±${bestEstimate.accuracy_meters || 'Unknown'} meters`;

            // Update map
            this.updateMap(bestEstimate);
        } else {
            document.getElementById('location-name').textContent = 'No Location Found';
            document.getElementById('coordinates').textContent = 'No GPS coordinates detected';
            document.getElementById('accuracy').textContent = 'Accuracy: N/A';
        }

        // Show evidence
        this.displayEvidence(data.results || []);

        // Show raw data
        this.displayRawData(data);
    }

    updateConfidenceDisplay(confidence) {
        const percent = document.getElementById('confidence-percent');
        const circle = document.querySelector('.confidence-circle');
        
        percent.textContent = `${confidence}%`;
        
        // Update circle gradient
        const angle = (confidence / 100) * 360;
        circle.style.background = `conic-gradient(var(--success-color) ${angle}deg, var(--light-gray) ${angle}deg)`;
        
        // Update color based on confidence level
        if (confidence >= 80) {
            circle.style.setProperty('--success-color', '#27ae60');
        } else if (confidence >= 60) {
            circle.style.setProperty('--success-color', '#f39c12');
        } else {
            circle.style.setProperty('--success-color', '#e74c3c');
        }
    }

    updateMap(locationData) {
        // Clear existing markers
        this.currentMarkers.forEach(marker => this.map.removeLayer(marker));
        this.currentMarkers = [];

        const lat = locationData.latitude;
        const lon = locationData.longitude;

        // Add main location marker
        const marker = L.marker([lat, lon]).addTo(this.map);
        marker.bindPopup(`
            <b>Detected Location</b><br>
            Confidence: ${Math.round(locationData.confidence * 100)}%<br>
            Methods: ${locationData.methods ? locationData.methods.join(', ') : 'Unknown'}
        `);
        this.currentMarkers.push(marker);

        // Add accuracy circle
        const accuracyRadius = locationData.accuracy_meters || 1000;
        const circle = L.circle([lat, lon], {
            color: '#3498db',
            fillColor: '#3498db',
            fillOpacity: 0.2,
            radius: accuracyRadius
        }).addTo(this.map);
        this.currentMarkers.push(circle);

        // Fit map to location
        this.map.setView([lat, lon], 15);
    }

    displayEvidence(results) {
        const evidenceList = document.getElementById('evidence-list');
        evidenceList.innerHTML = '';

        if (results.length === 0) {
            evidenceList.innerHTML = '<p>No evidence found</p>';
            return;
        }

        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'evidence-item';
            
            if (result.confidence > 0.8) {
                item.classList.add('high-confidence');
            } else if (result.confidence < 0.5) {
                item.classList.add('low-confidence');
            }

            item.innerHTML = `
                <div class="evidence-header">
                    <span class="evidence-type">${this.formatMethod(result.method)}</span>
                    <span class="evidence-confidence">${Math.round(result.confidence * 100)}%</span>
                </div>
                <div class="evidence-description">
                    ${this.getEvidenceDescription(result)}
                </div>
            `;

            evidenceList.appendChild(item);
        });
    }

    displayRawData(data) {
        // EXIF data
        const exifElement = document.getElementById('exif-json');
        if (data.exif_data) {
            exifElement.textContent = JSON.stringify(data.exif_data, null, 2);
        } else {
            exifElement.textContent = 'No EXIF data available';
        }

        // OCR data
        const ocrElement = document.getElementById('ocr-json');
        if (data.exif_data && data.exif_data.ocr_results) {
            ocrElement.textContent = JSON.stringify(data.exif_data.ocr_results, null, 2);
        } else {
            ocrElement.textContent = 'No OCR data available';
        }

        // API data
        const apiElement = document.getElementById('api-json');
        apiElement.textContent = JSON.stringify({
            total_results: data.total_results,
            best_estimate: data.best_estimate,
            results: data.results
        }, null, 2);
    }

    formatMethod(method) {
        const methodNames = {
            'EXIF_GPS': 'GPS Coordinates',
            'vision_api': 'AI Vision Analysis',
            'ocr_geographic_text': 'Text Recognition',
            'landmark_detection': 'Landmark Detection'
        };
        return methodNames[method] || method;
    }

    getEvidenceDescription(result) {
        if (result.latitude && result.longitude) {
            return `Coordinates: ${result.latitude.toFixed(6)}, ${result.longitude.toFixed(6)}`;
        } else if (result.raw_data) {
            try {
                const raw = typeof result.raw_data === 'string' ? 
                    JSON.parse(result.raw_data) : result.raw_data;
                if (raw.text) {
                    return `Text found: "${raw.text}"`;
                }
                if (raw.type) {
                    return `${raw.type}: ${raw.description || 'Geographic indicator detected'}`;
                }
            } catch (e) {
                // Ignore JSON parse errors
            }
        }
        return `Source: ${result.source}`;
    }

    // UI Helper Methods
    showProgress(message, percent) {
        const section = document.getElementById('progress-section');
        const fill = document.getElementById('progress-fill');
        const msg = document.getElementById('progress-message');
        
        section.classList.remove('hidden');
        fill.style.width = `${percent}%`;
        msg.textContent = message;
    }

    hideProgress() {
        document.getElementById('progress-section').classList.add('hidden');
    }

    updateProgressStep(stepId, status) {
        const step = document.getElementById(stepId);
        step.classList.remove('active', 'completed');
        step.classList.add(status);
    }

    showError(message) {
        const errorSection = document.getElementById('error-section');
        const errorMessage = document.getElementById('error-message');
        
        errorMessage.textContent = message;
        errorSection.classList.remove('hidden');
        this.hideProgress();
    }

    hideError() {
        document.getElementById('error-section').classList.add('hidden');
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`${tabName}-data`).classList.add('active');
    }

    centerMapOnResults() {
        if (this.currentMarkers.length > 0) {
            const group = new L.featureGroup(this.currentMarkers);
            this.map.fitBounds(group.getBounds());
        }
    }

    async generateReport(format = 'markdown') {
        if (!this.currentImageId) return;

        try {
            this.showProgress('Generating comprehensive report...', 90);
            
            const response = await fetch(`${this.apiBase}/report/${this.currentImageId}?format=json`);
            const data = await response.json();
            
            if (data.success) {
                this.displayMarkdownReport(data.markdown_report);
                this.hideProgress();
            } else {
                throw new Error(data.error || 'Failed to generate report');
            }
        } catch (error) {
            this.showError(`Report generation failed: ${error.message}`);
        }
    }

    async downloadReport(format = 'markdown') {
        if (!this.currentImageId) return;

        try {
            this.showProgress('Preparing report download...', 95);
            
            const response = await fetch(`${this.apiBase}/report/${this.currentImageId}?format=${format}`);
            
            if (!response.ok) {
                throw new Error('Failed to generate report');
            }
            
            const reportContent = await response.text();
            const blob = new Blob([reportContent], { 
                type: format === 'html' ? 'text/html' : 'text/markdown' 
            });
            
            const filename = `osint-report-${this.currentImageId}.${format === 'html' ? 'html' : 'md'}`;
            this.downloadFile(blob, filename);
            this.hideProgress();
            
        } catch (error) {
            this.showError(`Report download failed: ${error.message}`);
        }
    }

    async viewHTMLReport() {
        if (!this.currentImageId) return;

        try {
            const url = `${this.apiBase}/report/${this.currentImageId}?format=html`;
            window.open(url, '_blank', 'width=800,height=600,scrollbars=yes,resizable=yes');
        } catch (error) {
            this.showError(`Failed to open HTML report: ${error.message}`);
        }
    }

    displayMarkdownReport(markdownContent) {
        // Create or update report display area
        let reportSection = document.getElementById('report-section');
        if (!reportSection) {
            reportSection = document.createElement('div');
            reportSection.id = 'report-section';
            reportSection.className = 'card mt-4';
            document.querySelector('.results-container').appendChild(reportSection);
        }

        // Convert markdown to HTML (basic implementation)
        const htmlContent = this.markdownToHTML(markdownContent);
        
        reportSection.innerHTML = `
            <div class="card-header">
                <h3>📋 OSINT Analysis Report</h3>
                <div class="report-actions">
                    <button class="btn btn-secondary" onclick="app.downloadReport('markdown')">
                        📄 Download Markdown
                    </button>
                    <button class="btn btn-secondary" onclick="app.downloadReport('html')">
                        🌐 Download HTML
                    </button>
                    <button class="btn btn-primary" onclick="app.viewHTMLReport()">
                        👀 View in New Tab
                    </button>
                </div>
            </div>
            <div class="card-body">
                <div class="report-content">${htmlContent}</div>
            </div>
        `;

        // Scroll to report
        reportSection.scrollIntoView({ behavior: 'smooth' });
    }

    markdownToHTML(markdown) {
        // Basic markdown to HTML conversion
        let html = markdown
            // Headers
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            
            // Bold and italic
            .replace(/\*\*\*(.*)\*\*\*/gim, '<strong><em>$1</em></strong>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            
            // Code blocks and inline code
            .replace(/```([^`]+)```/gim, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/gim, '<code>$1</code>')
            
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank">$1</a>')
            
            // Lists
            .replace(/^\- (.*$)/gim, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>')
            
            // Line breaks
            .replace(/\n/gim, '<br>');

        return html;
    }

    exportResults(format) {
        if (!this.currentImageId) return;

        if (format === 'json') {
            // Export JSON data
            fetch(`${this.apiBase}/results/${this.currentImageId}`)
                .then(response => response.json())
                .then(data => {
                    const blob = new Blob([JSON.stringify(data, null, 2)], 
                        { type: 'application/json' });
                    this.downloadFile(blob, 'geolocation-results.json');
                });
        } else if (format === 'report') {
            this.generateReport('markdown');
        }
    }

    downloadFile(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    resetInterface() {
        // Reset all UI elements
        this.currentImageId = null;
        document.getElementById('controls-section').classList.add('hidden');
        document.getElementById('progress-section').classList.add('hidden');
        document.getElementById('results-section').classList.add('hidden');
        document.getElementById('error-section').classList.add('hidden');
        document.getElementById('image-preview').classList.add('hidden');
        
        // Clear file input
        document.getElementById('file-input').value = '';
        
        // Reset map
        this.currentMarkers.forEach(marker => this.map.removeLayer(marker));
        this.currentMarkers = [];
        this.map.setView([20, 0], 2);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GeolocationAnalyzer();
});