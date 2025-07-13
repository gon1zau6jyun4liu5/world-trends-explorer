# 🌍 World Trends Explorer v1.0.6

**Real-time Google Trends explorer with interactive world map and comprehensive testing suite**

![World Trends Explorer](https://img.shields.io/badge/Status-Ready%20to%20Run-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Latest-orange)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-yellow)
![D3.js](https://img.shields.io/badge/D3.js-v7-purple)
![Testing](https://img.shields.io/badge/Tests-Comprehensive-green)

## ✨ What's New in v1.0.6

### 🧪 **Enhanced Testing Suite**
- **Comprehensive Frontend Unit Tests**: Interactive HTML test runner with 25+ test cases
- **Automated Test Execution**: Python-based comprehensive test runner
- **Visual Test Reports**: Beautiful HTML reports with success rate analysis
- **Quality Assessment**: Automated quality rating system (Excellent/Good/Needs Improvement)
- **Developer Experience**: Enhanced debugging tools and test coverage

### 📊 **Testing Framework Features**
- Real-time test progress visualization
- Component-level testing (API, Utils, Charts, Maps)
- Integration testing with mock data
- Test result export (JSON format)
- Auto-expanding failed test details
- Browser-based test execution

## 🚀 Core Features

### 🔍 **Trend Analysis**
- **Real-time Google Trends data** via Pytrends API
- **Interactive time-series charts** showing interest over time
- **Multi-keyword comparison** (up to 5 keywords)
- **Historical data analysis** with customizable timeframes

### 🗺️ **Interactive World Map**
- **Real-world geographic visualization** using D3.js and TopoJSON
- **Country-level interest mapping** with color-coded intensity
- **Interactive tooltips** showing detailed trend information
- **Click-to-explore** functionality for country-specific analysis

### 📊 **Rich Data Visualization**
- **Regional interest rankings** with top countries display
- **Related queries analysis** (top & rising searches)
- **Real-time trending topics** by country
- **Export capabilities** for data and charts

### 🧪 **Quality Assurance (v1.0.6)**
- **Frontend Unit Tests**: 25+ test cases covering all components
- **Backend API Tests**: Comprehensive API endpoint testing
- **Integration Tests**: End-to-end workflow validation
- **Automated Quality Assessment**: Success rate-based quality ratings

## 📋 Prerequisites

- **Python 3.8+** with pip
- **Internet connection** (for Google Trends API access)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/gon1zau6jyun4liu5/world-trends-explorer.git
cd world-trends-explorer
```

### 2. Start the Backend (Automated)
```bash
chmod +x start.sh
./start.sh
```

The script will:
- Create a virtual environment
- Install Python dependencies
- Start the Flask server on `http://localhost:5000`

### 3. Open the Frontend
```bash
# Option 1: Open directly in browser
open frontend/index.html

# Option 2: Use Python's built-in server
cd frontend
python -m http.server 8000
# Then visit http://localhost:8000
```

### 4. Start Exploring! 🎉
- Enter any keyword (e.g., "cryptocurrency", "climate change", "olympics")
- Click on countries in the interactive map
- Watch real-time data visualization
- Explore trending topics by region

## 🧪 Testing (v1.0.6)

### Quick Test Execution
```bash
# Comprehensive test suite (All tests + HTML report)
python run_comprehensive_tests.py

# Frontend tests only (Browser-based)
open frontend/tests/unit-tests.html

# Backend API tests only
cd backend
python test_api_connection.py
python verify_api.py
```

### Test Features
- **Real-time Progress**: Visual progress bars and live updates
- **Quality Assessment**: 80%+ = Excellent, 60-80% = Good, <60% = Needs Improvement  
- **Detailed Reports**: HTML reports with expandable failed tests
- **Export Options**: JSON export for test results
- **Mock Integration**: Offline testing with realistic mock data

### Test Coverage
- ✅ **API Module**: TrendsAPI initialization, caching, data validation
- ✅ **Utilities**: Date formatting, text processing, data sorting
- ✅ **Charts**: TrendsChart and RegionalChart components
- ✅ **World Map**: Interactive map functionality and data binding
- ✅ **Integration**: End-to-end workflow and error handling

## 📁 Project Structure

```
world-trends-explorer/
├── 🐍 backend/
│   ├── app.py                    # Main Flask application
│   ├── requirements.txt          # Python dependencies
│   ├── test_api_connection.py    # API connectivity tests
│   ├── test_api_unit.py         # Unit tests for API functions
│   ├── test_backend_api.py      # Backend endpoint tests
│   ├── verify_api.py            # Quick API verification
│   └── mock_server.py           # Mock server for testing
├── 🌐 frontend/
│   ├── index.html               # Main HTML page (v1.0.6)
│   ├── css/
│   │   └── styles.css           # Enhanced CSS with test styles
│   ├── js/
│   │   ├── api.js               # API communication layer
│   │   ├── worldmap.js          # D3.js world map component
│   │   ├── chart.js             # Chart.js visualization
│   │   └── app.js               # Main application logic
│   └── tests/
│       └── unit-tests.html      # Frontend test suite (v1.0.6)
├── 📚 docs/
│   ├── DOCKER.md               # Docker deployment guide
│   ├── FEATURE_SPEC.md         # Feature specifications (v1.0.6)
│   └── API.md                  # API documentation
├── 🔧 scripts/
│   └── deploy.sh               # Deployment automation
├── 📋 Test Reports/
│   ├── run_comprehensive_tests.py  # Comprehensive test runner
│   └── RELEASE_NOTES.md            # Version history (v1.0.6)
├── start.sh                    # Quick start script
└── README.md                   # This file
```

## 🔗 API Endpoints

The backend provides a comprehensive REST API:

### Core Endpoints
- `GET /api/trends/health` - Health check
- `GET /api/trends/search?keyword={term}&geo={country}` - Search trends
- `GET /api/trends/trending?geo={country}` - Get trending searches
- `GET /api/trends/suggestions?keyword={term}` - Keyword suggestions
- `GET /api/trends/countries` - Available countries
- `POST /api/trends/compare` - Compare multiple keywords

### Example API Usage
```bash
# Search for "artificial intelligence" trends in the US
curl "http://localhost:5000/api/trends/search?keyword=artificial%20intelligence&geo=US"

# Get trending searches in Japan
curl "http://localhost:5000/api/trends/trending?geo=JP"

# Health check
curl "http://localhost:5000/api/trends/health"
```

## 🛠️ Manual Installation

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

### Frontend Setup
```bash
cd frontend

# Method 1: Open directly
open index.html

# Method 2: Use local server
python -m http.server 8000
# Visit http://localhost:8000

# Method 3: Use Node.js server (if you have Node.js)
npx serve .
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Backend will be available at http://localhost:5000
# Frontend will be available at http://localhost:80
```

See [`docs/DOCKER.md`](docs/DOCKER.md) for detailed Docker configuration.

## 🌟 Usage Examples

### 1. **Technology Trends**
Search for "artificial intelligence", "blockchain", or "quantum computing" to see global technology adoption patterns.

### 2. **Cultural Events**
Explore "olympics", "world cup", or "eurovision" to see international event interest.

### 3. **Economic Indicators**
Track "inflation", "stock market", or "cryptocurrency" for economic trend analysis.

### 4. **Health & Wellness**
Monitor "meditation", "fitness", or "mental health" trends globally.

### 5. **Comparison Analysis**
Compare multiple terms like "tesla vs bmw" or "python vs javascript" to see relative interest.

## 🔧 Configuration

### Environment Variables
```bash
# Backend configuration (optional)
FLASK_DEBUG=True          # Enable debug mode
FLASK_ENV=development     # Set environment
PORT=5000                 # Server port
```

### API Configuration
The frontend API URL can be configured in `frontend/js/api.js`:
```javascript
// Change the base URL for production deployment
const baseURL = 'https://your-api-domain.com/api/trends';
```

## 📊 Quality Metrics (v1.0.6)

### Test Suite Results
- **Total Test Cases**: 25+ comprehensive tests
- **Code Coverage**: Core functionality 80%+
- **Success Rate Target**: 80% for excellent quality
- **Performance**: API response <5s, Map rendering <2s
- **Browser Support**: Chrome, Firefox, Safari, Edge (latest versions)

### Quality Assurance Process
1. **Pre-commit**: Unit tests execution
2. **Feature Development**: Test-driven development
3. **Integration**: End-to-end testing
4. **Release**: Comprehensive test suite validation

## 🐛 Troubleshooting

### Common Issues

**1. "Failed to fetch trends data" Error**
- Check if the backend server is running on `http://localhost:5000`
- Verify internet connection for Google Trends API access
- Try different keywords or regions

**2. World Map Not Loading**
- Ensure D3.js and TopoJSON are loaded correctly
- Check browser console for JavaScript errors
- Verify the world atlas data is accessible

**3. Python Dependencies Issues**
```bash
# Update pip and try again
pip install --upgrade pip
pip install -r requirements.txt
```

**4. CORS Issues**
- Make sure Flask-CORS is installed: `pip install flask-cors`
- Backend includes CORS headers for frontend integration

**5. Tests Failing**
```bash
# Run comprehensive test diagnosis
python run_comprehensive_tests.py

# Check individual test components
open frontend/tests/unit-tests.html
```

### Performance Tips
- Use caching for repeated queries (built-in 5-minute cache)
- Limit concurrent API requests
- Consider rate limiting for production deployment

### Test-Specific Troubleshooting (v1.0.6)
- **Frontend Tests**: Ensure all CDN resources are loaded
- **Backend Tests**: Verify Python environment and dependencies
- **Integration Tests**: Check API connectivity and mock data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Workflow (v1.0.6)
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests**: Add unit tests for new features
4. **Run test suite**: `python run_comprehensive_tests.py`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Quality Guidelines
- Maintain 80%+ test success rate
- Add unit tests for new features
- Update documentation for API changes
- Follow existing code style

## 📜 Version History

### v1.0.6 (2025-07-13) 🧪
**Major Feature: Comprehensive Testing Suite**
- ✅ Interactive frontend unit test framework
- ✅ Automated comprehensive test runner
- ✅ Visual HTML test reports with quality assessment
- ✅ Enhanced developer experience and debugging tools

### v1.0.5 (2025-07-12) 🔧
**Major Feature: API Testing & Verification System**
- ✅ Google Trends API connection testing
- ✅ Backend endpoint validation
- ✅ Automated test execution scripts

### v1.0.4 (2025-07-12) 🗺️
**Major Feature: Interactive World Map**
- ✅ D3.js + TopoJSON world map implementation
- ✅ Country-level click interactions
- ✅ Real-time data visualization

### Previous Versions
- **v1.0.3**: UI/UX improvements, mobile optimization
- **v1.0.2**: API error handling, chart performance
- **v1.0.1**: Bug fixes, documentation
- **v1.0.0**: Initial release

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **[Pytrends](https://github.com/GeneralMills/pytrends)** - Unofficial Google Trends API
- **[D3.js](https://d3js.org/)** - Data visualization library
- **[Chart.js](https://www.chartjs.org/)** - Chart rendering library
- **[Flask](https://flask.palletsprojects.com/)** - Python web framework
- **[Natural Earth](https://www.naturalearthdata.com/)** - World map data

## 📞 Support

For questions or support:
- 📧 Open an issue on GitHub
- 💬 Check existing issues for solutions
- 📖 Review the documentation in the `docs/` folder
- 🧪 Run the test suite for diagnostics: `python run_comprehensive_tests.py`

---

**Happy Trend Exploring! 🌍📈**

*Built with ❤️ for data visualization and global insights*  
*v1.0.6 - Enhanced with comprehensive testing suite for reliable, quality-assured trend analysis*