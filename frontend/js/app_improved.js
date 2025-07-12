/**
 * Improved Main Application JavaScript for World Trends Explorer
 * Enhanced country selection and responsive UI
 */

class ImprovedWorldTrendsApp {
    constructor() {
        this.api = window.trendsAPI;
        this.chart = null;
        this.worldMap = null;
        this.currentData = null;
        this.selectedCountry = null;
        this.isLoading = false;
        
        // DOM elements
        this.elements = {
            searchInput: document.getElementById('searchInput'),
            countrySelect: document.getElementById('countrySelect'),
            searchBtn: document.getElementById('searchBtn'),
            resultsSection: document.getElementById('resultsSection'),
            searchKeyword: document.getElementById('searchKeyword'),
            searchStats: document.getElementById('searchStats'),
            regionalTable: document.getElementById('regionalTable'),
            topQueries: document.getElementById('topQueries'),
            risingQueries: document.getElementById('risingQueries'),
            globalTrendingGrid: document.getElementById('globalTrendingGrid'),
            trendingCountryName: document.getElementById('trendingCountryName'),
            selectedCountryInfo: document.getElementById('selectedCountryInfo'),
            selectedCountryName: document.getElementById('selectedCountryName'),
            loadingIndicator: document.getElementById('loadingIndicator'),
            errorMessage: document.getElementById('errorMessage'),
            errorText: document.getElementById('errorText')
        };
        
        this.init();
    }

    async init() {
        console.log('🌍 Initializing Improved World Trends Explorer...');
        
        try {
            // Initialize components
            this.chart = new TrendsChart('trendsChart');
            this.worldMap = new WorldMap('worldMap');
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Load initial trending data for Korea
            await this.loadTrendingSearches('KR');
            
            console.log('✅ Improved World Trends Explorer initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize app:', error);
            this.showError('애플리케이션 초기화에 실패했습니다');
        }
    }

    setupEventListeners() {
        // Search functionality
        this.elements.searchBtn.addEventListener('click', () => this.handleSearch());
        this.elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
        
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

    async handleSearch() {
        const keyword = this.elements.searchInput.value.trim();
        const geo = this.elements.countrySelect.value;
        
        if (!keyword) {
            this.showError('키워드를 입력해주세요');
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
            
            const data = await this.api.searchTrends(keyword, geo);
            
            if (this.isValidTrendsData(data)) {
                this.currentData = data;
                this.displaySearchResults(data);
            } else {
                throw new Error('API에서 유효하지 않은 데이터를 받았습니다');
            }
            
        } catch (error) {
            console.error('Search failed:', error);
            this.showError(error.message || '트렌드 검색에 실패했습니다');
        } finally {
            this.setLoading(false);
        }
    }

    handleCountrySelection(countryDetail) {
        console.log('Country selected:', countryDetail);
        
        this.selectedCountry = {
            code: countryDetail.code,
            name: countryDetail.name
        };
        
        // Show selected country info
        this.showSelectedCountryInfo(countryDetail);
        
        // Update country selector if available
        if (countryDetail.code && this.elements.countrySelect) {
            const option = Array.from(this.elements.countrySelect.options)
                .find(opt => opt.value === countryDetail.code);
            if (option) {
                this.elements.countrySelect.value = countryDetail.code;
            }
        }
        
        // Load trending for selected country
        this.loadTrendingSearches(countryDetail.code || 'KR');
    }

    showSelectedCountryInfo(countryDetail) {
        if (!this.elements.selectedCountryInfo || !this.elements.selectedCountryName) return;
        
        const flag = this.getCountryFlag(countryDetail.code);
        this.elements.selectedCountryName.textContent = `${flag} ${countryDetail.name}`;
        this.elements.selectedCountryInfo.classList.add('visible');
        
        // Hide after 3 seconds
        setTimeout(() => {
            this.elements.selectedCountryInfo.classList.remove('visible');
        }, 3000);
    }

    async loadTrendingSearches(geo = 'KR') {
        try {
            console.log(`🔥 Loading trending searches for: ${geo}`);
            
            const data = await this.api.getTrendingSearches(geo);
            this.displayTrendingSearches(data, geo);
            
        } catch (error) {
            console.error('Failed to load trending searches:', error);
            this.displayTrendingError();
        }
    }

    displayTrendingSearches(data, geo) {
        if (!this.elements.globalTrendingGrid) return;
        
        // Update country name in heading
        if (this.elements.trendingCountryName) {
            const countryNames = {
                'KR': '한국',
                'US': '미국',
                'JP': '일본',
                'CN': '중국',
                'GB': '영국',
                'DE': '독일',
                'FR': '프랑스',
                'CA': '캐나다',
                'AU': '호주',
                'IN': '인도',
                'BR': '브라질'
            };
            this.elements.trendingCountryName.textContent = countryNames[geo] || '전 세계';
        }
        
        this.elements.globalTrendingGrid.innerHTML = '';
        
        if (!data || !data.trending_searches || !Array.isArray(data.trending_searches)) {
            this.displayTrendingError();
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
                this.elements.searchInput.value = item.query;
                this.handleSearch();
            });
            
            this.elements.globalTrendingGrid.appendChild(element);
        });
    }

    displayTrendingError() {
        if (!this.elements.globalTrendingGrid) return;
        
        this.elements.globalTrendingGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: #666; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <div>인기 검색어를 불러올 수 없습니다</div>
                <button onclick="app.loadTrendingSearches('${this.selectedCountry?.code || 'KR'}')" 
                        style="margin-top: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    다시 시도
                </button>
            </div>
        `;
    }

    displaySearchResults(data) {
        // Update result header
        this.elements.searchKeyword.textContent = data.keyword;
        this.elements.searchStats.textContent = 
            `업데이트: ${this.formatRelativeTime(data.timestamp)} | 지역: ${data.geo || '전 세계'}`;
        
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
                '<div style="text-align: center; color: #666; padding: 2rem;">지역별 데이터가 없습니다</div>';
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
        this.elements.topQueries.innerHTML = '';
        this.elements.risingQueries.innerHTML = '';
        
        if (!relatedQueries) {
            this.elements.topQueries.innerHTML = '<li style="color: #666;">데이터가 없습니다</li>';
            this.elements.risingQueries.innerHTML = '<li style="color: #666;">데이터가 없습니다</li>';
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
                li.addEventListener('click', () => this.searchRelatedQuery(query.query || query));
                this.elements.topQueries.appendChild(li);
            });
        } else {
            this.elements.topQueries.innerHTML = '<li style="color: #666;">인기 검색어가 없습니다</li>';
        }
        
        // Display rising queries
        if (relatedQueries.rising && Array.isArray(relatedQueries.rising) && relatedQueries.rising.length > 0) {
            relatedQueries.rising.slice(0, 10).forEach(query => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="query-text">${this.truncateText(query.query || query, 40)}</span>
                    <span class="query-value">${query.value || '🔥'}</span>
                `;
                li.addEventListener('click', () => this.searchRelatedQuery(query.query || query));
                this.elements.risingQueries.appendChild(li);
            });
        } else {
            this.elements.risingQueries.innerHTML = '<li style="color: #666;">급상승 검색어가 없습니다</li>';
        }
    }

    searchRelatedQuery(query) {
        if (query && typeof query === 'string') {
            this.elements.searchInput.value = query;
            this.handleSearch();
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        
        if (loading) {
            this.elements.loadingIndicator.style.display = 'block';
            this.elements.searchBtn.disabled = true;
            this.elements.searchBtn.innerHTML = `
                <div style="width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top: 2px solid white; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 0.5rem;"></div>
                검색 중...
            `;
            
            if (this.chart) {
                this.chart.showLoading();
            }
        } else {
            this.elements.loadingIndicator.style.display = 'none';
            this.elements.searchBtn.disabled = false;
            this.elements.searchBtn.innerHTML = '<span class="search-icon">🔍</span>검색';
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
    getCountryFlag(countryCode) {
        const flags = {
            'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷',
            'IT': '🇮🇹', 'ES': '🇪🇸', 'CA': '🇨🇦', 'AU': '🇦🇺',
            'JP': '🇯🇵', 'KR': '🇰🇷', 'IN': '🇮🇳', 'BR': '🇧🇷',
            'MX': '🇲🇽', 'RU': '🇷🇺', 'CN': '🇨🇳', 'NL': '🇳🇱',
            'SE': '🇸🇪', 'NO': '🇳🇴', 'DK': '🇩🇰', 'FI': '🇫🇮'
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

            if (diffMins < 1) return '방금 전';
            if (diffMins < 60) return `${diffMins}분 전`;
            if (diffHours < 24) return `${diffHours}시간 전`;
            
            return date.toLocaleDateString('ko-KR');
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
    window.app = new ImprovedWorldTrendsApp();
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (window.app) {
        window.app.showError('예상치 못한 오류가 발생했습니다');
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    if (window.app) {
        window.app.showError('예상치 못한 오류가 발생했습니다');
    }
});