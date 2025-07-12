# 🌍 World Trends Explorer

**Real-time Google Trends explorer with interactive world map using Pytrends**

![World Trends Explorer](https://img.shields.io/badge/Status-Ready%20to%20Run-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Latest-orange)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-yellow)
![D3.js](https://img.shields.io/badge/D3.js-v7-purple)

## ✨ Features

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

### 🚀 **Modern Tech Stack**
- **Backend**: Python Flask with Pytrends integration
- **Frontend**: Vanilla JavaScript with D3.js and Chart.js
- **Responsive design** that works on all devices
- **RESTful API** with comprehensive error handling

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
- Select a country or search worldwide
- Watch the interactive map and charts update in real-time
- Click on countries in the map for detailed analysis
- Explore trending topics by region

## 📁 Project Structure

```
world-trends-explorer/
├── 🐍 backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Docker configuration
├── 🌐 frontend/
│   ├── index.html         # Main HTML page
│   ├── css/
│   │   └── styles.css     # Responsive CSS styling
│   └── js/
│       ├── api.js         # API communication layer
│       ├── worldmap.js    # D3.js world map component
│       ├── chart.js       # Chart.js visualization
│       └── app.js         # Main application logic
├── 📚 docs/
│   ├── DOCKER.md          # Docker deployment guide
│   └── API.md             # API documentation
├── 🔧 scripts/
│   └── deploy.sh          # Deployment automation
├── start.sh               # Quick start script
└── README.md              # This file
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

### Performance Tips
- Use caching for repeated queries (built-in 5-minute cache)
- Limit concurrent API requests
- Consider rate limiting for production deployment

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

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

---

**Happy Trend Exploring! 🌍📈**

*Built with ❤️ for data visualization and global insights*