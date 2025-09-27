// Custom JavaScript for Job Scraper Dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitBtn.disabled = true;
                
                // Re-enable after 5 seconds (fallback)
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });

    // Add smooth scrolling to anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
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

    // Add progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease';
            bar.style.width = width;
        }, 500);
    });

    // Add counter animation to stats
    const counters = document.querySelectorAll('.stat-item h3');
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/,/g, ''));
        let current = 0;
        const increment = target / 50;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.floor(current).toLocaleString();
        }, 30);
    });

    // Add search functionality
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const items = document.querySelectorAll('.searchable-item');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                    item.classList.add('fade-in');
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // Add confirmation dialogs for destructive actions
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Add auto-refresh for scrape status
    const scrapeStatusElements = document.querySelectorAll('[data-scrape-id]');
    scrapeStatusElements.forEach(element => {
        const scrapeId = element.dataset.scrapeId;
        const interval = setInterval(() => {
            fetch(`/dashboard/scrape/${scrapeId}/status/`)
                .then(response => response.json())
                .then(data => {
                    if (data.is_complete) {
                        clearInterval(interval);
                        location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error checking scrape status:', error);
                });
        }, 5000);
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + N for new scrape
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const newScrapeBtn = document.querySelector('a[href*="scrape-start"]');
            if (newScrapeBtn) {
                newScrapeBtn.click();
            }
        }
    });

    // Add notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Add copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const text = this.dataset.copyText;
            navigator.clipboard.writeText(text).then(() => {
                showNotification('Copied to clipboard!', 'success');
            }).catch(() => {
                showNotification('Failed to copy to clipboard', 'danger');
            });
        });
    });

    // Add filter toggle functionality
    const filterToggles = document.querySelectorAll('.filter-toggle');
    filterToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const filterPanel = document.querySelector(this.dataset.target);
            if (filterPanel) {
                filterPanel.classList.toggle('show');
            }
        });
    });

    // Add data export functionality
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const format = this.dataset.format;
            const url = this.dataset.url;
            
            if (format === 'csv') {
                window.location.href = url + '?format=csv';
            } else if (format === 'excel') {
                window.location.href = url + '?format=excel';
            } else if (format === 'google-sheets') {
                window.location.href = url + '?format=google-sheets';
            }
        });
    });

    // Add real-time search suggestions
    const searchInputs = document.querySelectorAll('input[name="q"]');
    searchInputs.forEach(input => {
        let timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const query = this.value;
                if (query.length > 2) {
                    // Implement search suggestions here
                    console.log('Searching for:', query);
                }
            }, 300);
        });
    });

    // Add infinite scroll for job listings
    const jobListings = document.querySelector('.job-listings');
    if (jobListings) {
        let page = 1;
        let loading = false;
        
        window.addEventListener('scroll', function() {
            if (loading) return;
            
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
                loading = true;
                page++;
                
                fetch(`/dashboard/jobs/?page=${page}`)
                    .then(response => response.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const newJobs = doc.querySelectorAll('.job-item');
                        
                        newJobs.forEach(job => {
                            jobListings.appendChild(job);
                        });
                        
                        loading = false;
                    })
                    .catch(error => {
                        console.error('Error loading more jobs:', error);
                        loading = false;
                    });
            }
        });
    }

    // Add drag and drop for file uploads
    const dropZones = document.querySelectorAll('.drop-zone');
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        zone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                // Handle file upload
                console.log('Files dropped:', files);
            }
        });
    });

    // Add theme toggle
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
        });
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }

    // Add print functionality
    const printButtons = document.querySelectorAll('.print-btn');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });

    // Add fullscreen functionality
    const fullscreenButtons = document.querySelectorAll('.fullscreen-btn');
    fullscreenButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        });
    });

    // Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        const focusableElements = document.querySelectorAll('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
        const currentIndex = Array.from(focusableElements).indexOf(document.activeElement);
        
        if (e.key === 'Tab') {
            // Let default tab behavior work
            return;
        }
        
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
            e.preventDefault();
            const nextIndex = (currentIndex + 1) % focusableElements.length;
            focusableElements[nextIndex].focus();
        }
        
        if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
            e.preventDefault();
            const prevIndex = currentIndex === 0 ? focusableElements.length - 1 : currentIndex - 1;
            focusableElements[prevIndex].focus();
        }
    });

    // Add accessibility improvements
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        if (!img.alt) {
            img.alt = 'Image';
        }
    });

    // Add focus indicators
    const focusableElements = document.querySelectorAll('a, button, input, select, textarea');
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid #667eea';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });

    // Add performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log('Page load time:', loadTime + 'ms');
        });
    }

    // Add error handling
    window.addEventListener('error', function(e) {
        console.error('JavaScript error:', e.error);
        showNotification('An error occurred. Please refresh the page.', 'danger');
    });

    // Add offline detection
    window.addEventListener('online', function() {
        showNotification('Connection restored!', 'success');
    });
    
    window.addEventListener('offline', function() {
        showNotification('You are offline. Some features may not work.', 'warning');
    });
});
