🥑 AVOCADO Web v2.7 - Web-based bibliographic metadata processor for Venezuelan cultural institutions. Enhanced OCLC WorldCat integration with multiple search strategies, and auto-credential loading. Convert book lists to rich metadata with a single upload.

## Features

### **Enhanced Processing**
- **Multiple Search Strategies**: 4 different methods for better OCLC number discovery
- **Advanced Metadata Extraction**: 6 extraction methods for comprehensive publisher information
- **Real-time Statistics**: Live progress tracking with detailed processing statistics
- **Desktop-Quality Results**: Same advanced parsing as the desktop version

### **User Experience**
- **Auto-Credential Loading**: Automatically detects and uses `.env` credentials
- **Clean Professional Interface**: Modern, responsive design
- **Smart Form Handling**: Conditional credential input based on environment
- **Template Download**: Pre-populated CSV template with Venezuelan literature examples

### **Metadata Fields**
- OCLC Number
- Title & Creator
- Publisher & Publication Date
- Language & Subjects
- Type & Format
- ISBN & ISSN
- Edition & WorldCat URL

## Installation

### Prerequisites
- Python 3.7+
- OCLC WorldCat Discovery API credentials

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/avocado-web.git
   cd avocado-web
   ```

2. **Install dependencies**
   ```bash
   pip install flask requests python-dotenv
   ```

3. **Configure credentials**
   Create a `.env` file in the project root:
   ```env
   OCLC_WSKEY=your_oclc_wskey_here
   OCLC_WSSECRET=your_oclc_secret_here
   FLASK_SECRET=your_flask_secret_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web interface**
   Open http://localhost:5000 in your browser

## Usage

### With .env Configuration (Recommended)
1. Set up your `.env` file with OCLC credentials
2. Upload your CSV file (must have columns: `OCLC #`, `Author`, `Title`)
3. Click "Process with AVOCADO v2.7"
4. Download the enhanced results

### Manual Credential Entry
1. Enter your OCLC WSKey and Secret in the web form
2. Upload your CSV file
3. Process and download results

### CSV Format
Your input CSV must contain these columns:
- `OCLC #` (optional - will search if empty)
- `Author` (required for search)
- `Title` (required for search)

## 🎯 Perfect For

- **Cultural Institutions**: Museums and cultural heritage organizations
- **Libraries**: Academic and public library collections
- **Archives**: Digital humanities and archival projects
- **Research Projects**: Bibliographic data management and analysis

## 🆕 New in v2.7 Enhanced

- **Desktop-Quality Processing**: Advanced metadata extraction matching desktop version
- **Multiple Search Strategies**: Improved OCLC number discovery success rate
- **Enhanced Publisher Extraction**: 6 different methods for complete publisher data
- **Auto-Credential Detection**: Seamless `.env` file integration
- **Clean Interface**: Removed distracting badges and streamlined design
- **Real-time Statistics**: Live processing feedback and completion metrics

## 🔧 Technical Details

### Built With
- **Flask**: Python web framework
- **OCLC WorldCat Discovery API v2**: Bibliographic data source
- **Bootstrap-inspired**: Responsive design principles
- **Tempfile**: Secure file handling

### API Integration
- Multiple search query strategies for better results
- Rate limiting to respect OCLC API guidelines
- Comprehensive error handling and fallback methods
- Enhanced metadata parsing with multiple extraction techniques

## 📁 Project Structure

```
avocado-web/
├── app.py                 # Main Flask application
├── templates/
│   ├── base.html         # Base template with styling
│   └── index.html        # Main interface
├── .env                  # Environment variables (create this)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/enhancement`)
5. Create a Pull Request

## 📄 License

This project is developed by **ARCHIVO VENEZUELA** (www.archivovenezuela.com).

## 🔗 Related Projects

- [AVOCADO Desktop](../desktop) - Desktop version with GUI interface
- [AVOCADO CLI](../cli) - Command-line version for batch processing

## 🆘 Support

For issues, questions, or contributions, please open an issue on GitHub or contact the development team.

---

🥑 AVOCADO v2.7 by Archivo Venezuela.
