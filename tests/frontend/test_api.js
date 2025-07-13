// tests/frontend/test_api.js - Frontend API Module Tests

// Note: This requires Jest setup - install with: npm install --save-dev jest
// Run with: npm test

import { TrendsAPI, TrendsUtils } from '../../frontend/js/api.js';

describe('TrendsAPI', () => {
    let api;
    
    beforeEach(() => {
        api = new TrendsAPI('http://localhost:5555/api/trends');
    });
    
    describe('makeRequest', () => {
        test('should make HTTP request successfully', async () => {
            // Mock fetch implementation
            global.fetch = jest.fn(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ status: 'healthy' })
                })
            );
            
            const result = await api.makeRequest('/health');
            expect(result.status).toBe('healthy');
        });
        
        test('should handle HTTP errors', async () => {
            global.fetch = jest.fn(() =>
                Promise.resolve({
                    ok: false,
                    status: 404,
                    statusText: 'Not Found'
                })
            );
            
            await expect(api.makeRequest('/notfound')).rejects.toThrow('HTTP 404: Not Found');
        });
        
        test('should timeout after specified duration', async () => {
            api.requestTimeout = 100; // 100ms timeout
            
            global.fetch = jest.fn(() =>
                new Promise(resolve => setTimeout(resolve, 200))
            );
            
            await expect(api.makeRequest('/slow')).rejects.toThrow();
        });
    });
    
    describe('caching', () => {
        test('should cache successful responses', async () => {
            const mockData = { test: 'data' };
            global.fetch = jest.fn(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockData)
                })
            );
            
            // First call
            await api.searchTrends('test');
            // Second call should use cache
            const result = api.getCached('search_test__today 12-m');
            
            expect(result).toEqual(mockData);
        });
        
        test('should expire cache after maxAge', () => {
            const oldData = { old: true };
            api.setCache('test', oldData);
            
            // Simulate time passage
            const cached = api.getCached('test', -1); // Expired
            expect(cached).toBeNull();
        });
    });
    
    describe('searchTrends', () => {
        test('should require keyword parameter', async () => {
            await expect(api.searchTrends('')).rejects.toThrow('Keyword is required');
        });
        
        test('should format parameters correctly', async () => {
            global.fetch = jest.fn(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ keyword: 'test' })
                })
            );
            
            await api.searchTrends('test keyword', 'US', 'today 7-d');
            
            const lastCall = global.fetch.mock.calls[0][0];
            expect(lastCall).toContain('keyword=test%20keyword');
            expect(lastCall).toContain('geo=US');
            expect(lastCall).toContain('timeframe=today%207-d');
        });
    });
});

describe('TrendsUtils', () => {
    describe('formatDate', () => {
        test('should format date string correctly', () => {
            const result = TrendsUtils.formatDate('2025-07-13T10:30:00Z');
            expect(result).toMatch(/Jul 13, 2025/);
        });
        
        test('should handle invalid date strings', () => {
            const result = TrendsUtils.formatDate('invalid');
            expect(result).toBe('invalid');
        });
        
        test('should handle null/undefined dates', () => {
            expect(TrendsUtils.formatDate(null)).toBe('Unknown');
            expect(TrendsUtils.formatDate(undefined)).toBe('Unknown');
        });
    });
    
    describe('truncateText', () => {
        test('should truncate long text', () => {
            const longText = 'This is a very long text that should be truncated';
            const result = TrendsUtils.truncateText(longText, 20);
            expect(result).toBe('This is a very lo...');
        });
        
        test('should not truncate short text', () => {
            const shortText = 'Short text';
            const result = TrendsUtils.truncateText(shortText, 20);
            expect(result).toBe('Short text');
        });
    });
    
    describe('sortByValue', () => {
        test('should sort array by value descending', () => {
            const data = [
                { name: 'A', value: 10 },
                { name: 'B', value: 30 },
                { name: 'C', value: 20 }
            ];
            
            const result = TrendsUtils.sortByValue(data, 'value', true);
            expect(result[0].name).toBe('B');
            expect(result[1].name).toBe('C');
            expect(result[2].name).toBe('A');
        });
    });
    
    describe('isValidTrendsData', () => {
        test('should validate proper trends data', () => {
            const validData = {
                keyword: 'test',
                interest_over_time: [],
                interest_by_region: []
            };
            
            expect(TrendsUtils.isValidTrendsData(validData)).toBe(true);
        });
        
        test('should reject invalid data', () => {
            expect(TrendsUtils.isValidTrendsData(null)).toBe(false);
            expect(TrendsUtils.isValidTrendsData({})).toBe(false);
            expect(TrendsUtils.isValidTrendsData({ keyword: 'test' })).toBe(false);
        });
    });
});