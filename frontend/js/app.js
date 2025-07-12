/**
 * Main Application JavaScript for World Trends Explorer
 * Interactive World Map First - Click countries to explore trends
 */

class WorldTrendsApp {
    constructor() {
        this.api = window.trendsAPI;
        this.chart = null;
        this.worldMap = null;
        this.currentData = null;
        this.selectedCountry = null;
        this.isLoading = false;
        
        // DOM elements
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
            searchStats: document.getElementById('searchStats'),
            regionalTable: document.getElementById('regionalTable'),
            topQueries: document.getElementById('topQueries'),
            risingQueries: document.getElementById('risingQueries'),
            
            // Global trending
            globalTrendingCountrySelect: document.getElementById('globalTrendingCountrySelect'),
            globalTrendingGrid: document.getElementById('globalTrendingGrid'),
            
            // UI elements
            loadingIndicator: document.getElementById('loadingIndicator'),
            errorMessage: document.getElementById('errorMessage'),
            errorText: document.getElementById('errorText')
        };
        
        this.init();
    }

    async init() {
        console.log('🌍 Initializing World Trends Explorer - Interactive Map First...');
        
        try {
            // Initialize components
            this.chart = new TrendsChart('trendsChart');
            this.worldMap = new WorldMap('worldMap');
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadGlobalTrendingSearches();
            
            // Check API health
            await this.checkAPIHealth();
            
            console.log('✅ World Trends Explorer initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize app:', error);
            this.showError('Failed to initialize application');
        }
    }

    setupEventListeners() {
        // Country selection from map
        document.addEventListener('countrySelected', (e) => {
            this.handleCountrySelection(e.detail);
        });
        
        // Close country panel
        if (this.elements.closeCountryPanel) {
            this.elements.closeCountryPanel.addEventListener('click', () => {
                this.hideCountryPanel();
            });
        }
        
        // Country search
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
        
        // Global trending country selection
        if (this.elements.globalTrendingCountrySelect) {
            this.elements.globalTrendingCountrySelect.addEventListener('change', (e) => {
                this.loadGlobalTrendingSearches(e.target.value);
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
                        if (this.elements.countrySearchInput) {
                            this.elements.countrySearchInput.focus();
                        }
                        break;
                    case 'r':
                        e.preventDefault();
                        this.handleRefresh();
                        break;
                }
            } else if (e.key === 'Escape') {
                this.hideCountryPanel();
                this.hideSearchResults();
            }
        });
    }

    async handleCountrySelection(countryDetail) {
        console.log('🌍 Country selected:', countryDetail);
        
        if (!countryDetail || !countryDetail.code) {
            console.warn('Invalid country selection');
            return;
        }
        
        this.selectedCountry = {
            code: countryDetail.code,
            name: countryDetail.name
        };
        
        // Highlight country on map
        if (this.worldMap) {
            this.worldMap.highlightCountry(countryDetail.code);
        }
        
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
    }

    hideCountryPanel() {
        this.elements.countryInfoPanel.style.display = 'none';
        this.selectedCountry = null;
        
        // Reset map highlighting
        if (this.worldMap) {
            this.worldMap.reset();
        }
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
            this.showError('Please select a country first');
            return;
        }
        
        this.searchInCountry(keyword);
    }

    async searchInCountry(keyword) {
        if (!this.selectedCountry) {
            this.showError('No country selected');
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
        if (!this.elements.resultsTitle || !this.elements.searchStats || !this.elements.resultsSection) {
            console.warn('Search results elements not found');
            return;
        }
        
        // Update result header
        this.elements.resultsTitle.textContent = `"${data.keyword}" in ${this.selectedCountry?.name || data.geo}`;
        this.elements.searchStats.textContent = 
            `Updated: ${TrendsUtils.formatRelativeTime(data.timestamp)} | Country: ${this.selectedCountry?.name || data.geo}`;
        
        // Show results section
        this.elements.resultsSection.style.display = 'block';
        this.elements.resultsSection.classList.add('fade-in');
        
        // Update chart
        if (this.chart) {
            this.chart.updateChart(data);
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
            
            // Add click handler to select country
            element.addEventListener('click', () => {
                if (item.geoCode) {
                    this.handleCountrySelection({
                        code: item.geoCode,
                        name: item.geoName
                    });
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

    async loadGlobalTrendingSearches(geo = 'US') {
        try {
            console.log(`🌍 Loading global trending searches for: ${geo}`);
            
            const data = await this.api.getTrendingSearches(geo);
            this.displayGlobalTrendingSearches(data);
            
        } catch (error) {
            console.error('Failed to load global trending searches:', error);
            this.displayGlobalTrendingError();
        }
    }

    displayGlobalTrendingSearches(data) {
        if (!this.elements.globalTrendingGrid) return;
        
        this.elements.globalTrendingGrid.innerHTML = '';
        
        if (!data || !data.trending_searches || !Array.isArray(data.trending_searches)) {
            this.displayGlobalTrendingError();
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
                // Set country search input and suggest selecting a country
                if (this.elements.countrySearchInput) {
                    this.elements.countrySearchInput.value = item.query;
                }
                
                if (this.selectedCountry) {
                    this.searchInCountry(item.query);
                } else {
                    this.showError('Click on a country in the map above to explore this trend!');
                }
            });
            
            this.elements.globalTrendingGrid.appendChild(element);
        });
    }

    displayGlobalTrendingError() {
        if (!this.elements.globalTrendingGrid) return;
        
        this.elements.globalTrendingGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: #666; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <div>Failed to load trending searches</div>
                <button onclick="app.loadGlobalTrendingSearches()" 
                        style="margin-top: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    Retry
                </button>
            </div>
        `;
    }

    async handleRefresh() {
        if (this.selectedCountry) {
            await this.loadCountryTrending(this.selectedCountry.code);
        }
        
        const selectedGlobalCountry = this.elements.globalTrendingCountrySelect?.value || 'US';
        await this.loadGlobalTrendingSearches(selectedGlobalCountry);
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
            // Don't show error for API health check failures - just use demo data
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