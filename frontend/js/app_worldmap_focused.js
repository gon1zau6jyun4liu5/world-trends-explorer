/**
 * World Map Focused Application for World Trends Explorer v1.0.2
 * Primary interaction: Click countries on world map to see trends
 */

class WorldMapFocusedApp {
    constructor() {
        this.api = window.trendsAPI;
        this.chart = null;
        this.worldMap = null;
        this.currentData = null;
        this.selectedCountry = null;
        this.isLoading = false;
        
        // Available countries that have trending data
        this.availableCountries = new Set([
            'US', 'GB', 'DE', 'FR', 'IT', 'ES', 'CA', 'AU', 
            'JP', 'KR', 'IN', 'BR', 'MX', 'RU', 'CN', 'NL',
            'SE', 'NO', 'DK', 'FI', 'BE', 'CH', 'AT', 'IE',
            'PT', 'GR', 'PL', 'CZ', 'HU', 'SK', 'SI', 'HR',
            'BG', 'RO', 'LT', 'LV', 'EE', 'MT', 'CY', 'LU'
        ]);
        
        // DOM elements
        this.elements = {
            countryInfoPanel: document.getElementById('countryInfoPanel'),
            countryTitle: document.getElementById('countryTitle'),
            countrySearchInput: document.getElementById('countrySearchInput'),
            countrySearchBtn: document.getElementById('countrySearchBtn'),
            closeCountryPanel: document.getElementById('closeCountryPanel'),
            trendingCount: document.getElementById('trendingCount'),
            dataAvailable: document.getElementById('dataAvailable'),
            countryCode: document.getElementById('countryCode'),
            countryTrendingGrid: document.getElementById('countryTrendingGrid'),
            resultsSection: document.getElementById('resultsSection'),
            resultsTitle: document.getElementById('resultsTitle'),
            searchStats: document.getElementById('searchStats'),
            regionalTable: document.getElementById('regionalTable'),
            topQueries: document.getElementById('topQueries'),
            risingQueries: document.getElementById('risingQueries'),
            loadingIndicator: document.getElementById('loadingIndicator'),
            errorMessage: document.getElementById('errorMessage'),
            errorText: document.getElementById('errorText')
        };
        
        this.init();
    }

    async init() {
        console.log('🌍 Initializing World Map Focused Explorer v1.0.2...');
        
        try {
            // Initialize components
            this.chart = new TrendsChart('trendsChart');
            this.worldMap = new WorldMap('worldMap');
            
            // Set available countries for map visualization
            if (this.worldMap) {
                this.worldMap.setAvailableCountries(this.availableCountries);
            }
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Check API health
            await this.checkAPIHealth();
            
            console.log('✅ World Map Focused Explorer initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize app:', error);
            this.showError('Failed to initialize application');
        }
    }

    setupEventListeners() {
        // Country search functionality
        if (this.elements.countrySearchBtn) {
            this.elements.countrySearchBtn.addEventListener('click', () => this.handleCountrySearch());
        }
        
        if (this.elements.countrySearchInput) {
            this.elements.countrySearchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleCountrySearch();
            });
        }
        
        // Close country panel
        if (this.elements.closeCountryPanel) {
            this.elements.closeCountryPanel.addEventListener('click', () => {
                this.closeCountryPanel();
            });
        }
        
        // Country selection from map
        document.addEventListener('countrySelected', (e) => {
            this.handleCountrySelection(e.detail);
        });
        
        // Window resize
        window.addEventListener('resize', this.debounce(() => {
            if (this.chart) this.chart.resize();
            if (this.worldMap) this.worldMap.resize();
        }, 250));
    }

    async handleCountrySelection(countryDetail) {
        console.log('🌍 Country selected:', countryDetail);
        
        // Check if country has data available
        if (!this.availableCountries.has(countryDetail.code)) {
            this.showError(`No data available for ${countryDetail.name}. Please select a different country.`);
            return;
        }
        
        this.selectedCountry = {
            code: countryDetail.code,
            name: countryDetail.name
        };
        
        // Show country info panel
        this.showCountryPanel(countryDetail);
        
        // Load trending searches for selected country
        await this.loadCountryTrendingSearches(countryDetail.code);
    }

    showCountryPanel(countryDetail) {
        // Update country panel header
        if (this.elements.countryTitle) {
            this.elements.countryTitle.textContent = `${this.getCountryFlag(countryDetail.code)} ${countryDetail.name} Trends`;
        }
        
        // Update stats
        if (this.elements.countryCode) {
            this.elements.countryCode.textContent = countryDetail.code;
        }
        
        if (this.elements.dataAvailable) {
            this.elements.dataAvailable.textContent = 'Loading...';
        }
        
        if (this.elements.trendingCount) {
            this.elements.trendingCount.textContent = 'Loading...';
        }
        
        // Show panel
        if (this.elements.countryInfoPanel) {
            this.elements.countryInfoPanel.style.display = 'block';
            this.elements.countryInfoPanel.classList.add('fade-in');
            
            // Scroll to panel
            this.elements.countryInfoPanel.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
    }

    closeCountryPanel() {
        if (this.elements.countryInfoPanel) {
            this.elements.countryInfoPanel.style.display = 'none';
        }
        
        if (this.elements.resultsSection) {
            this.elements.resultsSection.style.display = 'none';
        }
        
        // Reset map
        if (this.worldMap) {
            this.worldMap.reset();
        }
        
        this.selectedCountry = null;
        this.currentData = null;
    }

    async loadCountryTrendingSearches(countryCode) {
        try {
            console.log(`🔥 Loading trending searches for: ${countryCode}`);
            
            this.setLoading(true);
            
            const data = await this.api.getTrendingSearches(countryCode);
            this.displayCountryTrendingSearches(data, countryCode);
            
            // Update stats
            if (this.elements.trendingCount && data.trending_searches) {
                this.elements.trendingCount.textContent = data.trending_searches.length;
            }
            
            if (this.elements.dataAvailable) {
                this.elements.dataAvailable.textContent = 'Available';
            }
            
        } catch (error) {
            console.error('Failed to load country trending searches:', error);
            this.displayCountryTrendingError();
        } finally {
            this.setLoading(false);
        }
    }

    displayCountryTrendingSearches(data, countryCode) {
        if (!this.elements.countryTrendingGrid) return;
        
        this.elements.countryTrendingGrid.innerHTML = '';
        
        if (!data || !data.trending_searches || !Array.isArray(data.trending_searches)) {
            this.displayCountryTrendingError();
            return;
        }
        
        data.trending_searches.slice(0, 12).forEach(item => {
            const element = document.createElement('div');
            element.className = 'trending-item';
            element.innerHTML = `
                <div class="trending-rank">#${item.rank}</div>
                <div class="trending-query">${this.truncateText(item.query, 30)}</div>
            `;
            
            element.addEventListener('click', () => {
                this.searchInCountry(item.query, countryCode);
            });
            
            this.elements.countryTrendingGrid.appendChild(element);
        });
    }

    displayCountryTrendingError() {
        if (!this.elements.countryTrendingGrid) return;
        
        this.elements.countryTrendingGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: #666; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <div>Failed to load trending searches</div>
                <button onclick="app.loadCountryTrendingSearches('${this.selectedCountry?.code || 'US'}')" 
                        style="margin-top: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    Retry
                </button>
            </div>
        `;
    }

    async handleCountrySearch() {
        const keyword = this.elements.countrySearchInput?.value.trim();
        
        if (!keyword) {
            this.showError('Please enter a keyword to search');
            return;
        }
        
        if (!this.selectedCountry) {
            this.showError('Please select a country first');
            return;
        }
        
        await this.searchInCountry(keyword, this.selectedCountry.code);
    }

    async searchInCountry(keyword, countryCode) {
        if (this.isLoading) {
            console.log('Search already in progress...');
            return;
        }
        
        try {
            this.setLoading(true);
            this.hideError();
            
            console.log(`🔍 Searching trends for: "${keyword}" in ${countryCode}`);
            
            const data = await this.api.searchTrends(keyword, countryCode);
            
            if (this.isValidTrendsData(data)) {
                this.currentData = data;
                this.displaySearchResults(data);
                
                // Update world map with search results
                if (this.worldMap) {
                    this.worldMap.updateData(data);
                }
            } else {
                throw new Error('Invalid data received from API');
            }
            
        } catch (error) {
            console.error('Search failed:', error);
            this.showError(error.message || 'Failed to search trends');
        } finally {
            this.setLoading(false);
        }
    }

    displaySearchResults(data) {
        // Update result header
        if (this.elements.resultsTitle) {
            this.elements.resultsTitle.textContent = `"${data.keyword}" in ${this.selectedCountry?.name || data.geo}`;
        }
        
        if (this.elements.searchStats) {
            this.elements.searchStats.textContent = 
                `Updated: ${this.formatRelativeTime(data.timestamp)} | Country: ${this.selectedCountry?.name || data.geo}`;
        }
        
        // Show results section
        if (this.elements.resultsSection) {
            this.elements.resultsSection.style.display = 'block';
            this.elements.resultsSection.classList.add('fade-in');
        }
        
        // Update chart
        if (this.chart) {
            this.chart.updateChart(data);
        }
        
        // Update regional data
        this.displayRegionalData(data.interest_by_region, data.keyword);
        
        // Update related queries
        this.displayRelatedQueries(data.related_queries);
        
        // Scroll to results
        if (this.elements.resultsSection) {
            this.elements.resultsSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
    }

    displayRegionalData(regionalData, keyword) {
        if (!this.elements.regionalTable) return;
        
        this.elements.regionalTable.innerHTML = '';
        
        if (!regionalData || !Array.isArray(regionalData) || regionalData.length === 0) {
            this.elements.regionalTable.innerHTML = 
                '<div style="text-align: center; color: #666; padding: 2rem;">No regional data available</div>';
            return;
        }
        
        // Sort and filter data
        const filteredData = regionalData.filter(item => (item.value || 0) >= 1);
        const sortedData = filteredData.sort((a, b) => (b.value || 0) - (a.value || 0)).slice(0, 15);
        
        sortedData.forEach((item, index) => {
            const element = document.createElement('div');
            element.className = 'regional-item';
            element.innerHTML = `
                <div class="regional-country">
                    <span style="margin-right: 0.5rem;">${this.getCountryFlag(item.geoCode)}</span>
                    ${item.geoName}
                </div>
                <div class="regional-value">${item.value}</div>
            `;
            
            // Add click handler to highlight on map
            element.addEventListener('click', () => {
                if (this.worldMap && item.geoCode) {
                    this.worldMap.highlightCountry(item.geoCode);
                }
            });
            
            this.elements.regionalTable.appendChild(element);
        });
    }

    displayRelatedQueries(relatedQueries) {
        // Clear existing content
        if (this.elements.topQueries) {
            this.elements.topQueries.innerHTML = '';
        }
        if (this.elements.risingQueries) {
            this.elements.risingQueries.innerHTML = '';
        }
        
        if (!relatedQueries) {
            if (this.elements.topQueries) {
                this.elements.topQueries.innerHTML = '<li style="color: #666;">No data available</li>';
            }
            if (this.elements.risingQueries) {
                this.elements.risingQueries.innerHTML = '<li style="color: #666;">No data available</li>';
            }
            return;
        }
        
        // Display top queries
        if (relatedQueries.top && Array.isArray(relatedQueries.top) && relatedQueries.top.length > 0) {
            relatedQueries.top.slice(0, 10).forEach(query => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="query-text">${this.truncateText(query.query || query, 40)}</span>
                    <span class="query-value">${query.value || ''}</span>
                `;
                li.addEventListener('click', () => this.searchInCountry(query.query || query, this.selectedCountry?.code));
                if (this.elements.topQueries) {
                    this.elements.topQueries.appendChild(li);
                }
            });
        } else if (this.elements.topQueries) {
            this.elements.topQueries.innerHTML = '<li style="color: #666;">No top queries available</li>';
        }
        
        // Display rising queries
        if (relatedQueries.rising && Array.isArray(relatedQueries.rising) && relatedQueries.rising.length > 0) {
            relatedQueries.rising.slice(0, 10).forEach(query => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="query-text">${this.truncateText(query.query || query, 40)}</span>
                    <span class="query-value">${query.value || '🔥'}</span>
                `;
                li.addEventListener('click', () => this.searchInCountry(query.query || query, this.selectedCountry?.code));
                if (this.elements.risingQueries) {
                    this.elements.risingQueries.appendChild(li);
                }
            });
        } else if (this.elements.risingQueries) {
            this.elements.risingQueries.innerHTML = '<li style="color: #666;">No rising queries available</li>';
        }
    }

    async checkAPIHealth() {
        try {
            const health = await this.api.healthCheck();
            if (health) {
                console.log('✅ API is healthy:', health);
            } else {
                console.warn('⚠️ API health check failed');
            }
        } catch (error) {
            console.error('❌ API health check error:', error);
            this.showError('Unable to connect to trends API. Please check your connection.');
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        
        if (loading) {
            if (this.elements.loadingIndicator) {
                this.elements.loadingIndicator.style.display = 'block';
            }
            
            if (this.chart) {
                this.chart.showLoading();
            }
        } else {
            if (this.elements.loadingIndicator) {
                this.elements.loadingIndicator.style.display = 'none';
            }
        }
    }

    showError(message) {
        if (this.elements.errorText) {
            this.elements.errorText.textContent = message;
        }
        if (this.elements.errorMessage) {
            this.elements.errorMessage.style.display = 'flex';
        }
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        if (this.elements.errorMessage) {
            this.elements.errorMessage.style.display = 'none';
        }
    }

    // Utility methods
    getCountryFlag(countryCode) {
        const flags = {
            'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷',
            'IT': '🇮🇹', 'ES': '🇪🇸', 'CA': '🇨🇦', 'AU': '🇦🇺',
            'JP': '🇯🇵', 'KR': '🇰🇷', 'IN': '🇮🇳', 'BR': '🇧🇷',
            'MX': '🇲🇽', 'RU': '🇷🇺', 'CN': '🇨🇳', 'NL': '🇳🇱',
            'SE': '🇸🇪', 'NO': '🇳🇴', 'DK': '🇩🇰', 'FI': '🇫🇮',
            'BE': '🇧🇪', 'CH': '🇨🇭', 'AT': '🇦🇹', 'IE': '🇮🇪',
            'PT': '🇵🇹', 'GR': '🇬🇷', 'PL': '🇵🇱', 'CZ': '🇨🇿'
        };
        return flags[countryCode] || '🌍';
    }

    formatRelativeTime(dateString) {
        if (!dateString) return 'Unknown';
        
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);

            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins} minutes ago`;
            if (diffHours < 24) return `${diffHours} hours ago`;
            
            return date.toLocaleDateString('en-US');
        } catch (error) {
            return dateString;
        }
    }

    truncateText(text, maxLength = 50) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }

    isValidTrendsData(data) {
        return data && 
               typeof data === 'object' && 
               data.keyword && 
               (Array.isArray(data.interest_over_time) || 
                Array.isArray(data.interest_by_region));
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WorldMapFocusedApp();
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (window.app) {
        window.app.showError('An unexpected error occurred');
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    if (window.app) {
        window.app.showError('An unexpected error occurred');
    }
});