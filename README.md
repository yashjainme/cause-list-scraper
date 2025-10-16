# eCourts Cause List Scraper

A web-based tool to scrape and download cause lists from the eCourts India portal with an intuitive UI.

## Features

- 🔄 Step-by-step guided workflow
- 🎨 Modern, responsive web interface
- 🔐 CAPTCHA handling with refresh option
- 📊 Real-time selection summary
- 📄 Automatic PDF report generation
- ✅ Visual progress tracking

## Prerequisites

- Python 3.7+
- Chrome browser
- ChromeDriver (matching your Chrome version)

## Installation

1. **Clone or download the project**

2. **Install dependencies**
```bash
pip install flask selenium reportlab
```

3. **Setup ChromeDriver**
   - Download from [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Add to system PATH or place in project directory

## Project Structure

```
project/
│
├── main.py              # Flask backend
└── templates/
    └── index.html       # Frontend UI
```

## Usage

1. **Start the application**
```bash
python main.py
```

2. **Open browser**
   - Navigate to `http://localhost:5000`

3. **Follow the steps**
   - Click "Start Scraping Process"
   - Select State → District → Court Complex
   - Select Establishment (if required) → Court Name
   - Enter/modify date (DD-MM-YYYY format)
   - Solve CAPTCHA
   - Choose case type (Civil/Criminal)
   - Click "Fetch Cause List"

4. **Download results**
   - View results in the table
   - Click "Download PDF" to save the report

## Output

PDF files are generated with the naming format:
```
CauseList_[CaseType]_[Date]_[Timestamp].pdf
```

## Features Explained

- **Session Management**: Each user gets an isolated browser session
- **Progressive Workflow**: Steps unlock as you progress
- **CAPTCHA Refresh**: Refresh CAPTCHA if unclear
- **Data Validation**: Ensures all required fields are filled
- **Categorized Results**: Data grouped by case categories
- **PDF Export**: Professional formatted PDF reports

## Troubleshooting

**Browser not opening?**
- Ensure ChromeDriver is installed and matches Chrome version

**CAPTCHA errors?**
- Click refresh icon to get a new CAPTCHA
- Ensure text is entered exactly as shown

**No data found?**
- Verify date format (DD-MM-YYYY)
- Check if court has listings for selected date
- Try different case type (Civil/Criminal)

## Notes

- The scraper maintains backend functionality identical to the original CLI script
- Each session requires solving a CAPTCHA (eCourts security requirement)
- Browser instance closes automatically after successful data retrieval

## License

For educational and personal use only. Please respect eCourts India's terms of service.

## Support

For issues or questions, please check the eCourts India portal status and ensure all prerequisites are properly installed.