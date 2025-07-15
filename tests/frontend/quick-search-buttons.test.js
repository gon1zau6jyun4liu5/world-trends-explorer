/**
 * Unit Tests for Quick Search Buttons v1.2.4
 * Tests for Issue #33 - Quick Search Buttons Enhancement
 */

// Mock DOM setup for testing
function setupQuickSearchMockDOM() {
    // Create mock quick search buttons
    const mockButtons = [
        { keyword: 'artificial intelligence', category: 'tech', element: null },
        { keyword: '인공지능', category: 'tech', element: null },
        { keyword: 'climate change', category: 'environment', element: null },
        { keyword: 'olympics 2024', category: 'sports', element: null },
        { keyword: 'cryptocurrency', category: 'finance', element: null }
    ];

    // Create mock DOM elements
    const mockElements = {
        searchInput: { 
            value: '', 
            addEventListener: jest.fn(), 
            focus: jest.fn(),
            style: {}
        },
        searchBtn: { 
            addEventListener: jest.fn(), 
            disabled: false, 
            innerHTML: '' 
        },
        quickBtns: mockButtons.map((btn, index) => ({
            dataset: { keyword: btn.keyword, category: btn.category },
            getAttribute: jest.fn((attr) => {
                if (attr === 'data-keyword') return btn.keyword;
                if (attr === 'data-category') return btn.category;
                return null;
            }),
            addEventListener: jest.fn(),
            classList: { add: jest.fn(), remove: jest.fn(), contains: jest.fn(() => false) },
            style: {},
            innerHTML: `<span class="btn-icon">🤖</span><span class="btn-text">${btn.keyword}</span>`,
            replaceWith: jest.fn(function(newNode) { return this; }),
            cloneNode: jest.fn(function() { return this; })
        })),
        globalTrendingGrid: { innerHTML: '' },
        loadingIndicator: { style: { display: 'none' } },
        errorMessage: { style: { display: 'none' } },
        errorText: { textContent: '' }
    };

    // Mock document methods
    global.document = {
        getElementById: jest.fn((id) => {
            if (id === 'searchInput') return mockElements.searchInput;
            if (id === 'searchBtn') return mockElements.searchBtn;
            return mockElements[id] || null;
        }),
        querySelectorAll: jest.fn((selector) => {
            if (selector === '.quick-btn') return mockElements.quickBtns;
            return [];
        }),
        querySelector: jest.fn(() => ({ appendChild: jest.fn(), style: {} })),
        addEventListener: jest.fn(),
        createElement: jest.fn(() => ({
            id: '',
            style: { cssText: '' },
            textContent: '',
            appendChild: jest.fn()
        }))
    };

    return { mockElements, mockButtons };
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

describe('Quick Search Buttons v1.2.4 - Issue #33 Fix Tests', () => {
    let app;
    let mockElements;
    let mockButtons;

    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();
        
        // Setup mock DOM
        const setup = setupQuickSearchMockDOM();
        mockElements = setup.mockElements;
        mockButtons = setup.mockButtons;
        
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

    describe('Issue #33: Quick Search Button Enhancement', () => {
        test('should initialize quick search buttons correctly', () => {
            app = new WorldTrendsApp();
            
            expect(app.elements.quickBtns).toBeDefined();
            expect(app.elements.quickBtns.length).toBeGreaterThan(0);
            expect(console.log).toHaveBeenCalledWith(
                expect.stringContaining('Set up')
            );
        });

        test('should setup event listeners for all quick buttons', () => {
            app = new WorldTrendsApp();
            
            // Verify each button has event listeners
            mockElements.quickBtns.forEach(btn => {
                expect(btn.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
                expect(btn.addEventListener).toHaveBeenCalledWith('mouseenter', expect.any(Function));
                expect(btn.addEventListener).toHaveBeenCalledWith('mouseleave', expect.any(Function));
                expect(btn.addEventListener).toHaveBeenCalledWith('touchstart', expect.any(Function));
                expect(btn.addEventListener).toHaveBeenCalledWith('touchend', expect.any(Function));
            });
        });

        test('should handle quick button click correctly', async () => {
            app = new WorldTrendsApp();
            
            // Mock successful API response
            global.trendsAPI.searchTrends.mockResolvedValue({
                keyword: 'artificial intelligence',
                timestamp: new Date().toISOString(),
                interest_over_time: [],
                interest_by_region: []
            });
            
            // Simulate button click
            const button = mockElements.quickBtns[0];
            const keyword = button.dataset.keyword;
            
            await app.handleQuickSearch(keyword, button, 'tech');
            
            expect(mockElements.searchInput.value).toBe(keyword);
            expect(global.trendsAPI.searchTrends).toHaveBeenCalledWith(keyword, '');
        });

        test('should set button loading state correctly', () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            // Test loading state
            app.setQuickButtonLoading(button, true);
            
            expect(button.classList.add).toHaveBeenCalledWith('loading');
            expect(button.style.pointerEvents).toBe('none');
            expect(button.style.opacity).toBe('0.7');
            expect(button.innerHTML).toContain('Loading...');
            
            // Test normal state
            button.dataset.originalContent = 'original content';
            app.setQuickButtonLoading(button, false);
            
            expect(button.classList.remove).toHaveBeenCalledWith('loading');
            expect(button.style.pointerEvents).toBe('');
            expect(button.style.opacity).toBe('');
        });

        test('should handle quick search success feedback', () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            app.showQuickSearchSuccess(button, 'test keyword');
            
            expect(button.style.background).toBe('linear-gradient(135deg, #28a745 0%, #20c997 100%)');
            expect(button.style.color).toBe('white');
            expect(console.log).toHaveBeenCalledWith(
                expect.stringContaining('Quick search successful')
            );
        });

        test('should handle quick search error feedback', () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            app.showQuickSearchError(button, 'Test error');
            
            expect(button.style.background).toBe('linear-gradient(135deg, #dc3545 0%, #e74c3c 100%)');
            expect(button.style.color).toBe('white');
            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining('Quick search failed')
            );
        });

        test('should handle missing keyword gracefully', async () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            // Remove keyword data
            button.dataset.keyword = '';
            button.getAttribute = jest.fn(() => '');
            
            await app.handleQuickSearch('', button, 'tech');
            
            expect(global.trendsAPI.searchTrends).not.toHaveBeenCalled();
        });

        test('should handle API errors in quick search', async () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            // Mock API error
            global.trendsAPI.searchTrends.mockRejectedValue(new Error('API Error'));
            
            await app.handleQuickSearch('test keyword', button, 'tech');
            
            expect(console.error).toHaveBeenCalledWith(
                'Quick search failed:', expect.any(Error)
            );
        });

        test('should handle Korean keywords correctly', async () => {
            app = new WorldTrendsApp();
            const koreanButton = mockElements.quickBtns[1]; // 인공지능 button
            
            global.trendsAPI.searchTrends.mockResolvedValue({
                keyword: '인공지능',
                timestamp: new Date().toISOString(),
                interest_over_time: [],
                interest_by_region: []
            });
            
            await app.handleQuickSearch('인공지능', koreanButton, 'tech');
            
            expect(mockElements.searchInput.value).toBe('인공지능');
            expect(global.trendsAPI.searchTrends).toHaveBeenCalledWith('인공지능', '');
        });

        test('should handle multiple simultaneous quick searches', async () => {
            app = new WorldTrendsApp();
            const button1 = mockElements.quickBtns[0];
            const button2 = mockElements.quickBtns[2];
            
            global.trendsAPI.searchTrends.mockResolvedValue({
                keyword: 'test',
                timestamp: new Date().toISOString(),
                interest_over_time: [],
                interest_by_region: []
            });
            
            // Simulate simultaneous clicks
            const promise1 = app.handleQuickSearch('keyword1', button1, 'tech');
            const promise2 = app.handleQuickSearch('keyword2', button2, 'environment');
            
            await Promise.all([promise1, promise2]);
            
            // Should handle both searches
            expect(global.trendsAPI.searchTrends).toHaveBeenCalledTimes(2);
        });

        test('should add visual feedback to search input', async () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            global.trendsAPI.searchTrends.mockResolvedValue({
                keyword: 'test',
                timestamp: new Date().toISOString(),
                interest_over_time: [],
                interest_by_region: []
            });
            
            await app.handleQuickSearch('test keyword', button, 'tech');
            
            expect(mockElements.searchInput.style.borderColor).toBe('#667eea');
            expect(mockElements.searchInput.style.boxShadow).toBe('0 0 0 3px rgba(102, 126, 234, 0.1)');
        });

        test('should handle category-based analytics', async () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            global.trendsAPI.searchTrends.mockResolvedValue({
                keyword: 'test',
                timestamp: new Date().toISOString(),
                interest_over_time: [],
                interest_by_region: []
            });
            
            await app.handleQuickSearch('test keyword', button, 'tech');
            
            expect(console.log).toHaveBeenCalledWith(
                expect.stringContaining('Quick search analytics: Category=tech')
            );
        });
    });

    describe('Button Interaction Tests', () => {
        test('should handle hover effects correctly', () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            // Get the hover event handlers
            const hoverEnterHandler = button.addEventListener.mock.calls
                .find(call => call[0] === 'mouseenter')[1];
            const hoverLeaveHandler = button.addEventListener.mock.calls
                .find(call => call[0] === 'mouseleave')[1];
            
            // Test hover enter
            hoverEnterHandler();
            expect(button.style.transform).toBe('translateY(-3px)');
            
            // Test hover leave
            hoverLeaveHandler();
            expect(button.style.transform).toBe('');
        });

        test('should handle touch events correctly', () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            // Get the touch event handlers
            const touchStartHandler = button.addEventListener.mock.calls
                .find(call => call[0] === 'touchstart')[1];
            const touchEndHandler = button.addEventListener.mock.calls
                .find(call => call[0] === 'touchend')[1];
            
            // Test touch start
            touchStartHandler({ preventDefault: jest.fn() });
            expect(button.style.transform).toBe('translateY(-2px)');
            
            // Test touch end
            touchEndHandler({ preventDefault: jest.fn() });
            // Transform should be reset after timeout
        });

        test('should prevent default on touch events', () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            const mockEvent = { preventDefault: jest.fn(), stopPropagation: jest.fn() };
            
            // Get the click handler
            const clickHandler = button.addEventListener.mock.calls
                .find(call => call[0] === 'click')[1];
            
            clickHandler(mockEvent);
            
            expect(mockEvent.preventDefault).toHaveBeenCalled();
            expect(mockEvent.stopPropagation).toHaveBeenCalled();
        });
    });

    describe('Error Handling Tests', () => {
        test('should handle missing button element gracefully', () => {
            app = new WorldTrendsApp();
            
            // Test with null button
            expect(() => {
                app.setQuickButtonLoading(null, true);
            }).not.toThrow();
            
            expect(() => {
                app.showQuickSearchSuccess(null, 'test');
            }).not.toThrow();
            
            expect(() => {
                app.showQuickSearchError(null, 'test error');
            }).not.toThrow();
        });

        test('should handle quick buttons not found scenario', () => {
            // Mock empty quick buttons
            global.document.querySelectorAll = jest.fn(() => []);
            
            app = new WorldTrendsApp();
            
            expect(console.warn).toHaveBeenCalledWith(
                expect.stringContaining('Quick search buttons not found')
            );
        });

        test('should handle malformed button data', async () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            // Remove all keyword data
            button.dataset = {};
            button.getAttribute = jest.fn(() => null);
            
            await app.handleQuickSearch('', button, 'tech');
            
            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining('No keyword found')
            );
        });
    });

    describe('Integration Tests', () => {
        test('should complete full quick search workflow', async () => {
            app = new WorldTrendsApp();
            
            // Setup complete mock response
            const mockResponse = {
                keyword: 'artificial intelligence',
                timestamp: new Date().toISOString(),
                interest_over_time: [{ date: '2025-07-15', value: 50 }],
                interest_by_region: [{ geoName: 'United States', geoCode: 'US', value: 75 }],
                related_queries: { top: [], rising: [] }
            };
            
            global.trendsAPI.searchTrends.mockResolvedValue(mockResponse);
            
            // Simulate quick button click workflow
            const button = mockElements.quickBtns[0];
            const keyword = button.dataset.keyword;
            
            await app.handleQuickSearch(keyword, button, 'tech');
            
            // Verify complete workflow
            expect(mockElements.searchInput.value).toBe(keyword);
            expect(global.trendsAPI.searchTrends).toHaveBeenCalledWith(keyword, '');
            expect(app.currentData).toEqual(mockResponse);
        });

        test('should maintain button state during search', async () => {
            app = new WorldTrendsApp();
            const button = mockElements.quickBtns[0];
            
            // Mock slow API response
            global.trendsAPI.searchTrends.mockImplementation(() => 
                new Promise(resolve => setTimeout(() => resolve({
                    keyword: 'test',
                    timestamp: new Date().toISOString(),
                    interest_over_time: [],
                    interest_by_region: []
                }), 100))
            );
            
            const searchPromise = app.handleQuickSearch('test', button, 'tech');
            
            // Check loading state is set
            expect(button.classList.add).toHaveBeenCalledWith('loading');
            
            await searchPromise;
            
            // Check loading state is eventually removed
            setTimeout(() => {
                expect(button.classList.remove).toHaveBeenCalledWith('loading');
            }, 1100);
        });
    });
});

// Export for test runner
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { setupQuickSearchMockDOM };
}