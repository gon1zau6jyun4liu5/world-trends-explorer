/**
 * Unit Tests for World Trends Explorer v1.0.3
 * Tests for core functionality and map visualization
 */

describe('World Trends Explorer Unit Tests', () => {
    
    // Test API functionality
    describe('TrendsAPI', () => {
        let api;
        
        beforeEach(() => {
            api = new TrendsAPI();
        });
        
        afterEach(() => {
            api.clearCache();
        });
        
        it('should initialize with correct base URL', () => {
            expect(api.baseURL).toBe('http://localhost:5000/api/trends');
        });
        
        it('should cache search results', async () => {
            const mockData = { keyword: 'test', timestamp: Date.now() };
            api.setCache('test_key', mockData);
            
            const cachedData = api.getCached('test_key');
            expect(cachedData).toEqual(mockData);
        });
        
        it('should clear expired cache', () => {
            const oldData = { keyword: 'old', timestamp: Date.now() - 10000 };
            api.setCache('old_key', oldData);
            
            const cachedData = api.getCached('old_key', 5000); // 5 second max age
            expect(cachedData).toBeNull();
        });
        
        it('should validate search parameters', async () => {
            try {
                await api.searchTrends(''); // Empty keyword
                fail('Should throw error for empty keyword');
            } catch (error) {
                expect(error.message).toContain('required');
            }
        });
    });
    
    // Test World Map functionality  
    describe('WorldMap', () => {
        let worldMap;
        let mockContainer;
        
        beforeEach(() => {
            // Create mock DOM elements
            mockContainer = document.createElement('svg');
            mockContainer.id = 'worldMap';
            document.body.appendChild(mockContainer);
            
            // Mock D3 selection
            global.d3 = {
                select: jest.fn(() => ({
                    attr: jest.fn().mockReturnThis(),
                    style: jest.fn().mockReturnThis()
                })),
                geoNaturalEarth1: jest.fn(() => ({
                    scale: jest.fn().mockReturnThis(),
                    translate: jest.fn().mockReturnThis()
                })),
                geoPath: jest.fn(() => jest.fn()),
                scaleThreshold: jest.fn(() => ({
                    domain: jest.fn().mockReturnThis(),
                    range: jest.fn().mockReturnThis()
                }))
            };
            
            worldMap = new WorldMap('worldMap');
        });
        
        afterEach(() => {
            document.body.removeChild(mockContainer);
        });
        
        it('should initialize with correct dimensions', () => {
            expect(worldMap.width).toBe(800);
            expect(worldMap.height).toBe(400);
        });
        
        it('should update data correctly', () => {
            const mockData = {
                keyword: 'test',
                interest_by_region: [
                    { geoCode: 'US', geoName: 'United States', value: 100 },
                    { geoCode: 'GB', geoName: 'United Kingdom', value: 75 }
                ]
            };
            
            worldMap.updateData(mockData);
            expect(worldMap.data).toEqual(mockData);
        });
    });
    
    // Test App functionality
    describe('WorldTrendsApp', () => {
        let app;
        let mockElements;
        
        beforeEach(() => {
            // Mock DOM elements
            mockElements = {
                searchInput: { value: '', addEventListener: jest.fn() },
                searchBtn: { addEventListener: jest.fn(), disabled: false },
                countrySelect: { value: '', options: [] },
                resultsSection: { style: { display: 'none' } },
                loadingIndicator: { style: { display: 'none' } },
                errorMessage: { style: { display: 'none' } },
                errorText: { textContent: '' }
            };
            
            // Mock document.getElementById
            global.document.getElementById = jest.fn((id) => mockElements[id]);
            
            // Mock API
            global.trendsAPI = {
                searchTrends: jest.fn(),
                getTrendingSearches: jest.fn(),
                healthCheck: jest.fn(),
                clearCache: jest.fn()
            };
            
            app = new WorldTrendsApp();
        });
        
        it('should validate search input', async () => {
            mockElements.searchInput.value = '';
            
            const showErrorSpy = jest.spyOn(app, 'showError');
            await app.handleSearch();
            
            expect(showErrorSpy).toHaveBeenCalledWith('Please enter a keyword to search');
        });
        
        it('should handle country selection correctly', () => {
            const countryDetail = {
                code: 'US',
                name: 'United States'
            };
            
            app.handleCountrySelection(countryDetail);
            expect(app.selectedCountry?.code).toBe('US');
        });
    });
    
    // Test Utility Functions
    describe('TrendsUtils', () => {
        it('should format dates correctly', () => {
            const date = '2025-07-12T15:30:00Z';
            const formatted = TrendsUtils.formatDate(date);
            
            expect(formatted).toMatch(/Jul 12, 2025/);
        });
        
        it('should truncate text correctly', () => {
            const longText = 'This is a very long text that should be truncated';
            const truncated = TrendsUtils.truncateText(longText, 20);
            
            expect(truncated.length).toBeLessThanOrEqual(20);
            expect(truncated).toContain('...');
        });
        
        it('should sort data by value', () => {
            const data = [
                { name: 'A', value: 10 },
                { name: 'B', value: 30 },
                { name: 'C', value: 20 }
            ];
            
            const sorted = TrendsUtils.sortByValue(data, 'value', true);
            
            expect(sorted[0].name).toBe('B'); // Highest value
            expect(sorted[2].name).toBe('A'); // Lowest value
        });
        
        it('should filter by minimum value', () => {
            const data = [
                { name: 'A', value: 5 },
                { name: 'B', value: 15 },
                { name: 'C', value: 1 }
            ];
            
            const filtered = TrendsUtils.filterByMinValue(data, 'value', 10);
            
            expect(filtered.length).toBe(1);
            expect(filtered[0].name).toBe('B');
        });
        
        it('should generate intensity colors', () => {
            expect(TrendsUtils.getIntensityColor(0)).toBe('#e1e5e9'); // No data
            expect(TrendsUtils.getIntensityColor(100)).toMatch(/^#[0-9a-f]{6}$/i); // Valid hex color
        });
    });
    
    // Integration Tests
    describe('Integration Tests', () => {
        it('should handle complete search workflow', async () => {
            // Mock successful API response
            const mockResponse = {
                keyword: 'test',
                interest_over_time: [
                    { date: '2025-07-01', value: 50 },
                    { date: '2025-07-02', value: 75 }
                ],
                interest_by_region: [
                    { geoCode: 'US', geoName: 'United States', value: 100 }
                ]
            };
            
            global.trendsAPI.searchTrends.mockResolvedValue(mockResponse);
            
            const app = new WorldTrendsApp();
            app.elements.searchInput.value = 'test';
            
            await app.handleSearch();
            
            expect(app.currentData).toEqual(mockResponse);
            expect(global.trendsAPI.searchTrends).toHaveBeenCalledWith('test', '');
        });
        
        it('should handle API errors gracefully', async () => {
            global.trendsAPI.searchTrends.mockRejectedValue(new Error('API Error'));
            
            const app = new WorldTrendsApp();
            const showErrorSpy = jest.spyOn(app, 'showError');
            
            app.elements.searchInput.value = 'test';
            await app.handleSearch();
            
            expect(showErrorSpy).toHaveBeenCalledWith(
                expect.stringContaining('API Error')
            );
        });
    });
    
    // Performance Tests
    describe('Performance Tests', () => {
        it('should debounce function calls', (done) => {
            const mockFn = jest.fn();
            const debouncedFn = TrendsUtils.debounce(mockFn, 100);
            
            // Call multiple times quickly
            debouncedFn();
            debouncedFn();
            debouncedFn();
            
            // Should only call once after delay
            setTimeout(() => {
                expect(mockFn).toHaveBeenCalledTimes(1);
                done();
            }, 150);
        });
        
        it('should handle large datasets efficiently', () => {
            const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
                name: `Country ${i}`,
                value: Math.random() * 100
            }));
            
            const start = performance.now();
            const sorted = TrendsUtils.sortByValue(largeDataset, 'value', true);
            const end = performance.now();
            
            expect(sorted.length).toBe(1000);
            expect(end - start).toBeLessThan(100); // Should complete in under 100ms
        });
    });
});

// Test Runner Configuration
const testConfig = {
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
    collectCoverageFrom: [
        'frontend/js/**/*.js',
        '!frontend/js/**/*.test.js'
    ],
    coverageThreshold: {
        global: {
            branches: 80,
            functions: 80,
            lines: 80,
            statements: 80
        }
    }
};

// Export test configuration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = testConfig;
}
