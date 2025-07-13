// tests/frontend/setup.js - Jest Setup for Frontend Tests

// Mock external libraries that are loaded via CDN
global.Chart = {
    register: jest.fn(),
    defaults: {
        font: {},
        elements: {}
    }
};

// Mock D3.js
global.d3 = {
    select: jest.fn(() => ({
        attr: jest.fn(),
        style: jest.fn(),
        append: jest.fn(),
        selectAll: jest.fn(),
        data: jest.fn(),
        enter: jest.fn(),
        exit: jest.fn(),
        remove: jest.fn(),
        on: jest.fn(),
        transition: jest.fn(),
        duration: jest.fn()
    })),
    scaleThreshold: jest.fn(() => ({
        domain: jest.fn(),
        range: jest.fn()
    })),
    geoNaturalEarth1: jest.fn(() => ({
        scale: jest.fn(),
        translate: jest.fn()
    })),
    geoPath: jest.fn(() => jest.fn())
};

// Mock TopoJSON
global.topojson = {
    feature: jest.fn(() => ({
        features: []
    }))
};

// Mock DOM methods
Object.defineProperty(window, 'location', {
    value: {
        href: 'http://localhost:3000'
    },
    writable: true
});

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock console methods to reduce noise in tests
global.console = {
    ...console,
    log: jest.fn(),
    warn: jest.fn(),
    error: jest.fn()
};

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn()
}));

// Mock localStorage
const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};
global.localStorage = localStorageMock;

// Mock sessionStorage
global.sessionStorage = localStorageMock;

// Setup custom matchers for DOM testing
expect.extend({
    toHaveClass(received, className) {
        const pass = received.classList.contains(className);
        if (pass) {
            return {
                message: () => `expected ${received} not to have class ${className}`,
                pass: true
            };
        } else {
            return {
                message: () => `expected ${received} to have class ${className}`,
                pass: false
            };
        }
    }
});

// Clean up after each test
afterEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = '';
});