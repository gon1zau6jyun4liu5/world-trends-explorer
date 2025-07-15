/**
 * Unit Tests for World Trends Explorer v1.2.4
 * Tests for Issue #32 - Critical Search Functionality Fix
 */

// Mock DOM setup for testing
function setupMockDOM() {
    // Create mock elements
    const mockElements = {
        searchInput: { value: '', addEventListener: jest.fn(), focus: jest.fn() },
        searchBtn: { addEventListener: jest.fn(), disabled: false, innerHTML: '' },
        countrySelect: { value: '', options: [] },
        globalTrendingGrid: { innerHTML: '' },
        loadingIndicator: { style: { display: 'none' } },
        errorMessage: { style: { display: 'none' } },
        errorText: { textContent: '' },
        resultsSection: { style: { display: 'none' }, classList: { add: jest.fn() } }
    };

    // Mock document.getElementById
    global.document = {
        getElementById: jest.fn((id) => mockElements[id] || null),
        querySelector: jest.fn(() => ({ appendChild: jest.fn(), style: {} })),
        addEventListener: jest.fn(),
        createElement: jest.fn(() => ({
            id: '',
            style: { cssText: '' },
            textContent: '',
            appendChild: jest.fn()
        }))
    };

    // Mock localStorage
    global.localStorage = {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn()
    };

    return mockElements;
}

// Mock TrendsUtils
global.TrendsUtils = {
    debounce: (fn) => fn,
    formatRelativeTime: jest.fn(() => '1 minute ago'),
    isValidTrendsData: jest.fn(() => true),
    getCountryFlag: jest.fn(() => '🇺🇸'),
    truncateText: jest.fn((text) => text)
};

// Mock API
global.trendsAPI = {
    searchTrends: jest.fn(),
    getTrendingSearches: jest.fn(),
    healthCheck: jest.fn(),
    clearCache: jest.fn()
};

describe('WorldTrendsApp v1.2.4 - Critical Search Fix Tests', () => {
    let app;
    let mockElements;

    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();
        
        // Setup mock DOM
        mockElements = setupMockDOM();
        
        // Mock Chart and Map classes
        global.TrendsChart = jest.fn();
        global.WorldMap = jest.fn();
        
        // Mock console methods
        global.console = {
            log: jest.fn(),
            error: jest.fn(),
            warn: jest.fn()
        };
    });

    describe('Issue #32: Search Functionality Fix', () => {
        test('should initialize essential DOM elements correctly', () => {
            app = new WorldTrendsApp();
            
            expect(app.elements.searchInput).toBeDefined();
            expect(app.elements.searchBtn).toBeDefined();
            expect(app.validateEssentialElements()).toBe(true);
        });

        test('should handle missing DOM elements gracefully', () => {
            // Remove essential elements
            global.document.getElementById.mockReturnValue(null);
            
            app = new WorldTrendsApp();
            
            expect(app.validateEssentialElements()).toBe(false);
            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining('Missing essential elements')
            );
        });

        test('should register search event listeners properly', () => {
            app = new WorldTrendsApp();
            
            expect(mockElements.searchBtn.addEventListener).toHaveBeenCalledWith(
                'click', expect.any(Function)
            );
            expect(mockElements.searchInput.addEventListener).toHaveBeenCalledWith(
                'keypress', expect.any(Function)
            );
        });

        test('should validate search input correctly', async () => {
            app = new WorldTrendsApp();
            
            // Test empty keyword
            mockElements.searchInput.value = '';
            await app.handleSearch();
            
            expect(app.showError).toHaveBeenCalledWith('Please enter a keyword to search');
            expect(mockElements.searchInput.focus).toHaveBeenCalled();
        });

        test('should validate minimum character length', async () => {
            app = new WorldTrendsApp();
            
            // Test short keyword
            mockElements.searchInput.value = 'a';
            await app.handleSearch();
            
            expect(app.showError).toHaveBeenCalledWith('Please enter at least 2 characters');
        });

        test('should prevent multiple simultaneous searches', async () => {
            app = new WorldTrendsApp();
            app.isLoading = true;
            
            const consoleSpy = jest.spyOn(console, 'log');
            await app.handleSearch();
            
            expect(consoleSpy).toHaveBeenCalledWith('Search already in progress...');
        });

        test('should call API with correct parameters', async () => {
            app = new WorldTrendsApp();
            mockElements.searchInput.value = 'test keyword';
            mockElements.countrySelect.value = 'US';
            
            // Mock successful API response
            global.trendsAPI.searchTrends.mockResolvedValue({
                keyword: 'test keyword',
                timestamp: new Date().toISOString(),
                interest_over_time: [],
                interest_by_region: []
            });
            
            await app.handleSearch();
            
            expect(global.trendsAPI.searchTrends).toHaveBeenCalledWith('test keyword', 'US');
        });

        test('should handle API timeout correctly', async () => {
            app = new WorldTrendsApp();
            mockElements.searchInput.value = 'test';
            
            // Mock timeout
            global.trendsAPI.searchTrends.mockImplementation(() => 
                new Promise(resolve => setTimeout(resolve, 35000))
            );
            
            await app.handleSearch();
            
            expect(app.showError).toHaveBeenCalledWith(
                expect.stringContaining('Search timeout')
            );
        });

        test('should save successful search to localStorage', async () => {
            app = new WorldTrendsApp();
            mockElements.searchInput.value = 'test keyword';
            
            global.trendsAPI.searchTrends.mockResolvedValue({
                keyword: 'test keyword',
                timestamp: new Date().toISOString(),
                interest_over_time: [],
                interest_by_region: []
            });
            
            await app.handleSearch();
            
            expect(localStorage.setItem).toHaveBeenCalledWith(
                'lastSearch',
                expect.stringContaining('test keyword')
            );
        });

        test('should restore last search from localStorage', () => {
            const lastSearch = {
                keyword: 'restored keyword',
                geo: 'US',
                timestamp: Date.now() - 1000 // 1 second ago
            };
            
            localStorage.getItem.mockReturnValue(JSON.stringify(lastSearch));
            
            app = new WorldTrendsApp();
            app.restoreLastSearch();
            
            expect(mockElements.searchInput.value).toBe('restored keyword');
            expect(console.log).toHaveBeenCalledWith(
                '🔄 Restored last search:', 'restored keyword'
            );
        });

        test('should not restore old search from localStorage', () => {
            const oldSearch = {
                keyword: 'old keyword',
                geo: 'US',
                timestamp: Date.now() - 4000000 // Over 1 hour ago
            };
            
            localStorage.getItem.mockReturnValue(JSON.stringify(oldSearch));
            
            app = new WorldTrendsApp();
            app.restoreLastSearch();
            
            expect(mockElements.searchInput.value).not.toBe('old keyword');
        });

        test('should handle localStorage errors gracefully', () => {
            localStorage.getItem.mockImplementation(() => {
                throw new Error('localStorage error');
            });
            
            app = new WorldTrendsApp();
            app.restoreLastSearch();
            
            expect(console.warn).toHaveBeenCalledWith(
                'Could not restore last search:', expect.any(Error)
            );
        });

        test('should display version number correctly', () => {
            const mockHeader = {
                appendChild: jest.fn(),
                style: {}
            };
            global.document.querySelector.mockReturnValue(mockHeader);
            
            app = new WorldTrendsApp();
            app.displayVersion();
            
            expect(mockHeader.appendChild).toHaveBeenCalled();
            expect(mockHeader.style.position).toBe('relative');
        });
    });

    describe('Error Handling Tests', () => {
        test('should show error with fallback alert when error elements missing', () => {
            global.alert = jest.fn();
            
            app = new WorldTrendsApp();
            app.elements.errorText = null;
            app.elements.errorMessage = null;
            
            app.showError('Test error');
            
            expect(global.alert).toHaveBeenCalledWith('Error: Test error');
        });

        test('should auto-hide error after timeout', (done) => {
            jest.useFakeTimers();
            
            app = new WorldTrendsApp();
            app.showError('Test error');
            
            expect(mockElements.errorMessage.style.display).toBe('flex');
            
            // Fast-forward time
            jest.advanceTimersByTime(8000);
            
            setTimeout(() => {
                expect(mockElements.errorMessage.style.display).toBe('none');
                jest.useRealTimers();
                done();
            }, 0);
        });

        test('should handle API errors gracefully', async () => {
            app = new WorldTrendsApp();
            mockElements.searchInput.value = 'test';
            
            global.trendsAPI.searchTrends.mockRejectedValue(new Error('API Error'));
            
            await app.handleSearch();
            
            expect(app.showError).toHaveBeenCalledWith(
                'Search failed: API Error'
            );
        });
    });

    describe('Loading State Tests', () => {
        test('should set loading state correctly', () => {
            app = new WorldTrendsApp();
            
            app.setLoading(true);
            
            expect(mockElements.searchBtn.disabled).toBe(true);
            expect(mockElements.searchBtn.innerHTML).toContain('Searching...');
            expect(mockElements.loadingIndicator.style.display).toBe('block');
        });

        test('should clear loading state correctly', () => {
            app = new WorldTrendsApp();
            
            app.setLoading(false);
            
            expect(mockElements.searchBtn.disabled).toBe(false);
            expect(mockElements.searchBtn.innerHTML).toContain('Search');
            expect(mockElements.loadingIndicator.style.display).toBe('none');
        });
    });

    describe('Integration Tests', () => {
        test('should complete full search workflow', async () => {
            app = new WorldTrendsApp();
            
            // Setup search
            mockElements.searchInput.value = 'integration test';
            
            // Mock API response
            const mockResponse = {
                keyword: 'integration test',
                timestamp: new Date().toISOString(),
                interest_over_time: [{ date: '2025-07-15', value: 50 }],
                interest_by_region: [{ geoName: 'United States', geoCode: 'US', value: 75 }],
                related_queries: { top: [], rising: [] }
            };
            
            global.trendsAPI.searchTrends.mockResolvedValue(mockResponse);
            
            // Execute search
            await app.handleSearch();
            
            // Verify workflow
            expect(global.trendsAPI.searchTrends).toHaveBeenCalled();
            expect(app.currentData).toEqual(mockResponse);
            expect(localStorage.setItem).toHaveBeenCalled();
            expect(mockElements.resultsSection.style.display).toBe('block');
        });
    });
});

// Export for test runner
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { setupMockDOM };
}