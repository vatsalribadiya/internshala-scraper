# 🕷️ Internshala Job Listings Scraper

A production-ready web scraper that extracts, cleans, and exports structured internship data from [Internshala](https://internshala.com) — one of India's largest job listing platforms.

Built as a demonstration of end-to-end data extraction, cleaning, and structured dataset delivery using Python.

---

## 📦 Features

- Scrapes multiple pages of internship listings automatically
- Handles missing/malformed fields gracefully with fallback logic
- Parses stipend ranges into numeric `min/max` columns for analysis
- Flags remote (`Work from Home`) positions with an `is_wfh` boolean
- Removes duplicate entries based on title + company combination
- Exports clean, structured output in both **CSV** and **JSON**
- Includes a terminal summary report with key data insights

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `requests` | HTTP page fetching with browser-like headers |
| `BeautifulSoup4` | HTML parsing and DOM traversal |
| `pandas` | Data cleaning, deduplication, normalization |
| `json` | Structured JSON export |
| `re` | Stipend range extraction via regex |

---

## 📁 Project Structure

```
internshala-scraper/
├── scraper.py          # Main scraper script
├── internships.csv     # Sample output (CSV)
├── internships.json    # Sample output (JSON)
└── README.md
```

---

## ⚙️ Setup & Usage

### 1. Clone the repo
```bash
git clone https://github.com/vatsalribadiya/internshala-scraper.git
cd internshala-scraper
```

### 2. Install dependencies
```bash
pip3 install requests beautifulsoup4 pandas
```

### 3. Run the scraper
```bash
python3 scraper.py
```

---

## 📊 Sample Output

### Terminal summary
```
🔍 Starting scraper...

[1/4] Fetching listings from Internshala...
  Scraping page 1: https://internshala.com/internships/page-1/
  Found 42 listings on page 1
  ...
  Total raw listings collected: 125

[2/4] Cleaning and validating data...
  Removed 1 duplicate entries
  Clean listings ready: 124

[3/4] Saving outputs...
  Saved → internships.csv
  Saved → internships.json

📊 Quick Data Summary:
  Total listings:         124
  Work from home:         38
  Paid internships:       101
  Avg max stipend (paid): ₹ 18,450/month
  Top hiring company:     Unibridges
  Top location:           Work from home

✅ Done! Check internships.csv and internships.json
```

### CSV preview

| title | company | location | is_wfh | stipend | stipend_min | stipend_max |
|---|---|---|---|---|---|---|
| Marketing | Careers360 | Work from home | Yes | ₹ 15,150 lump sum | 15150 | 15150 |
| Social Media Associate | StoryMirror | Mumbai | No | ₹ 8,000 - 12,000 /month | 8000 | 12000 |
| Business Development | Unibridges | Delhi | No | ₹ 28,000 - 35,000 lump sum | 28000 | 35000 |

---

## 🔍 Key Technical Highlights

**Graceful error handling** — every field uses a `safe_get()` helper that returns `"N/A"` instead of crashing on missing elements, mimicking real-world scraping where site structure varies.

**Stipend normalization** — raw strings like `"₹ 8,000 - 12,000 /month"` are parsed into separate `stipend_min` / `stipend_max` integer columns using regex, enabling numeric filtering and analysis.

**Polite scraping** — `time.sleep(1)` between page requests avoids hammering the server, following standard scraping etiquette.

**Dual export** — CSV for spreadsheet analysis, JSON for API/pipeline consumption — matching real-world data delivery requirements.

---

## 🚀 Potential Extensions

- Add Selenium support for JavaScript-rendered pages (infinite scroll, AJAX)
- Integrate with Apify for large-scale cloud scraping
- Pipeline output directly into Google Sheets via API
- Add proxy rotation for large-scale runs
- Schedule via cron job for daily data updates

---
