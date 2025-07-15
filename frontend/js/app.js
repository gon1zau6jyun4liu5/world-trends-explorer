/**
 * Main Application JavaScript for World Trends Explorer v1.2.4
 * Enhanced with Quick Search Button functionality (Issue #33 Fix)
 */

class WorldTrendsApp {
    constructor() {
        this.api = window.trendsAPI;
        this.chart = null;
        this.worldMap = null;
        this.currentData = null;
        this.selectedCountry = null;
        this.isLoading = false;
        this.version = 'v1.2.4';
        
        // DOM elements - Enhanced with quick buttons
        this.elements = this.initializeElements();
        
        this.init();
    }

    initializeElements() {
        return {
            // Search elements
            searchInput: document.getElementById('searchInput'),
            countrySelect: document.getElementById('countrySelect'),
            searchBtn: document.getElementById('searchBtn'),
            
            // Quick search buttons - Fix for Issue #33
            quickBtns: document.querySelectorAll('.quick-btn'),
            
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
    }

    async init() {
        console.log(`🌍 World Trends Explorer ${this.version} - Enhanced Quick Search`);
        console.log('📅 Build Date: July 15, 2025');
        console.log('🚀 Features: Quick Search Buttons, Full Interface, Multi-language');
        
        try {
            // Display version
            this.displayVersion();
            
            // Initialize components
            this.chart = new TrendsChart('trendsChart');
            this.worldMap = new WorldMap('worldMap');
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Load initial trending data
            await this.loadGlobalTrending();
            
            // Check API health
            await this.checkAPIHealth();
            
            console.log(`✅ World Trends Explorer ${this.version} initialized successfully`);
        } catch (error) {
            console.error('❌ Failed to initialize app:', error);
            this.showError('Failed to initialize application');
        }
    }

    displayVersion() {
        // Add version to header if not exists
        const header = document.querySelector('.header .container');
        if (header && !document.getElementById('versionDisplay')) {
            const versionDiv = document.createElement('div');
            versionDiv.id = 'versionDisplay';
            versionDiv.style.cssText = 'position: absolute; top: 10px; right: 20px; color: rgba(255,255,255,0.7); font-size: 0.9rem;';
            versionDiv.textContent = this.version;
            header.style.position = 'relative';
            header.appendChild(versionDiv);
        }
    }

    setupEventListeners() {
        console.log(`🔧 Setting up event listeners for ${this.version}...`);
        
        // Primary search functionality
        if (this.elements.searchBtn) {
            this.elements.searchBtn.addEventListener('click', () => this.handleSearch());
        }
        
        if (this.elements.searchInput) {
            this.elements.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleSearch();
            });
            
            // Search suggestions (debounced)
            this.elements.searchInput.addEventListener('input', 
                TrendsUtils.debounce((e) => this.handleSearchInput(e), 300)
            );
        }
        
        // Enhanced Quick search buttons - Fix for Issue #33
        this.setupQuickSearchButtons();
        
        // Country selection from map
        document.addEventListener('countrySelected', (e) => {
            this.handleCountrySelection(e.detail);
        });
        
        // Country panel controls
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
                this.loadGlobalTrending(e.target.value);
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
                        if (this.elements.searchInput) {
                            this.elements.searchInput.focus();
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
        
        console.log(`✅ Event listeners set up for ${this.version}`);
    }

    /**
     * Enhanced Quick Search Buttons Setup - Fix for Issue #33
     */
    setupQuickSearchButtons() {
        console.log('🔧 Setting up quick search buttons...');
        
        if (!this.elements.quickBtns || this.elements.quickBtns.length === 0) {
            console.warn('⚠️ Quick search buttons not found');
            return;
        }
        
        this.elements.quickBtns.forEach((btn, index) => {
            // Remove any existing listeners
            btn.replaceWith(btn.cloneNode(true));
        });
        
        // Re-query the buttons after cloning
        this.elements.quickBtns = document.querySelectorAll('.quick-btn');
        
        this.elements.quickBtns.forEach((btn, index) => {
            // Enhanced click handler
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const keyword = btn.dataset.keyword || btn.getAttribute('data-keyword');
                const category = btn.dataset.category || btn.getAttribute('data-category');
                
                console.log(`🔍 Quick search clicked: "${keyword}" (${category})`);
                
                if (keyword && keyword.trim()) {
                    this.handleQuickSearch(keyword.trim(), btn, category);
                } else {
                    console.error('❌ No keyword found for quick search button');
                }
            });
            
            // Enhanced hover effects
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-3px)';
                console.log(`💡 Hovering over: ${btn.dataset.keyword}`);
            });
            
            btn.addEventListener('mouseleave', () => {
                if (!btn.classList.contains('loading')) {
                    btn.style.transform = '';
                }
            });
            
            // Touch support for mobile
            btn.addEventListener('touchstart', (e) => {
                btn.style.transform = 'translateY(-2px)';
            });
            
            btn.addEventListener('touchend', (e) => {
                setTimeout(() => {
                    if (!btn.classList.contains('loading')) {
                        btn.style.transform = '';
                    }
                }, 150);
            });
        });
        
        console.log(`✅ Set up ${this.elements.quickBtns.length} quick search buttons`);
    }

    /**
     * Handle quick search with enhanced feedback - Fix for Issue #33
     */
    async handleQuickSearch(keyword, buttonElement, category) {
        try {
            // Immediate visual feedback
            this.setQuickButtonLoading(buttonElement, true);
            
            // Set the search input
            if (this.elements.searchInput) {
                this.elements.searchInput.value = keyword;
                
                // Add visual highlight to search input
                this.elements.searchInput.style.borderColor = '#667eea';
                this.elements.searchInput.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
                
                setTimeout(() => {
                    this.elements.searchInput.style.borderColor = '';
                    this.elements.searchInput.style.boxShadow = '';
                }, 1000);
            }
            
            // Add category-specific analytics
            console.log(`📊 Quick search analytics: Category=${category}, Keyword=${keyword}`);
            
            // Perform the search
            await this.handleSearch();
            
            // Success feedback
            this.showQuickSearchSuccess(buttonElement, keyword);
            
        } catch (error) {
            console.error('Quick search failed:', error);
            this.showQuickSearchError(buttonElement, error.message);
        } finally {
            // Remove loading state after delay
            setTimeout(() => {
                this.setQuickButtonLoading(buttonElement, false);
            }, 1000);
        }
    }

    /**
     * Set loading state for quick button
     */
    setQuickButtonLoading(button, loading) {
        if (!button) return;
        
        if (loading) {
            button.classList.add('loading');
            button.style.pointerEvents = 'none';
            button.style.opacity = '0.7';
            
            // Store original content
            if (!button.dataset.originalContent) {
                button.dataset.originalContent = button.innerHTML;
            }
            
            // Show loading state
            button.innerHTML = `
                <span class="btn-icon">⏳</span>
                <span class="btn-text">Loading...</span>
            `;
        } else {
            button.classList.remove('loading');
            button.style.pointerEvents = '';
            button.style.opacity = '';
            button.style.transform = '';
            
            // Restore original content
            if (button.dataset.originalContent) {
                button.innerHTML = button.dataset.originalContent;
                delete button.dataset.originalContent;
            }
        }
    }

    /**
     * Show quick search success feedback
     */
    showQuickSearchSuccess(button, keyword) {
        if (!button) return;
        
        // Temporary success state
        const originalBg = button.style.background;
        button.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
        button.style.color = 'white';
        
        setTimeout(() => {
            button.style.background = originalBg;
            button.style.color = '';
        }, 2000);
        
        console.log(`✅ Quick search successful: ${keyword}`);
    }

    /**
     * Show quick search error feedback
     */
    showQuickSearchError(button, errorMessage) {
        if (!button) return;
        
        // Temporary error state
        const originalBg = button.style.background;
        button.style.background = 'linear-gradient(135deg, #dc3545 0%, #e74c3c 100%)';
        button.style.color = 'white';
        
        setTimeout(() => {
            button.style.background = originalBg;
            button.style.color = '';
        }, 3000);
        
        this.showError(`Quick search failed: ${errorMessage}`);
        console.error(`❌ Quick search failed: ${errorMessage}`);
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
                // Optional: Get suggestions for auto-complete
                console.log(`🔍 Getting suggestions for: ${keyword}`);
            } catch (error) {
                console.warn('Failed to get suggestions:', error);
            }
        }
    }

    async handleCountrySelection(countryDetail) {
        console.log('🌍 Country selected:', countryDetail);
        
        this.selectedCountry = {
            code: countryDetail.code,
            name: countryDetail.name
        };
        
        // Update country selector if available
        if (countryDetail.code && this.elements.countrySelect) {
            const option = Array.from(this.elements.countrySelect.options)
                .find(opt => opt.value === countryDetail.code);
            if (option) {
                this.elements.countrySelect.value = countryDetail.code;
            }
        }
        
        // Show country info panel
        this.showCountryPanel(countryDetail);
        
        // Load country-specific trending data
        await this.loadCountryTrending(countryDetail.code);
        
        // Re-search with selected country if we have current data
        if (this.currentData && this.currentData.keyword) {
            await this.handleSearch();
        }
    }

    async showCountryPanel(countryDetail) {
        const flag = TrendsUtils.getCountryFlag(countryDetail.code);
        
        // Update panel content
        if (this.elements.countryTitle) {
            this.elements.countryTitle.innerHTML = `${flag} ${countryDetail.name}`;
        }
        if (this.elements.countryCode) {
            this.elements.countryCode.textContent = countryDetail.code;
        }
        
        // Show panel with animation
        if (this.elements.countryInfoPanel) {
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
        
        console.log(`📱 Country panel shown for ${countryDetail.name}`);
    }

    hideCountryPanel() {
        if (this.elements.countryInfoPanel) {
            this.elements.countryInfoPanel.style.display = 'none';
        }
        this.selectedCountry = null;
        console.log('📱 Country panel hidden');
    }

    async loadCountryTrending(countryCode) {
        try {
            this.setCountryLoading(true);
            
            console.log(`🔥 Loading trending searches for: ${countryCode}`);
            
            const data = await this.api.getTrendingSearches(countryCode);
            this.displayCountryTrending(data);
            
        } catch (error) {
            console.error('Failed to load country trending:', error);
            this.displayCountryTrendingError(error);
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
        if (this.elements.trendingCount) {
            this.elements.trendingCount.textContent = data.trending_searches.length;
        }
        if (this.elements.dataAvailable) {
            this.elements.dataAvailable.textContent = 'Available';
        }
        
        // Display trending topics
        data.trending_searches.slice(0, 8).forEach(item => {
            const element = document.createElement('div');
            element.className = 'trending-item';
            element.innerHTML = `
                <div class="trending-rank">#${item.rank}</div>
                <div class="trending-query">${TrendsUtils.truncateText(item.query, 25)}</div>
            `;
            
            element.addEventListener('click', () => {
                if (this.elements.searchInput) {
                    this.elements.searchInput.value = item.query;
                    this.handleSearch();
                }
            });
            
            this.elements.countryTrendingGrid.appendChild(element);
        });
        
        console.log(`✅ Displayed ${data.trending_searches.length} trending topics`);
    }

    displayCountryTrendingError(error) {
        if (!this.elements.countryTrendingGrid) return;
        
        if (this.elements.trendingCount) {
            this.elements.trendingCount.textContent = '0';
        }
        if (this.elements.dataAvailable) {
            this.elements.dataAvailable.textContent = 'Unavailable';
        }
        
        this.elements.countryTrendingGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: #666; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <div>Failed to load trending data</div>
                <div style="font-size: 0.9rem; color: #999; margin-top: 0.5rem;">
                    ${error ? error.message : 'Unknown error'}
                </div>
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
        
        // Set the main search with country
        if (this.elements.searchInput) {
            this.elements.searchInput.value = keyword;
        }
        if (this.elements.countrySelect) {
            this.elements.countrySelect.value = this.selectedCountry.code;
        }
        
        await this.handleSearch();
    }

    displaySearchResults(data) {
        if (!this.elements.resultsSection) {
            console.warn('Search results elements not found');
            return;
        }
        
        // Update result header
        if (this.elements.resultsTitle) {
            this.elements.resultsTitle.textContent = `"${data.keyword}" Trends`;
        }
        if (this.elements.searchStats) {
            this.elements.searchStats.textContent = 
                `Updated: ${TrendsUtils.formatRelativeTime(data.timestamp)} | Region: ${data.geo || 'Worldwide'}`;
        }
        
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

    searchRelatedQuery(query) {
        if (query && typeof query === 'string') {
            if (this.elements.searchInput) {
                this.elements.searchInput.value = query;
                this.handleSearch();
            }
        }
    }

    async loadGlobalTrending(geo = 'US') {
        try {
            console.log(`🔥 Loading global trending searches for: ${geo}`);
            
            const data = await this.api.getTrendingSearches(geo);
            this.displayGlobalTrending(data);
            
        } catch (error) {
            console.error('Failed to load global trending:', error);
            this.displayGlobalTrendingError();
        }
    }

    displayGlobalTrending(data) {
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
                if (this.elements.searchInput) {
                    this.elements.searchInput.value = item.query;
                    this.handleSearch();
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
                <button onclick="app.loadGlobalTrending()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    Retry
                </button>
            </div>
        `;
    }

    async handleRefresh() {
        if (this.currentData && this.currentData.keyword) {
            this.api.clearCache();
            await this.handleSearch();
        } else {
            await this.loadGlobalTrending();
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
            if (this.elements.searchBtn) {
                this.elements.searchBtn.disabled = true;
                this.elements.searchBtn.innerHTML = '<span class="spinner" style="width: 20px; height: 20px; margin-right: 0.5rem;"></span>Searching...';
            }
            if (this.chart) {
                this.chart.showLoading();
            }
        } else {
            if (this.elements.loadingIndicator) {
                this.elements.loadingIndicator.style.display = 'none';
            }
            if (this.elements.searchBtn) {
                this.elements.searchBtn.disabled = false;
                this.elements.searchBtn.innerHTML = '<span class="search-icon">🔍</span>Search';
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

    // Version management method
    getVersionInfo() {
        return {
            version: '1.2.4',
            branch: 'fix/quick-search-buttons-v1.2.4',
            environment: 'development',
            features: ['Enhanced Quick Search Buttons', 'Full Interface', 'Multi-language Support']
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