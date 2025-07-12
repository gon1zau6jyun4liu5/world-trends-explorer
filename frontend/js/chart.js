/**
 * Chart Component for World Trends Explorer
 * Handles Chart.js visualizations for trends data
 */

class TrendsChart {
    constructor(canvasId, options = {}) {
        this.canvasId = canvasId;
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.chart = null;
        this.options = {
            responsive: true,
            maintainAspectRatio: false,
            ...options
        };
        
        this.init();
    }

    init() {
        // Default chart configuration
        this.defaultConfig = {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: false
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            boxWidth: 20,
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#667eea',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Date'
                        },
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Interest Level'
                        },
                        min: 0,
                        max: 100,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                elements: {
                    point: {
                        radius: 3,
                        hoverRadius: 6
                    },
                    line: {
                        tension: 0.4,
                        borderWidth: 3
                    }
                }
            }
        };
    }

    /**
     * Create or update chart with trends data
     */
    updateChart(trendsData) {
        if (!trendsData || !trendsData.interest_over_time) {
            this.showNoData();
            return;
        }

        const timeData = trendsData.interest_over_time;
        if (!Array.isArray(timeData) || timeData.length === 0) {
            this.showNoData();
            return;
        }

        // Prepare data
        const labels = timeData.map(item => {
            if (item.date) {
                return TrendsUtils.formatDate(item.date);
            }
            return '';
        });

        const values = timeData.map(item => item.value || 0);

        const dataset = {
            label: `"${trendsData.keyword}" Interest`,
            data: values,
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#667eea',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 8
        };

        const config = {
            ...this.defaultConfig,
            data: {
                labels: labels,
                datasets: [dataset]
            }
        };

        // Update title
        config.options.plugins.title = {
            display: true,
            text: `Trends for "${trendsData.keyword}"`,
            font: {
                size: 16,
                weight: 'bold'
            },
            color: '#333'
        };

        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }

        // Create new chart
        this.chart = new Chart(this.ctx, config);
        
        console.log('Chart updated successfully');
    }

    /**
     * Create comparison chart with multiple keywords
     */
    updateComparisonChart(comparisonData) {
        if (!comparisonData || !comparisonData.comparison_data) {
            this.showNoData();
            return;
        }

        const timeData = comparisonData.comparison_data;
        const keywords = comparisonData.keywords;

        if (!Array.isArray(timeData) || timeData.length === 0 || !Array.isArray(keywords)) {
            this.showNoData();
            return;
        }

        // Prepare labels
        const labels = timeData.map(item => {
            if (item.date) {
                return TrendsUtils.formatDate(item.date);
            }
            return '';
        });

        // Color palette for multiple lines
        const colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c',
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
        ];

        // Create datasets for each keyword
        const datasets = keywords.map((keyword, index) => {
            const color = colors[index % colors.length];
            const values = timeData.map(item => item[keyword] || 0);

            return {
                label: `"${keyword}"`,
                data: values,
                borderColor: color,
                backgroundColor: color + '20',
                fill: false,
                tension: 0.4,
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 6
            };
        });

        const config = {
            ...this.defaultConfig,
            data: {
                labels: labels,
                datasets: datasets
            }
        };

        // Update title
        config.options.plugins.title = {
            display: true,
            text: `Comparison: ${keywords.join(' vs ')}`,
            font: {
                size: 16,
                weight: 'bold'
            },
            color: '#333'
        };

        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }

        // Create new chart
        this.chart = new Chart(this.ctx, config);
        
        console.log('Comparison chart updated successfully');
    }

    /**
     * Show no data message
     */
    showNoData() {
        if (this.chart) {
            this.chart.destroy();
        }

        const config = {
            type: 'line',
            data: {
                labels: ['No Data'],
                datasets: [{
                    label: 'No data available',
                    data: [0],
                    borderColor: '#ccc',
                    backgroundColor: '#f5f5f5'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'No data available',
                        font: {
                            size: 16
                        },
                        color: '#666'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: false
                    }
                }
            }
        };

        this.chart = new Chart(this.ctx, config);
    }

    /**
     * Show loading state
     */
    showLoading() {
        if (this.chart) {
            this.chart.destroy();
        }

        const config = {
            type: 'line',
            data: {
                labels: ['Loading...'],
                datasets: [{
                    label: 'Loading data...',
                    data: [50],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Loading trends data...',
                        font: {
                            size: 16
                        },
                        color: '#667eea'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: false
                    }
                }
            }
        };

        this.chart = new Chart(this.ctx, config);
    }

    /**
     * Resize chart
     */
    resize() {
        if (this.chart) {
            this.chart.resize();
        }
    }

    /**
     * Export chart as image
     */
    exportAsImage(filename = 'trends-chart.png') {
        if (!this.chart) return;

        const link = document.createElement('a');
        link.download = filename;
        link.href = this.chart.toBase64Image();
        link.click();
    }

    /**
     * Get chart data
     */
    getData() {
        if (!this.chart) return null;
        return this.chart.data;
    }

    /**
     * Destroy chart
     */
    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Regional Chart Component for bar charts
class RegionalChart {
    constructor(canvasId, options = {}) {
        this.canvasId = canvasId;
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.warn(`Canvas with id ${canvasId} not found`);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.chart = null;
        this.options = options;
    }

    updateChart(regionalData, keyword = '') {
        if (!regionalData || !Array.isArray(regionalData) || regionalData.length === 0) {
            this.showNoData();
            return;
        }

        // Sort and take top 10
        const sortedData = TrendsUtils.sortByValue(regionalData, 'value', true).slice(0, 10);
        
        const labels = sortedData.map(item => item.geoName || item.country || 'Unknown');
        const values = sortedData.map(item => item.value || 0);
        
        // Generate colors
        const colors = values.map(value => TrendsUtils.getIntensityColor(value));
        
        const config = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Interest Level',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: keyword ? `"${keyword}" by Region` : 'Interest by Region',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Interest Level'
                        }
                    }
                }
            }
        };

        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(this.ctx, config);
    }

    showNoData() {
        if (this.chart) {
            this.chart.destroy();
        }

        const config = {
            type: 'bar',
            data: {
                labels: ['No Data'],
                datasets: [{
                    label: 'No data',
                    data: [0],
                    backgroundColor: '#f5f5f5'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'No regional data available'
                    },
                    legend: {
                        display: false
                    }
                }
            }
        };

        this.chart = new Chart(this.ctx, config);
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Export for global use
window.TrendsChart = TrendsChart;
window.RegionalChart = RegionalChart;
