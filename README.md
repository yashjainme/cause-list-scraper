# eCourts Cause List Scraper

A Python automation tool to scrape cause list data from the eCourts India portal and generate PDF reports.

## Features

- Interactive selection of State, District, Court Complex, Establishment, and Court Name
- Automated form filling and CAPTCHA input
- Extracts cause list data including case numbers, party names, advocates, and hearing dates
- Generates formatted PDF reports grouped by case categories
- Supports both Civil and Criminal case types

## Requirements
```bash
pip install selenium reportlab
```

- Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Usage

1. Run the script:
```bash
python script.py
```

2. Follow the interactive prompts:
   - Select State, District, Court Complex, and Court Name
   - Enter date (DD-MM-YYYY format)
   - Solve CAPTCHA displayed in browser
   - Choose Civil or Criminal case type

3. PDF report will be automatically generated with filename:
   `CauseList_{CaseType}_{Date}_{Timestamp}.pdf`

## Output

The PDF includes:
- Court details and selected criteria
- Cause list entries grouped by category
- Case numbers, hearing dates, party names, and advocates
- Professional landscape-oriented formatting

## Notes

- Requires active internet connection
- Browser window will open during execution
- CAPTCHA must be manually entered
- Uncomment `--headless` in chrome_options for background execution (after CAPTCHA automation)