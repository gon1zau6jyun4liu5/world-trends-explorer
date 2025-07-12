/**
 * World Map Component for World Trends Explorer v1.0.4
 * Interactive SVG world map using D3.js and TopoJSON - Fixed for proper display
 */

class WorldMap {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = d3.select(`#${containerId}`);
        this.tooltip = d3.select('#mapTooltip');
        this.loadingOverlay = d3.select('#mapLoadingOverlay');
        
        // Configuration
        this.width = options.width || 800;
        this.height = options.height || 400;
        this.data = null;
        this.worldData = null;
        this.availableCountries = new Set([
            'US', 'GB', 'DE', 'FR', 'IT', 'ES', 'CA', 'AU', 
            'JP', 'KR', 'IN', 'BR', 'MX', 'RU', 'CN', 'NL',
            'SE', 'NO', 'DK', 'FI', 'BE', 'CH', 'AT', 'IE',
            'PT', 'GR', 'PL', 'CZ', 'HU', 'SK', 'SI', 'HR',
            'BG', 'RO', 'LT', 'LV', 'EE', 'MT', 'CY', 'LU'
        ]);
        
        // Color scale for intensity
        this.colorScale = d3.scaleThreshold()
            .domain([1, 20, 40, 60, 80, 100])
            .range(['#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c']);
        
        // Initialize map
        this.init();
    }

    async init() {
        try {
            console.log('🗺️ Initializing World Map v1.0.4...');
            
            // Show loading overlay
            this.showLoading();
            
            // Set up SVG with proper dimensions
            this.svg = this.container
                .attr('width', '100%')
                .attr('height', '100%')
                .attr('viewBox', `0 0 ${this.width} ${this.height}`)
                .style('background-color', '#f8f9fa');

            // Set up projection with better scaling
            this.projection = d3.geoNaturalEarth1()
                .scale(130)
                .translate([this.width / 2, this.height / 2]);

            this.path = d3.geoPath().projection(this.projection);

            // Load world data
            await this.loadWorldData();
            
            // Draw initial map
            this.drawMap();
            
            // Hide loading overlay
            this.hideLoading();
            
            console.log('✅ World map initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing world map:', error);
            this.showError();
        }
    }

    showLoading() {
        if (this.loadingOverlay.node()) {
            this.loadingOverlay.style('display', 'flex');
        }
    }

    hideLoading() {
        if (this.loadingOverlay.node()) {
            this.loadingOverlay.style('display', 'none');
        }
    }

    showError() {
        this.hideLoading();
        
        // Clear SVG and show error message
        this.svg.selectAll('*').remove();
        
        // Add error message
        this.svg.append('rect')
            .attr('x', 0)
            .attr('y', 0)
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('fill', '#f8f9fa');
        
        this.svg.append('text')
            .attr('x', this.width / 2)
            .attr('y', this.height / 2 - 20)
            .attr('text-anchor', 'middle')
            .attr('fill', '#dc3545')
            .attr('font-size', '16px')
            .attr('font-weight', 'bold')
            .text('⚠️ Failed to load world map');
        
        this.svg.append('text')
            .attr('x', this.width / 2)
            .attr('y', this.height / 2 + 10)
            .attr('text-anchor', 'middle')
            .attr('fill', '#666')
            .attr('font-size', '14px')
            .text('Please refresh the page to try again');
    }

    async loadWorldData() {
        try {
            console.log('📥 Loading world topology data...');
            
            // Load world topology data from CDN with fallback
            const urls = [
                'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json',
                'https://unpkg.com/world-atlas@2/countries-110m.json'
            ];
            
            let world = null;
            for (const url of urls) {
                try {
                    const response = await fetch(url);
                    if (response.ok) {
                        world = await response.json();
                        console.log(`✅ Loaded world data from: ${url}`);
                        break;
                    }
                } catch (err) {
                    console.warn(`Failed to load from ${url}:`, err);
                }
            }
            
            if (!world) {
                throw new Error('Failed to load world data from all sources');
            }
            
            this.worldData = topojson.feature(world, world.objects.countries);
            console.log(`🌍 World data loaded: ${this.worldData.features.length} countries`);
            
        } catch (error) {
            console.error('❌ Error loading world data:', error);
            throw error;
        }
    }

    drawMap() {
        if (!this.worldData) {
            console.warn('World data not loaded');
            return;
        }

        console.log('🎨 Drawing world map...');

        // Clear existing map
        this.svg.selectAll('.country').remove();

        // Draw countries
        this.svg.selectAll('.country')
            .data(this.worldData.features)
            .enter()
            .append('path')
            .attr('class', 'country')
            .attr('d', this.path)
            .attr('fill', (d) => this.getCountryColor(d))
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 0.5)
            .style('cursor', (d) => {
                const countryCode = this.getCountryCode(d);
                return this.availableCountries.has(countryCode) ? 'pointer' : 'default';
            })
            .classed('has-data', (d) => {
                const countryCode = this.getCountryCode(d);
                return this.availableCountries.has(countryCode);
            })
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mousemove', (event, d) => this.moveTooltip(event, d))
            .on('mouseout', () => this.hideTooltip())
            .on('click', (event, d) => this.onCountryClick(d));
        
        console.log(`✅ Map drawn with ${this.worldData.features.length} countries`);
        console.log(`🔵 ${this.availableCountries.size} countries have data available`);
    }

    getCountryColor(countryFeature) {
        const countryCode = this.getCountryCode(countryFeature);
        
        // Check if country has available data
        if (this.availableCountries.has(countryCode)) {
            // Check if we have search result data for this country
            if (this.data && this.data.interest_by_region) {
                const countryData = this.data.interest_by_region.find(
                    item => item.geoCode === countryCode
                );
                
                if (countryData && countryData.value > 0) {
                    return this.colorScale(countryData.value);
                }
            }
            
            return '#667eea'; // Blue for available data
        }
        
        return '#e1e5e9'; // Default gray for no data
    }

    updateData(trendsData) {
        this.data = trendsData;
        
        if (!this.worldData) {
            console.warn('World data not loaded yet');
            return;
        }

        console.log('🔄 Updating map with trends data...');

        // Update country colors based on search data
        this.svg.selectAll('.country')
            .transition()
            .duration(750)
            .attr('fill', (d) => this.getCountryColor(d));
        
        console.log('✅ Map updated with trends data');
    }

    /**
     * Get country code from feature properties
     */
    getCountryCode(countryFeature) {
        if (countryFeature.properties) {
            // Try different property names for country codes
            return countryFeature.properties.ISO_A2 || 
                   countryFeature.properties.iso_a2 ||
                   countryFeature.properties.ADM0_A3 ||
                   countryFeature.properties.SOV_A3 ||
                   countryFeature.properties.ISO_A3;
        }
        return null;
    }

    /**
     * Get country name from feature properties
     */
    getCountryName(countryFeature) {
        if (countryFeature.properties) {
            return countryFeature.properties.NAME || 
                   countryFeature.properties.name ||
                   countryFeature.properties.NAME_EN ||
                   countryFeature.properties.NAME_LONG ||
                   'Unknown Country';
        }
        return 'Unknown Country';
    }

    showTooltip(event, countryFeature) {
        const countryCode = this.getCountryCode(countryFeature);
        const countryName = this.getCountryName(countryFeature);
        
        let content = `<strong>${countryName}</strong>`;
        
        // Check if country has available data
        const hasData = this.availableCountries.has(countryCode);
        
        if (hasData) {
            content += '<br>✅ <span style="color: #28a745;">Click to explore trends</span>';
            
            // Show search data if available
            if (this.data && this.data.interest_by_region) {
                const countryData = this.data.interest_by_region.find(
                    item => item.geoCode === countryCode
                );
                
                if (countryData && countryData.value > 0) {
                    content += `<br>📊 Interest: <strong>${countryData.value}</strong>`;
                    if (this.data.keyword) {
                        content += `<br>🔍 "${this.data.keyword}"`;
                    }
                }
            }
        } else {
            content += '<br>❌ <span style="color: #dc3545;">No data available</span>';
        }
        
        this.tooltip
            .html(content)
            .classed('visible', true);
        
        this.moveTooltip(event);
    }

    moveTooltip(event) {
        if (!this.tooltip.node()) return;
        
        const containerRect = this.container.node().getBoundingClientRect();
        const tooltipRect = this.tooltip.node().getBoundingClientRect();
        
        let x = event.clientX - containerRect.left + 10;
        let y = event.clientY - containerRect.top - 10;
        
        // Keep tooltip within container bounds
        if (x + tooltipRect.width > containerRect.width) {
            x = event.clientX - containerRect.left - tooltipRect.width - 10;
        }
        if (y < 0) {
            y = event.clientY - containerRect.top + 20;
        }
        
        this.tooltip
            .style('left', x + 'px')
            .style('top', y + 'px');
    }

    hideTooltip() {
        if (this.tooltip.node()) {
            this.tooltip.classed('visible', false);
        }
    }

    onCountryClick(countryFeature) {
        const countryCode = this.getCountryCode(countryFeature);
        const countryName = this.getCountryName(countryFeature);
        
        console.log(`🖱️ Country clicked: ${countryName} (${countryCode})`);
        
        // Only allow clicks on countries with data
        if (!this.availableCountries.has(countryCode)) {
            console.warn(`⚠️ No data available for ${countryName} (${countryCode})`);
            
            // Show error message briefly
            if (window.app && window.app.showError) {
                window.app.showError(`No data available for ${countryName}. Try another country.`);
            }
            return;
        }
        
        // Highlight clicked country
        this.svg.selectAll('.country')
            .classed('highlighted', false);
        
        this.svg.selectAll('.country')
            .filter(d => d === countryFeature)
            .classed('highlighted', true);
        
        // Trigger custom event for country selection
        const event = new CustomEvent('countrySelected', {
            detail: {
                code: countryCode,
                name: countryName,
                feature: countryFeature
            }
        });
        document.dispatchEvent(event);
        
        console.log(`✅ Country selection event triggered for ${countryName}`);
    }

    resize() {
        if (!this.container.node()) return;
        
        const containerRect = this.container.node().getBoundingClientRect();
        this.width = containerRect.width || 800;
        this.height = containerRect.height || 400;
        
        this.svg
            .attr('viewBox', `0 0 ${this.width} ${this.height}`);
        
        this.projection
            .scale(Math.min(this.width, this.height) / 6)
            .translate([this.width / 2, this.height / 2]);
        
        this.svg.selectAll('.country')
            .attr('d', this.path);
        
        console.log(`📐 Map resized to ${this.width}x${this.height}`);
    }

    highlightCountry(countryCode) {
        if (!countryCode) return;
        
        console.log(`🎯 Highlighting country: ${countryCode}`);
        
        this.svg.selectAll('.country')
            .classed('highlighted', false);
        
        const highlighted = this.svg.selectAll('.country')
            .filter(d => this.getCountryCode(d) === countryCode)
            .classed('highlighted', true)
            .classed('pulse', true);
        
        if (highlighted.empty()) {
            console.warn(`Country with code ${countryCode} not found on map`);
        }
        
        // Remove pulse after animation
        setTimeout(() => {
            this.svg.selectAll('.country').classed('pulse', false);
        }, 2000);
    }

    reset() {
        this.data = null;
        
        if (this.svg) {
            this.svg.selectAll('.country')
                .transition()
                .duration(500)
                .attr('fill', (d) => this.getCountryColor(d))
                .classed('highlighted', false);
        }
        
        console.log('🔄 Map reset to default state');
    }

    /**
     * Get available countries for testing
     */
    getAvailableCountries() {
        return Array.from(this.availableCountries);
    }

    /**
     * Check if map is ready
     */
    isReady() {
        return this.worldData !== null && this.svg !== null;
    }
}

// Export for global use
window.WorldMap = WorldMap;