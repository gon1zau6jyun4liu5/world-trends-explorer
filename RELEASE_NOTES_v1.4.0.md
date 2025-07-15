# World Trends Explorer - Release Notes

## Version 1.4.0 (2025-07-15)

### 🚨 Breaking Changes
- **Pytrends API has been permanently removed**
- **SerpAPI is now the only data source**
- **API key is REQUIRED** - Without SerpAPI key, only mock data will be shown

### ✨ New Features
1. **Complete SerpAPI Integration**
   - Full migration from Pytrends to SerpAPI
   - Enhanced data reliability and accuracy
   - Better rate limiting and error handling
   - Support for all Google Trends features via SerpAPI

2. **Improved Documentation**
   - Added `SERPAPI_SETUP.md` with clear setup instructions
   - Updated README with SerpAPI requirements
   - Environment variable configuration guide

3. **Enhanced Testing**
   - Added `test_serpapi_integration.py` to verify Pytrends removal
   - Unit tests to ensure SerpAPI is properly integrated
   - Verification that mock server is removed

### 🛠️ Technical Changes
- Removed `pytrends` from `requirements.txt`
- Removed all Pytrends imports and code
- Deleted `mock_server.py` permanently
- Implemented `SerpAPIClient` class for all API calls
- Updated all API endpoints to use SerpAPI

### 📝 Migration Guide
1. **Set up SerpAPI Key (Required!)**
   ```bash
   export SERPAPI_KEY="your_serpapi_key_here"
   ```
   
2. **Get your API key from:**
   - https://serpapi.com
   - Sign up for free account (100 searches/month)

3. **Update any custom code:**
   - Remove any Pytrends-specific implementations
   - Update API response parsing for SerpAPI format

### ⚠️ Important Notes
- Without SerpAPI key, the app will show enhanced mock data
- Real Google Trends data requires valid SerpAPI key
- API response format has slightly changed
- All features remain the same, just different data source

---

## Previous Versions
See git history for details on versions 1.0.0 - 1.3.2
