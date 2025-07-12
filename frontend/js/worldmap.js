/**
 * World Map Component for World Trends Explorer
 * Interactive SVG world map using D3.js and TopoJSON
 */

class WorldMap {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = d3.select(`#${containerId}`);
        this.tooltip = d3.select('#mapTooltip');
        
        // Configuration
        this.width = options.width || 800;
        this.height = options.height || 400;
        this.data = null;
        this.worldData = null;
        
        // Color scale for intensity
        this.colorScale = d3.scaleThreshold()
            .domain([1, 20, 40, 60, 80, 100])
            .range(['#e1e5e9', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c']);
        
        // Initialize map
        this.init();
    }

    async init() {
        try {
            // Set up SVG
            this.svg = this.container
                .attr('width', '100%')
                .attr('height', '100%')
                .attr('viewBox', `0 0 ${this.width} ${this.height}`)
                .style('background-color', '#f8f9fa');

            // Set up projection
            this.projection = d3.geoNaturalEarth1()
                .scale(130)
                .translate([this.width / 2, this.height / 2]);

            this.path = d3.geoPath().projection(this.projection);

            // Load world data
            await this.loadWorldData();
            
            // Draw initial map
            this.drawMap();
            
            console.log('World map initialized successfully');
        } catch (error) {
            console.error('Error initializing world map:', error);
        }
    }

    async loadWorldData() {
        try {
            // Load world topology data from public CDN
            const response = await fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json');
            const world = await response.json();
            
            this.worldData = topojson.feature(world, world.objects.countries);
            console.log('World data loaded successfully');
        } catch (error) {
            console.error('Error loading world data:', error);
            // Fallback: create simple world data
            this.createFallbackMap();
        }
    }

    createFallbackMap() {
        // Simple fallback rectangle representing world
        this.svg.append('rect')
            .attr('x', 50)
            .attr('y', 50)
            .attr('width', this.width - 100)
            .attr('height', this.height - 100)
            .attr('fill', '#e1e5e9')
            .attr('stroke', '#ccc')
            .attr('stroke-width', 1);
        
        this.svg.append('text')
            .attr('x', this.width / 2)
            .attr('y', this.height / 2)
            .attr('text-anchor', 'middle')
            .attr('fill', '#666')
            .text('World Map (Loading...)');
    }

    drawMap() {
        if (!this.worldData) {
            console.warn('World data not loaded');
            return;
        }

        // Clear existing map
        this.svg.selectAll('.country').remove();

        // Draw countries
        this.svg.selectAll('.country')
            .data(this.worldData.features)
            .enter()
            .append('path')
            .attr('class', 'country')
            .attr('d', this.path)
            .attr('fill', '#e1e5e9')
            .attr('stroke', '#fff')
            .attr('stroke-width', 0.5)
            .style('cursor', 'pointer')
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mousemove', (event, d) => this.moveTooltip(event, d))
            .on('mouseout', () => this.hideTooltip())
            .on('click', (event, d) => this.onCountryClick(d));
    }

    updateData(trendsData) {
        this.data = trendsData;
        
        if (!this.worldData) {
            console.warn('World data not loaded yet');
            return;
        }

        // Create country code to data mapping
        const dataMap = new Map();
        if (trendsData && trendsData.interest_by_region) {
            trendsData.interest_by_region.forEach(item => {
                if (item.geoCode && item.value > 0) {
                    dataMap.set(item.geoCode, {
                        value: item.value,
                        name: item.geoName
                    });
                }
            });
        }

        // Update country colors based on data
        this.svg.selectAll('.country')
            .transition()
            .duration(750)
            .attr('fill', (d) => {
                const countryCode = this.getCountryCode(d);
                const countryData = dataMap.get(countryCode);
                
                if (countryData) {
                    return this.colorScale(countryData.value);
                }
                return '#e1e5e9'; // Default color for no data
            })
            .attr('class', (d) => {
                const countryCode = this.getCountryCode(d);
                const countryData = dataMap.get(countryCode);
                return countryData ? 'country has-data' : 'country';
            });
    }

    getCountryCode(countryFeature) {
        // Try to get country code from properties
        if (countryFeature.properties) {
            return countryFeature.properties.ISO_A2 || 
                   countryFeature.properties.iso_a2 ||
                   countryFeature.properties.ADM0_A3 ||
                   countryFeature.properties.SOV_A3;
        }
        return null;
    }

    getCountryName(countryFeature) {
        if (countryFeature.properties) {
            return countryFeature.properties.NAME || 
                   countryFeature.properties.name ||
                   countryFeature.properties.NAME_EN ||
                   'Unknown Country';
        }
        return 'Unknown Country';
    }

    showTooltip(event, countryFeature) {
        const countryCode = this.getCountryCode(countryFeature);
        const countryName = this.getCountryName(countryFeature);
        
        let content = `<strong>${countryName}</strong>`;
        
        if (this.data && this.data.interest_by_region) {
            const countryData = this.data.interest_by_region.find(
                item => item.geoCode === countryCode
            );
            
            if (countryData) {
                content += `<br>Interest: ${countryData.value}`;
                content += `<br>Keyword: "${this.data.keyword}"`;
            } else {
                content += '<br>No data available';
            }
        }
        
        this.tooltip
            .html(content)
            .classed('visible', true);
        
        this.moveTooltip(event);
    }

    moveTooltip(event) {
        const containerRect = this.container.node().getBoundingClientRect();
        const x = event.clientX - containerRect.left + 10;
        const y = event.clientY - containerRect.top - 10;
        
        this.tooltip
            .style('left', x + 'px')
            .style('top', y + 'px');
    }

    hideTooltip() {
        this.tooltip.classed('visible', false);
    }

    onCountryClick(countryFeature) {
        const countryCode = this.getCountryCode(countryFeature);
        const countryName = this.getCountryName(countryFeature);
        
        console.log('Country clicked:', countryName, countryCode);
        
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
    }

    resize() {
        const containerRect = this.container.node().getBoundingClientRect();
        this.width = containerRect.width;
        this.height = containerRect.height;
        
        this.svg
            .attr('viewBox', `0 0 ${this.width} ${this.height}`);
        
        this.projection
            .scale(Math.min(this.width, this.height) / 6)
            .translate([this.width / 2, this.height / 2]);
        
        this.svg.selectAll('.country')
            .attr('d', this.path);
    }

    highlightCountry(countryCode) {
        this.svg.selectAll('.country')
            .classed('highlighted', false);
        
        this.svg.selectAll('.country')
            .filter(d => this.getCountryCode(d) === countryCode)
            .classed('highlighted', true)
            .classed('pulse', true);
        
        // Remove pulse after animation
        setTimeout(() => {
            this.svg.selectAll('.country').classed('pulse', false);
        }, 2000);
    }

    reset() {
        this.data = null;
        this.svg.selectAll('.country')
            .transition()
            .duration(500)
            .attr('fill', '#e1e5e9')
            .attr('class', 'country');
    }
}

// Export for global use
window.WorldMap = WorldMap;
