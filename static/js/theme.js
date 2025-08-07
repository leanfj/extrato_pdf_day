// Theme and UI enhancements for PDF Extractor

document.addEventListener('DOMContentLoaded', function() {
    
    // Enhanced file upload with drag and drop
    const fileInput = document.getElementById('file');
    const uploadForm = document.getElementById('uploadForm');
    
    if (fileInput && uploadForm) {
        const uploadArea = uploadForm.querySelector('.card-body');
        
        // Add drag and drop styling class
        uploadArea.classList.add('file-upload-area');
        
        // Drag and drop events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight(e) {
            uploadArea.classList.add('dragover');
        }
        
        function unhighlight(e) {
            uploadArea.classList.remove('dragover');
        }
        
        // Handle dropped files
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        }
    }
    
    // Theme-aware chart colors
    window.getChartColors = function() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        
        return {
            primary: isDark ? '#4dabf7' : '#0d6efd',
            success: isDark ? '#51cf66' : '#198754',
            danger: isDark ? '#ff6b6b' : '#dc3545',
            warning: isDark ? '#ffd43b' : '#ffc107',
            info: isDark ? '#74c0fc' : '#0dcaf0',
            text: isDark ? '#ffffff' : '#212529',
            background: isDark ? '#2d2d2d' : '#ffffff',
            grid: isDark ? '#495057' : '#dee2e6'
        };
    };
    
    // Update charts when theme changes
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            setTimeout(() => {
                // Trigger chart updates if they exist
                if (window.Chart) {
                    Chart.helpers.each(Chart.instances, function(instance) {
                        instance.update();
                    });
                }
            }, 300);
        });
    }
    
    // Enhanced tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Enhanced loading states
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processando...';
                submitBtn.disabled = true;
                
                // Re-enable after timeout (fallback)
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 30000);
            }
        });
    });
    
    // Theme persistence
    function saveThemePreference(theme) {
        localStorage.setItem('theme', theme);
        localStorage.setItem('theme-manual', 'true');
    }
    
    // Expose theme functions globally
    window.themeUtils = {
        saveThemePreference,
        getChartColors: window.getChartColors
    };
});

// Utility functions for theme-aware components
window.updateChartsForTheme = function() {
    if (window.Chart) {
        Chart.helpers.each(Chart.instances, function(instance) {
            const colors = window.getChartColors();
            
            // Update chart colors based on theme
            if (instance.config.type === 'doughnut' || instance.config.type === 'pie') {
                instance.config.data.datasets.forEach(dataset => {
                    if (dataset.backgroundColor) {
                        dataset.backgroundColor = [colors.success, colors.danger, colors.warning, colors.info];
                    }
                });
            }
            
            if (instance.config.type === 'bar' || instance.config.type === 'line') {
                instance.config.data.datasets.forEach(dataset => {
                    dataset.backgroundColor = colors.primary;
                    dataset.borderColor = colors.primary;
                });
                
                // Update scales
                if (instance.config.options.scales) {
                    if (instance.config.options.scales.x) {
                        instance.config.options.scales.x.grid = {
                            color: colors.grid
                        };
                        instance.config.options.scales.x.ticks = {
                            color: colors.text
                        };
                    }
                    if (instance.config.options.scales.y) {
                        instance.config.options.scales.y.grid = {
                            color: colors.grid
                        };
                        instance.config.options.scales.y.ticks = {
                            color: colors.text
                        };
                    }
                }
            }
            
            instance.update('none');
        });
    }
};
