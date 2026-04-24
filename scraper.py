import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

# ──────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────
BASE_URL = "https://internshala.com/internships/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
MAX_PAGES = 3  # scrape 3 pages (~60 listings)


# ──────────────────────────────────────────
# STEP 1: FETCH PAGE HTML
# ──────────────────────────────────────────
def fetch_page(url):
    """
    Sends an HTTP GET request and returns parsed HTML.
    The User-Agent header makes us look like a real browser.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # raises error if status is 4xx/5xx
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Failed to fetch {url}: {e}")
        return None


# ──────────────────────────────────────────
# STEP 2: EXTRACT DATA FROM ONE LISTING CARD
# ──────────────────────────────────────────
def parse_listing(card):
    """
    Extracts fields from a single internship card element.
    Updated selectors to match current Internshala HTML structure.
    """

    def safe_get(selector, attr=None):
        el = card.select_one(selector)
        if not el:
            return "N/A"
        if attr:
            return el.get(attr, "N/A").strip()
        return el.get_text(strip=True)

    title    = safe_get(".job-internship-name")
    company  = safe_get(".company-name")
    location = safe_get(".locations span a")
    stipend  = safe_get(".stipend")
    posted   = safe_get(".status-inactive")

    # Fixed: duration lives inside .other-details spans
    duration_els = card.select(".other-details .item-body")
    duration = duration_els[0].get_text(strip=True) if duration_els else "N/A"

    # Fixed: grab the detail page link from the card title anchor
    link_tag = card.select_one("a.job-internship-name")
    if not link_tag:
        link_tag = card.select_one(".view-internship-button, h3 a, .job-title-href")
    link = "https://internshala.com" + link_tag["href"] if link_tag and link_tag.get("href") else "N/A"

    # BONUS: work from home flag
    is_wfh = "Yes" if "work from home" in location.lower() else "No"

    # BONUS: parse stipend range into min/max numbers for analysis
    stipend_min, stipend_max = parse_stipend(stipend)

    return {
        "title":       title,
        "company":     company,
        "location":    location,
        "is_wfh":      is_wfh,
        "stipend":     stipend,
        "stipend_min": stipend_min,
        "stipend_max": stipend_max,
        "duration":    duration,
        "posted":      posted,
        "link":        link
    }

def parse_stipend(stipend_text):
    """
    Extracts numeric min/max from stipend strings like '₹ 8,000 - 12,000 /month'
    Returns (min, max) as integers, or (0, 0) if unpaid/not available.
    Useful for filtering and sorting by pay — shows data processing skill.
    """
    import re
    if not stipend_text or stipend_text in ("N/A", "Unpaid", "Performance Based"):
        return 0, 0
    numbers = re.findall(r"[\d,]+", stipend_text)
    numbers = [int(n.replace(",", "")) for n in numbers]
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    elif len(numbers) >= 2:
        return numbers[0], numbers[1]
    return 0, 0

# ──────────────────────────────────────────
# STEP 3: SCRAPE MULTIPLE PAGES
# ──────────────────────────────────────────
def scrape_all_pages():
    """
    Loops through pages, collects all listing cards,
    and builds a list of dictionaries.
    """
    all_listings = []

    for page_num in range(1, MAX_PAGES + 1):
        url = f"{BASE_URL}page-{page_num}/"
        print(f"  Scraping page {page_num}: {url}")

        soup = fetch_page(url)
        if not soup:
            continue

        # Each internship is inside a div with this class
        cards = soup.select(".individual_internship")
        print(f"  Found {len(cards)} listings on page {page_num}")

        for card in cards:
            listing = parse_listing(card)
            all_listings.append(listing)

        time.sleep(1)  # polite delay — avoid hammering the server

    return all_listings


# ──────────────────────────────────────────
# STEP 4: CLEAN & VALIDATE DATA
# ──────────────────────────────────────────
def clean_data(listings):
    """
    Converts list of dicts to a Pandas DataFrame.
    - Removes duplicate entries
    - Drops rows where both title AND company are missing
    - Strips extra whitespace from all text fields
    """
    df = pd.DataFrame(listings)

    # Remove duplicates based on title + company combo
    before = len(df)
    df.drop_duplicates(subset=["title", "company"], inplace=True)
    after = len(df)
    print(f"  Removed {before - after} duplicate entries")

    # Drop rows with no useful data
    df = df[~((df["title"] == "N/A") & (df["company"] == "N/A"))]

    # Clean whitespace across all string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    return df


# ──────────────────────────────────────────
# STEP 5: SAVE TO CSV + JSON
# ──────────────────────────────────────────
def save_data(df):
    """
    Exports cleaned data to both CSV and JSON formats.
    CSV  → easy to open in Excel / Google Sheets
    JSON → structured format for API use or further processing
    """
    df.to_csv("internships.csv", index=False, encoding="utf-8")
    print("  Saved → internships.csv")

    records = df.to_dict(orient="records")
    with open("internships.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print("  Saved → internships.json")


# ──────────────────────────────────────────
# MAIN RUNNER
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("\n🔍 Starting scraper...")

    print("\n[1/4] Fetching listings from Internshala...")
    raw_listings = scrape_all_pages()
    print(f"  Total raw listings collected: {len(raw_listings)}")

    print("\n[2/4] Cleaning and validating data...")
    df = clean_data(raw_listings)
    print(f"  Clean listings ready: {len(df)}")

    print("\n[3/4] Saving outputs...")
    save_data(df)

    print("\n[4/4] Preview of first 5 results:")
    print(df[["title", "company", "location", "stipend"]].head())

    print("\n📊 Quick Data Summary:")
    print(f"  Total listings:         {len(df)}")
    print(f"  Work from home:         {(df['is_wfh'] == 'Yes').sum()}")
    print(f"  Paid internships:       {(df['stipend_min'] > 0).sum()}")
    print(f"  Avg max stipend (paid): ₹ {df[df['stipend_max'] > 0]['stipend_max'].mean():,.0f}/month")
    print(f"  Top hiring company:     {df['company'].value_counts().idxmax()}")
    print(f"  Top location:           {df['location'].value_counts().idxmax()}")

    print("\n✅ Done! Check internships.csv and internships.json")
