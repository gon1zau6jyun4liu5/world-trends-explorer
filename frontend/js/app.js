/**
 * Main Application JavaScript for World Trends Explorer
 * Coordinates all components and handles user interactions
 */

class WorldTrendsApp {
    constructor() {
        this.api = window.trendsAPI;
        this.chart = null;
        this.worldMap = null;
        this.currentData = null;
        this.isLoading = false;
        
        // DOM elements
        this.elements = {
            searchInput: document.getElementById('searchInput'),
            countrySelect: document.getElementById('countrySelect'),
            searchBtn: document.getElementById('searchBtn'),
            trendingCountrySelect: document.getElementById('trendingCountrySelect'),
            resultsSection: document.getElementById('resultsSection'),
            searchKeyword: document.getElementById('searchKeyword'),
            searchStats: document.getElementById('searchStats'),
            regionalTable: document.getElementById('regionalTable'),
            topQueries: document.getElementById('topQueries'),
            risingQueries: document.getElementById('risingQueries'),
            trendingGrid: document.getElementById('trendingGrid'),
            loadingIndicator: document.getElementById('loadingIndicator'),
            errorMessage: document.getElementById('errorMessage'),
            errorText: document.getElementById('errorText')
        };
        
        this.init();
    }

    async init() {
        console.log('🌍 Initializing World Trends Explorer...');
        
        try {
            // Initialize components
            this.chart = new TrendsChart('trendsChart');
            this.worldMap = new WorldMap('worldMap');
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadTrendingSearches();
            
            // Check API health
            await this.checkAPIHealth();
            
            console.log('✅ World Trends Explorer initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize app:', error);
            this.showError('Failed to initialize application');
        }
    }

    setupEventListeners() {
        // Search functionality
        this.elements.searchBtn.addEventListener('click', () => this.handleSearch());
        this.elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
        
        // Search input suggestions (debounced)
        this.elements.searchInput.addEventListener('input', 
            TrendsUtils.debounce((e) => this.handleSearchInput(e), 300)
        );
        
        // Trending country selection
        if (this.elements.trendingCountrySelect) {
            this.elements.trendingCountrySelect.addEventListener('change', (e) => {
                this.loadTrendingSearches(e.target.value);
            });
        }
        
        // Country selection from map
        document.addEventListener('countrySelected', (e) => {
            this.handleCountrySelection(e.detail);
        });
        
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
                        this.elements.searchInput.focus();
                        break;
                    case 'r':
                        e.preventDefault();
                        this.handleRefresh();
                        break;
                }
            }
        });
    }

    async handleSearch() {
        const keyword = this.elements.searchInput.value.trim();
        const geo = this.elements.countrySelect.value;
        
        if (!keyword) {
            this.showError('Please enter a keyword to search');
            return;
        }
        
        if (this.isLoading) {
            console.log('Search already in progress...');
            return;
        }
        
        try {
            this.setLoading(true);
            this.hideError();
            
            console.log(`🔍 Searching trends for: "${keyword}" in ${geo || 'worldwide'}`);
            
            // Search trends
            const data = await this.api.searchTrends(keyword, geo);
            
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

    async handleSearchInput(event) {
        const keyword = event.target.value.trim();
        if (keyword.length > 2) {
            try {
                // Get suggestions (optional feature)
                // const suggestions = await this.api.getSuggestions(keyword);
                // this.displaySuggestions(suggestions);
            } catch (error) {
                console.warn('Failed to get suggestions:', error);
            }
        }
    }

    handleCountrySelection(countryDetail) {
        console.log('Country selected:', countryDetail);
        
        // Update country selector
        if (countryDetail.code && this.elements.countrySelect) {
            const option = Array.from(this.elements.countrySelect.options)
                .find(opt => opt.value === countryDetail.code);
            if (option) {
                this.elements.countrySelect.value = countryDetail.code;
            }
        }
        
        // Re-search with selected country if we have current data
        if (this.currentData && this.currentData.keyword) {
            this.handleSearch();
        }
    }

    async handleRefresh() {
        if (this.currentData && this.currentData.keyword) {
            this.api.clearCache();
            await this.handleSearch();
        } else {
            await this.loadTrendingSearches();
        }
    }

    displaySearchResults(data) {
        // Update result header
        this.elements.searchKeyword.textContent = data.keyword;
        this.elements.searchStats.textContent = 
            `Updated: ${TrendsUtils.formatRelativeTime(data.timestamp)} | Region: ${data.geo || 'Worldwide'}`;
        
        // Show results section
        this.elements.resultsSection.style.display = 'block';
        this.elements.resultsSection.classList.add('fade-in');
        
        // Update chart
        if (this.chart) {
            this.chart.updateChart(data);
        }
        
        // Update world map
        if (this.worldMap) {
            this.worldMap.updateData(data);
        }
        
        // Update regional data
        this.displayRegionalData(data.interest_by_region, data.keyword);
        
        // Update related queries
        this.displayRelatedQueries(data.related_queries);
        
        // Scroll to results
        this.elements.resultsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
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
                li.addEventListener('click', () => this.searchRelatedQuery(query.query || query));
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
                li.addEventListener('click', () => this.searchRelatedQuery(query.query || query));
                this.elements.risingQueries.appendChild(li);
            });
        } else {
            this.elements.risingQueries.innerHTML = '<li style="color: #666;">No rising queries available</li>';
        }
    }

    async loadTrendingSearches(geo = 'US') {
        try {
            console.log(`🔥 Loading trending searches for: ${geo}`);
            
            const data = await this.api.getTrendingSearches(geo);
            this.displayTrendingSearches(data);
            
        } catch (error) {
            console.error('Failed to load trending searches:', error);
            this.displayTrendingError();
        }
    }

    displayTrendingSearches(data) {
        if (!this.elements.trendingGrid) return;
        
        this.elements.trendingGrid.innerHTML = '';
        
        if (!data || !data.trending_searches || !Array.isArray(data.trending_searches)) {
            this.displayTrendingError();
            return;
        }
        
        data.trending_searches.slice(0, 12).forEach(item => {
            const element = document.createElement('div');
            element.className = 'trending-item';
            element.innerHTML = `
                <div class="trending-rank">#${item.rank}</div>
                <div class="trending-query">${TrendsUtils.truncateText(item.query, 30)}</div>
            `;
            
            element.addEventListener('click', () => {
                this.elements.searchInput.value = item.query;
                this.handleSearch();
            });
            
            this.elements.trendingGrid.appendChild(element);
        });
    }

    displayTrendingError() {
        if (!this.elements.trendingGrid) return;
        
        this.elements.trendingGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: #666; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <div>Failed to load trending searches</div>
                <button onclick="app.loadTrendingSearches()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    Retry
                </button>
            </div>
        `;
    }

    searchRelatedQuery(query) {
        if (query && typeof query === 'string') {
            this.elements.searchInput.value = query;
            this.handleSearch();
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
            this.elements.loadingIndicator.style.display = 'block';
            this.elements.searchBtn.disabled = true;
            this.elements.searchBtn.innerHTML = '<span class="spinner" style="width: 20px; height: 20px; margin-right: 0.5rem;"></span>Searching...';
            
            if (this.chart) {
                this.chart.showLoading();
            }
        } else {
            this.elements.loadingIndicator.style.display = 'none';
            this.elements.searchBtn.disabled = false;
            this.elements.searchBtn.innerHTML = '<span class="search-icon">🔍</span>Search';
        }
    }

    showError(message) {
        this.elements.errorText.textContent = message;
        this.elements.errorMessage.style.display = 'flex';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        this.elements.errorMessage.style.display = 'none';
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
        link.download = `trends-${this.currentData.keyword}-${Date.now()}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
    }

    exportChart() {
        if (this.chart) {
            this.chart.exportAsImage(`trends-chart-${Date.now()}.png`);
        }
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
