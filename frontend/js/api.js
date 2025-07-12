/**
 * API Communication Module for World Trends Explorer
 * Handles all backend communication with Flask/Pytrends API
 */

class TrendsAPI {
    constructor(baseURL = 'http://localhost:5555/api/trends') {
        this.baseURL = baseURL;
        this.cache = new Map();
        this.requestTimeout = 30000; // 30 seconds
    }

    /**
     * Make HTTP request with timeout and error handling
     */
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.requestTimeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            clearTimeout(timeoutId);
            console.error(`API Error (${url}):`, error);
            throw error;
        }
    }

    /**
     * Get cached data if available and fresh
     */
    getCached(key, maxAge = 5 * 60 * 1000) { // 5 minutes default
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < maxAge) {
            return cached.data;
        }
        return null;
    }

    /**
     * Set cache data
     */
    setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    /**
     * Health check endpoint
     */
    async healthCheck() {
        try {
            const data = await this.makeRequest('/health');
            return data;
        } catch (error) {
            console.error('Health check failed:', error);
            return null;
        }
    }

    /**
     * Search trends for a keyword
     */
    async searchTrends(keyword, geo = '', timeframe = 'today 12-m') {
        if (!keyword || keyword.trim() === '') {
            throw new Error('Keyword is required');
        }

        const cacheKey = `search_${keyword}_${geo}_${timeframe}`;
        const cached = this.getCached(cacheKey);
        if (cached) {
            console.log('Returning cached search results');
            return cached;
        }

        const params = new URLSearchParams({
            keyword: keyword.trim(),
            timeframe: timeframe
        });

        if (geo && geo.trim() !== '') {
            params.append('geo', geo.trim());
        }

        try {
            const data = await this.makeRequest(`/search?${params}`);
            this.setCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error('Search trends failed:', error);
            throw new Error(`Failed to search trends for "${keyword}": ${error.message}`);
        }
    }

    /**
     * Get trending searches by country
     */
    async getTrendingSearches(geo = 'US') {
        const cacheKey = `trending_${geo}`;
        const cached = this.getCached(cacheKey, 10 * 60 * 1000); // 10 minutes cache
        if (cached) {
            console.log('Returning cached trending searches');
            return cached;
        }

        try {
            const data = await this.makeRequest(`/trending?geo=${geo}`);
            this.setCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error('Get trending searches failed:', error);
            throw new Error(`Failed to get trending searches for ${geo}: ${error.message}`);
        }
    }

    /**
     * Get keyword suggestions
     */
    async getSuggestions(keyword) {
        if (!keyword || keyword.trim() === '') {
            return { suggestions: [] };
        }

        const cacheKey = `suggestions_${keyword}`;
        const cached = this.getCached(cacheKey, 15 * 60 * 1000); // 15 minutes cache
        if (cached) {
            return cached;
        }

        try {
            const data = await this.makeRequest(`/suggestions?keyword=${encodeURIComponent(keyword.trim())}`);
            this.setCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error('Get suggestions failed:', error);
            return { suggestions: [] };
        }
    }

    /**
     * Get available countries
     */
    async getCountries() {
        const cacheKey = 'countries';
        const cached = this.getCached(cacheKey, 24 * 60 * 60 * 1000); // 24 hours cache
        if (cached) {
            return cached;
        }

        try {
            const data = await this.makeRequest('/countries');
            this.setCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error('Get countries failed:', error);
            return { countries: [] };
        }
    }

    /**
     * Compare multiple keywords
     */
    async compareTrends(keywords, geo = '', timeframe = 'today 12-m') {
        if (!keywords || !Array.isArray(keywords) || keywords.length < 2) {
            throw new Error('At least 2 keywords are required for comparison');
        }

        if (keywords.length > 5) {
            throw new Error('Maximum 5 keywords allowed for comparison');
        }

        const cacheKey = `compare_${keywords.join('_')}_${geo}_${timeframe}`;
        const cached = this.getCached(cacheKey);
        if (cached) {
            console.log('Returning cached comparison results');
            return cached;
        }

        const payload = {
            keywords: keywords.map(k => k.trim()),
            timeframe: timeframe
        };

        if (geo && geo.trim() !== '') {
            payload.geo = geo.trim();
        }

        try {
            const data = await this.makeRequest('/compare', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            this.setCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error('Compare trends failed:', error);
            throw new Error(`Failed to compare trends: ${error.message}`);
        }
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('API cache cleared');
    }

    /**
     * Get cache statistics
     */
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }
}

// Utility functions for data processing
const TrendsUtils = {
    /**
     * Format date for display
     */
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            return dateString;
        }
    },

    /**
     * Format relative time
     */
    formatRelativeTime(dateString) {
        if (!dateString) return 'Unknown';
        
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);

            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins} minutes ago`;
            if (diffHours < 24) return `${diffHours} hours ago`;
            if (diffDays < 7) return `${diffDays} days ago`;
            
            return this.formatDate(dateString);
        } catch (error) {
            return this.formatDate(dateString);
        }
    },

    /**
     * Truncate text to specified length
     */
    truncateText(text, maxLength = 50) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    },

    /**
     * Get country flag emoji by country code
     */
    getCountryFlag(countryCode) {
        const flags = {
            'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷',
            'IT': '🇮🇹', 'ES': '🇪🇸', 'CA': '🇨🇦', 'AU': '🇦🇺',
            'JP': '🇯🇵', 'KR': '🇰🇷', 'IN': '🇮🇳', 'BR': '🇧🇷',
            'MX': '🇲🇽', 'RU': '🇷🇺', 'CN': '🇨🇳', 'NL': '🇳🇱',
            'SE': '🇸🇪', 'NO': '🇳🇴', 'DK': '🇩🇰', 'FI': '🇫🇮'
        };
        return flags[countryCode] || '🌍';
    },

    /**
     * Sort data by value
     */
    sortByValue(data, key = 'value', descending = true) {
        if (!Array.isArray(data)) return [];
        
        return [...data].sort((a, b) => {
            const aVal = a[key] || 0;
            const bVal = b[key] || 0;
            return descending ? bVal - aVal : aVal - bVal;
        });
    },

    /**
     * Filter data by minimum value
     */
    filterByMinValue(data, key = 'value', minValue = 1) {
        if (!Array.isArray(data)) return [];
        
        return data.filter(item => (item[key] || 0) >= minValue);
    },

    /**
     * Generate color based on value intensity
     */
    getIntensityColor(value, maxValue = 100) {
        if (!value || value <= 0) return '#e1e5e9';
        
        const intensity = Math.min(value / maxValue, 1);
        const colors = [
            '#c6dbef', '#9ecae1', '#6baed6', 
            '#4292c6', '#2171b5', '#08519c'
        ];
        
        const index = Math.floor(intensity * (colors.length - 1));
        return colors[index];
    },

    /**
     * Debounce function calls
     */
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
    },

    /**
     * Check if data is valid trends response
     */
    isValidTrendsData(data) {
        return data && 
               typeof data === 'object' && 
               data.keyword && 
               (Array.isArray(data.interest_over_time) || 
                Array.isArray(data.interest_by_region));
    }
};

// Initialize global API instance
window.trendsAPI = new TrendsAPI();
window.TrendsUtils = TrendsUtils;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TrendsAPI, TrendsUtils };
}
