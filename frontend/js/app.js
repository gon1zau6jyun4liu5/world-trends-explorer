/**
 * Main Application JavaScript for World Trends Explorer v1.0.4
 * Map-Only Interface - Country selection ONLY through map clicks
 */

class WorldTrendsApp {
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
        
        // DOM elements - Map-only interface
        this.elements = {
            // Country info panel
            countryInfoPanel: document.getElementById('countryInfoPanel'),
            countryTitle: document.getElementById('countryTitle'),
            closeCountryPanel: document.getElementById('closeCountryPanel'),
            trendingCount: document.getElementById('trendingCount'),
            dataAvailable: document.getElementById('dataAvailable'),
            countryCode: document.getElementById('countryCode'),
            countryTrendingGrid: document.getElementById('countryTrendingGrid'),
            countrySearchInput: document.getElementById('countrySearchInput'),
            countrySearchBtn: document.getElementById('countrySearchBtn'),
            
            // Search results
            resultsSection: document.getElementById('resultsSection'),
            resultsTitle: document.getElementById('resultsTitle'),
            searchKeyword: document.getElementById('searchKeyword'),
            searchStats: document.getElementById('searchStats'),
            regionalTable: document.getElementById('regionalTable'),
            topQueries: document.getElementById('topQueries'),
            risingQueries: document.getElementById('risingQueries'),
            
            // UI elements
            loadingIndicator: document.getElementById('loadingIndicator'),
            errorMessage: document.getElementById('errorMessage'),
            errorText: document.getElementById('errorText'),
            resetMapBtn: document.getElementById('resetMapBtn')
        };
        
        this.init();
    }

    async init() {
        console.log('🌍 Initializing World Trends Explorer v1.0.4 - Map-Only Interface...');
        
        try {
            // Initialize components
            this.chart = new TrendsChart('trendsChart');
            this.worldMap = new WorldMap('worldMap');
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Check API health
            await this.checkAPIHealth();
            
            console.log('✅ World Trends Explorer v1.0.4 initialized successfully');
            console.log('🗺️ Click on any blue country in the map to start exploring!');
        } catch (error) {
            console.error('❌ Failed to initialize app:', error);
            this.showError('Failed to initialize application');
        }
    }

    setupEventListeners() {
        console.log('🔧 Setting up event listeners for map-only interface...');
        
        // Country selection from map - PRIMARY INTERACTION
        document.addEventListener('countrySelected', (e) => {
            this.handleCountrySelection(e.detail);
        });
        
        // Close country panel
        if (this.elements.closeCountryPanel) {
            this.elements.closeCountryPanel.addEventListener('click', () => {
                this.hideCountryPanel();
            });
        }
        
        // Country search within selected country
        if (this.elements.countrySearchBtn) {
            this.elements.countrySearchBtn.addEventListener('click', () => {
                this.handleCountrySearch();
            });
        }
        
        if (this.elements.countrySearchInput) {
            this.elements.countrySearchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleCountrySearch();
            });
        }
        
        // Map reset button
        if (this.elements.resetMapBtn) {
            this.elements.resetMapBtn.addEventListener('click', () => {
                this.resetMap();
            });
        }
        
        // Window resize
        window.addEventListener('resize', TrendsUtils.debounce(() => {
            if (this.chart) this.chart.resize();
            if (this.worldMap) this.worldMap.resize();
        }, 250));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'k':
                        e.preventDefault();
                        if (this.elements.countrySearchInput && this.selectedCountry) {
                            this.elements.countrySearchInput.focus();
                        }
                        break;
                    case 'r':
                        e.preventDefault();
                        this.handleRefresh();
                        break;
                }
            }
            
            // Escape key handling
            if (e.key === 'Escape') {
                this.hideCountryPanel();
                this.hideSearchResults();
            }
        });
        
        console.log('✅ Event listeners set up for v1.0.4');
    }

    async handleCountrySelection(countryDetail) {
        console.log('🌍 Country selected:', countryDetail);
        
        if (!countryDetail || !countryDetail.code) {
            console.warn('Invalid country selection');
            return;
        }
        
        // Check if country has data available
        if (!this.availableCountries.has(countryDetail.code)) {
            this.showError(`No data available for ${countryDetail.name}. Please select a blue country on the map.`);
            return;
        }
        
        this.selectedCountry = {
            code: countryDetail.code,
            name: countryDetail.name
        };
        
        // Show country info panel
        this.showCountryPanel(countryDetail);
        
        // Load country-specific trending data
        await this.loadCountryTrending(countryDetail.code);
    }

    async showCountryPanel(countryDetail) {
        const flag = TrendsUtils.getCountryFlag(countryDetail.code);
        
        // Update panel title
        this.elements.countryTitle.innerHTML = `${flag} ${countryDetail.name}`;
        this.elements.countryCode.textContent = countryDetail.code;
        
        // Show panel with animation
        this.elements.countryInfoPanel.style.display = 'block';
        this.elements.countryInfoPanel.classList.add('fade-in');
        
        // Scroll to panel
        setTimeout(() => {
            this.elements.countryInfoPanel.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }, 100);
        
        console.log(`📱 Country panel shown for ${countryDetail.name}`);
    }

    hideCountryPanel() {
        this.elements.countryInfoPanel.style.display = 'none';
        this.selectedCountry = null;
        
        // Reset map highlighting
        if (this.worldMap) {
            this.worldMap.reset();
        }
        
        console.log('📱 Country panel hidden');
    }

    resetMap() {
        this.hideCountryPanel();
        this.hideSearchResults();
        
        if (this.worldMap) {
            this.worldMap.reset();
        }
        
        console.log('🔄 Map reset to initial state');
    }

    async loadCountryTrending(countryCode) {
        try {
            this.setCountryLoading(true);
            
            console.log(`🔥 Loading trending searches for: ${countryCode}`);
            
            const data = await this.api.getTrendingSearches(countryCode);
            this.displayCountryTrending(data);
            
        } catch (error) {
            console.error('Failed to load country trending:', error);
            this.displayCountryTrendingError();
        } finally {
            this.setCountryLoading(false);
        }
    }

    displayCountryTrending(data) {
        if (!this.elements.countryTrendingGrid) return;
        
        this.elements.countryTrendingGrid.innerHTML = '';
        
        if (!data || !data.trending_searches || !Array.isArray(data.trending_searches)) {
            this.displayCountryTrendingError();
            return;
        }
        
        // Update stats
        this.elements.trendingCount.textContent = data.trending_searches.length;
        this.elements.dataAvailable.textContent = 'Available';
        
        // Display trending topics
        data.trending_searches.slice(0, 8).forEach(item => {
            const element = document.createElement('div');
            element.className = 'trending-item';
            element.innerHTML = `
                <div class="trending-rank">#${item.rank}</div>
                <div class="trending-query">${TrendsUtils.truncateText(item.query, 25)}</div>
            `;
            
            element.addEventListener('click', () => {
                this.searchInCountry(item.query);
            });
            
            this.elements.countryTrendingGrid.appendChild(element);
        });
        
        console.log(`✅ Displayed ${data.trending_searches.length} trending topics`);
    }

    displayCountryTrendingError() {
        if (!this.elements.countryTrendingGrid) return;
        
        this.elements.trendingCount.textContent = '0';
        this.elements.dataAvailable.textContent = 'Unavailable';
        
        this.elements.countryTrendingGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: #666; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <div>No trending data available for this country</div>
                <button onclick="app.loadCountryTrending('${this.selectedCountry?.code || 'US'}')" 
                        style="margin-top: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    Retry
                </button>
            </div>
        `;
    }

    setCountryLoading(loading) {
        if (!this.elements.countryTrendingGrid) return;
        
        if (loading) {
            this.elements.countryTrendingGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; color: #667eea; padding: 2rem;">
                    <div class="spinner" style="width: 40px; height: 40px; margin: 0 auto 1rem;"></div>
                    <div>Loading trending topics...</div>
                </div>
            `;
        }
    }

    async handleCountrySearch() {
        const keyword = this.elements.countrySearchInput.value.trim();
        
        if (!keyword) {
            this.showError('Please enter a keyword to search');
            return;
        }
        
        if (!this.selectedCountry) {
            this.showError('Please select a country from the map first');
            return;
        }
        
        this.searchInCountry(keyword);
    }

    async searchInCountry(keyword) {
        if (!this.selectedCountry) {
            this.showError('No country selected. Click on a blue country in the map first.');
            return;
        }
        
        try {
            this.setLoading(true);
            this.hideError();
            
            console.log(`🔍 Searching "${keyword}" in ${this.selectedCountry.name}`);
            
            // Search trends for specific country
            const data = await this.api.searchTrends(keyword, this.selectedCountry.code);
            
            if (TrendsUtils.isValidTrendsData(data)) {
                this.currentData = data;
                this.displaySearchResults(data);
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
        if (!this.elements.resultsSection) {
            console.warn('Search results elements not found');
            return;
        }
        
        // Update result header
        if (this.elements.searchKeyword) {
            this.elements.searchKeyword.textContent = data.keyword;
        }
        if (this.elements.searchStats) {
            this.elements.searchStats.textContent = 
                `Updated: ${TrendsUtils.formatRelativeTime(data.timestamp)} | Country: ${this.selectedCountry?.name || data.geo}`;
        }
        
        // Show results section
        this.elements.resultsSection.style.display = 'block';
        this.elements.resultsSection.classList.add('fade-in');
        
        // Update chart
        if (this.chart) {
            this.chart.updateChart(data);
        }
        
        // Update world map with search results
        if (this.worldMap) {
            this.worldMap.updateData(data);
        }
        
        // Update regional data
        this.displayRegionalData(data.interest_by_region, data.keyword);
        
        // Update related queries
        this.displayRelatedQueries(data.related_queries);
        
        // Scroll to results
        setTimeout(() => {
            this.elements.resultsSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);
        
        console.log(`✅ Search results displayed for "${data.keyword}"`);
    }

    hideSearchResults() {
        if (this.elements.resultsSection) {
            this.elements.resultsSection.style.display = 'none';
        }
        this.currentData = null;
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
        const filteredData = TrendsUtils.filterByMinValue(regionalData, 'value', 1);
        const sortedData = TrendsUtils.sortByValue(filteredData, 'value', true).slice(0, 15);
        
        sortedData.forEach((item, index) => {
            const element = document.createElement('div');
            element.className = 'regional-item';
            element.innerHTML = `
                <div class="regional-country">
                    <span style="margin-right: 0.5rem;">${TrendsUtils.getCountryFlag(item.geoCode)}</span>
                    ${item.geoName}
                </div>
                <div class="regional-value">${item.value}</div>
            `;
            
            // Add click handler to select country if available
            element.addEventListener('click', () => {
                if (item.geoCode && this.availableCountries.has(item.geoCode)) {
                    this.handleCountrySelection({
                        code: item.geoCode,
                        name: item.geoName
                    });
                } else {
                    this.showError(`${item.geoName} data not available for exploration. Try clicking blue countries on the map.`);
                }
            });
            
            this.elements.regionalTable.appendChild(element);
        });
    }

    displayRelatedQueries(relatedQueries) {
        if (!this.elements.topQueries || !this.elements.risingQueries) return;
        
        // Clear existing content
        this.elements.topQueries.innerHTML = '';
        this.elements.risingQueries.innerHTML = '';
        
        if (!relatedQueries) {
            this.elements.topQueries.innerHTML = '<li style="color: #666;">No data available</li>';
            this.elements.risingQueries.innerHTML = '<li style="color: #666;">No data available</li>';
            return;
        }
        
        // Display top queries
        if (relatedQueries.top && Array.isArray(relatedQueries.top) && relatedQueries.top.length > 0) {
            relatedQueries.top.slice(0, 10).forEach(query => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="query-text">${TrendsUtils.truncateText(query.query || query, 40)}</span>
                    <span class="query-value">${query.value || ''}</span>
                `;
                li.addEventListener('click', () => this.searchInCountry(query.query || query));
                this.elements.topQueries.appendChild(li);
            });
        } else {
            this.elements.topQueries.innerHTML = '<li style="color: #666;">No top queries available</li>';
        }
        
        // Display rising queries
        if (relatedQueries.rising && Array.isArray(relatedQueries.rising) && relatedQueries.rising.length > 0) {
            relatedQueries.rising.slice(0, 10).forEach(query => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="query-text">${TrendsUtils.truncateText(query.query || query, 40)}</span>
                    <span class="query-value">${query.value || '🔥'}</span>
                `;
                li.addEventListener('click', () => this.searchInCountry(query.query || query));
                this.elements.risingQueries.appendChild(li);
            });
        } else {
            this.elements.risingQueries.innerHTML = '<li style="color: #666;">No rising queries available</li>';
        }
    }

    async handleRefresh() {
        if (this.selectedCountry) {
            await this.loadCountryTrending(this.selectedCountry.code);
        }
        
        if (this.currentData && this.selectedCountry) {
            await this.searchInCountry(this.currentData.keyword);
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
            console.log('🔄 Using demo data mode');
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        
        if (loading) {
            if (this.elements.loadingIndicator) {
                this.elements.loadingIndicator.style.display = 'block';
            }
            
            if (this.elements.countrySearchBtn) {
                this.elements.countrySearchBtn.disabled = true;
                this.elements.countrySearchBtn.innerHTML = '<span class="spinner" style="width: 20px; height: 20px; margin-right: 0.5rem;"></span>Searching...';
            }
            
            if (this.chart) {
                this.chart.showLoading();
            }
        } else {
            if (this.elements.loadingIndicator) {
                this.elements.loadingIndicator.style.display = 'none';
            }
            
            if (this.elements.countrySearchBtn) {
                this.elements.countrySearchBtn.disabled = false;
                this.elements.countrySearchBtn.innerHTML = '<span class="search-icon">🔍</span>Search';
            }
        }
    }

    showError(message) {
        if (this.elements.errorText && this.elements.errorMessage) {
            this.elements.errorText.textContent = message;
            this.elements.errorMessage.style.display = 'flex';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                this.hideError();
            }, 5000);
        }
        
        console.warn('⚠️ Error shown to user:', message);
    }

    hideError() {
        if (this.elements.errorMessage) {
            this.elements.errorMessage.style.display = 'none';
        }
    }

    // Utility methods
    exportData() {
        if (!this.currentData) {
            this.showError('No data to export');
            return;
        }
        
        const dataStr = JSON.stringify(this.currentData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `trends-${this.currentData.keyword}-${this.selectedCountry?.code || 'global'}-${Date.now()}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
    }

    exportChart() {
        if (this.chart) {
            this.chart.exportAsImage(`trends-chart-${this.selectedCountry?.code || 'global'}-${Date.now()}.png`);
        }
    }

    // Version management method
    getVersionInfo() {
        return {
            version: '1.0.4',
            branch: 'fix/map-display-and-ui-cleanup-v1.0.4',
            environment: 'development',
            policy: 'Map-only country selection permanently enforced'
        };
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WorldTrendsApp();
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

// Add version info to console on load
console.log('🔖 World Trends Explorer Version: v1.0.4 - Map-Only Interface');
console.log('🚫 Dropdown-based country selection permanently removed');
console.log('🗺️ Country selection ONLY through interactive map clicks');