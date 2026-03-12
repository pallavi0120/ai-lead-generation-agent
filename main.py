"""
AI Lead Generation Agent - Strikin Internship Assignment (Task 02)
Author: [Your Name]
Description: This agent monitors Real Estate/PropTech news, classifies intent using Llama-3,
             discovers key executives (CEO/CTO) on LinkedIn, and exports a lead list.
"""

#importing libraries
import feedparser
import os
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import time

# ---------------------------------------------------------
# 1. INITIALIZATION & CONFIGURATION
# ---------------------------------------------------------

# Load environment variables
load_dotenv()

# Create Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# RSS signal sources targeting Real Estate Technology
rss_sources = [
    "https://news.google.com/rss/search?q=real+estate+technology",
    "https://realty.economictimes.indiatimes.com/rss/technology" 
]

# Filtering lists to ensure high-quality, private company leads
# Ignore media publishers
ignore_companies = [
    "cnbc","forbes","bloomberg","reuters","techcrunch","yahoo",
    "business insider","hindustan times","financial express",
    "arab news","world economic forum","inc42","yourstory",
    "livemint","economic times","times of india","the hindu",
    "ndtv","bbc","cnn","the guardian","washington post"
]

media_domains = [
    "entrackr.com",
    "financialexpress.com",
    "arabnews.com",
    "forbes.com",
    "bloomberg.com",
    "reuters.com",
    "techcrunch.com",
    "inc42.com",
    "yourstory.com",
    "livemint.com"
]
invalid_companies = [
    "no specific company mentioned",
    "none mentioned",
    "not mentioned",
    "unknown",
    "not specified",
    "none",
    "na",
    "n/a",
    "proptech startups",
    "real estate sector",
    "the article",
    "sector",
    "news source"
]
government_keywords = [
    "municipal", "government", "govt", "corporation", "authority", 
    "ministry", "department", "state of", "city of", "pune municipal"
]

# ---------------------------------------------------------
# 2. DATA ACQUISITION (STEP 1: SIGNAL MONITORING)
# ---------------------------------------------------------

def scrape_proptech_news():
    print("Scraping Inman Proptech for latest signals...")
    # Inman is much more stable for DNS resolution
    url = "https://www.inman.com/category/proptech/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        scraped_entries = []
        # Target Inman's article headlines
        articles = soup.select('article h2 a', limit=5) 
        
        for link_tag in articles:
            scraped_entries.append({
                'title': link_tag.get_text().strip(),
                'link': link_tag['href'] if link_tag['href'].startswith('http') else f"https://www.inman.com{link_tag['href']}",
                'summary': "PropTech industry update from Inman."
            })
        return scraped_entries
    except Exception as e:
        print(f"Scraping failed: {e}")
        return []
    
# ---------------------------------------------------------
# 3. LEAD ENRICHMENT (STEP 3: CONTACT DISCOVERY)
# ---------------------------------------------------------

def find_contact(company):
    # CLEANING: Remove domain suffixes like .com or .ai for better matching
    clean_company = company.split('.')[0] if '.' in company else company
    
    # BROADENED QUERY: Added Managing Director for more results
    search_query = f'site:linkedin.com/in "{clean_company}" (CEO OR CTO OR Founder OR "Managing Director")'

    with DDGS() as ddgs:
        try:
            # Added a small delay to avoid rate limits
            time.sleep(1) 
            results = list(ddgs.text(search_query, max_results=10))
        except Exception as e:
            print(f"Search failed: {e}")
            return None, None, None

    for r in results:
        link = r.get("href","")
        title = r.get("title","")
        if "linkedin.com/in/" in link.lower():
            name = title.split("|")[0].strip()
            return name, link, title
    return None, None, None

def find_company_website(company_name):
    with DDGS() as ddgs:
        results = list(ddgs.text(f"{company_name} official website", max_results=1))
        return results[0].get("href", "") if results else ""

def validate_contact(contact_name, company):

    if contact_name is None:
        return False

    contact_lower = contact_name.lower()

    if "ceo" in contact_lower or "cto" in contact_lower or "chief executive" in contact_lower:
        return True

    return False

def is_person_profile(contact_name, linkedin_url):

    if linkedin_url is None:
        return False

    # reject company pages
    if "company" in linkedin_url:
        return False

    # reject login pages
    if "login" in linkedin_url:
        return False

    # reject generic linkedin pages
    if "linkedin.com/in/" not in linkedin_url:
        return False

    return True

# ---------------------------------------------------------
# 4. PROCESSING PIPELINE (STEP 2: INTENT CLASSIFICATION)
# ---------------------------------------------------------

def run_agent():

    """Main execution loop for signal monitoring and lead generation."""
    print("\nScanning articles...\n")

    leads = []
    rss_entries = []

    # Fetch RSS entries
    for source in rss_sources:
        feed = feedparser.parse(source)
        rss_entries.extend(feed.entries[:15])

    scraped_entries = scrape_proptech_news()

    # Aggregate signals from RSS and Web Scraping
    all_signals = rss_entries + scraped_entries

    for entry in all_signals:

        #domain filtering
        domain = urlparse(entry.link).netloc.lower()
        if any(media in domain for media in media_domains):
            continue

        article_text = entry.title + " " + entry.summary

        # LLM intent detection
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{
                "role": "user",
                "content": f"""Analyze this news signal for private Real Estate/PropTech companies.
                
                STRICT FORMAT:
                Intent: YES / NO
                Company: [Specific Private Company Name Only]
                Summary: [One sentence]
                Reason: [Brief explanation]
                Score: [1-10]
                
                If NO SPECIFIC private company is mentioned, set Company to 'NONE'.
                Article: {entry.title} {entry.summary}"""
            }]
        )

        analysis = response.choices[0].message.content.strip()
        print(analysis)

        lines = analysis.split("\n")

        intent = ""
        company = ""
        summary = ""
        score = 0

        for line in lines:

            if line.lower().startswith("intent"):
                intent = line.split(":",1)[1].strip()

            elif line.lower().startswith("company"):
                company = line.split(":",1)[1].strip()

            elif line.lower().startswith("summary"):
                summary = line.split(":",1)[1].strip()

            elif line.lower().startswith("score"):
                try:
                    score = int(line.split(":",1)[1].strip())
                except:
                    score = 5

        #commpany filters
        company_lower = company.lower()

        if any(bad in company_lower for bad in invalid_companies):
            continue

        if any(bad in company_lower for bad in ignore_companies):
            continue

        if any(gov in company_lower for gov in government_keywords):
            print(f"Skipping government entity: {company}")
            continue

        if intent == "YES" and company.upper() != "NONE":
            print(f"Lead Found: {company}")
            contact, linkedin, contact_title = find_contact(company)

            print("Contact:", contact)
            print("LinkedIn:", linkedin)
            print("-------------------------")

            # Lead scoring based on signal
            title_lower = entry.title.lower()

            if "launch" in title_lower or "platform" in title_lower:
                score = max(score, 9)

            elif "funding" in title_lower or "investment" in title_lower:
                score = max(score, 8)

            elif "expansion" in title_lower or "growth" in title_lower:
                score = max(score, 7)

            elif "hiring" in title_lower:
                score = max(score, 6)
            
            if not company or company.strip() == "":
                continue
            
            if hasattr(entry, "published"):
                try:
                    date_found = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d")
                except:
                    date_found = datetime.now().strftime("%Y-%m-%d")
            else:
                date_found = datetime.now().strftime("%Y-%m-%d")
            
            if linkedin and is_person_profile(contact, linkedin):
                leads.append({
                "Company Name": company,
                "Contact Name": contact,
                "Title": contact_title if contact_title else "Executive",
                "LinkedIn URL": linkedin,
                "Company Website": "",
                "Signal Source": entry.link,
                "Signal Summary": summary,
                "Intent Score": score,
                "Date Found": date_found
            })
            else:
                print("Rejected contact (company mismatch)")

    # Create dataset
    if len(leads) == 0:
        print("No leads collected")
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(leads)

        if "Company Name" in df.columns:
            df = df.drop_duplicates(subset=["Company Name"])

    # ---------------------------------------------------------
    # 5. OUTPUT (STEP 4: EXCEL/CSV EXPORT)
    # ---------------------------------------------------------

    # Save only if leads exist
    if len(df) > 0:
        df.to_csv("leads.csv", mode="a", header=not os.path.exists("leads.csv"), index=False)
        if os.path.exists("leads.xlsx"):
            os.remove("leads.xlsx")
        df.to_excel("leads.xlsx", index=False)
        print("Leads saved successfully")
    else:
        print("No leads to save")

    print("\nLead dataset saved as leads.csv and leads.xlsx")

    print("\nLead Generation Summary")
    print("------------------------")
    print("Total leads found:", len(df))
    print("Top leads:")

    for i, row in df.head(3).iterrows():
        print(f"- {row['Company Name']} (Score: {row['Intent Score']})")

# Run once immediately
run_agent()

# ---------------------------------------------------------
# 6. SCHEDULER
# ---------------------------------------------------------

scheduler = BlockingScheduler()

scheduler.add_job(run_agent, 'interval', hours=24)

print("Scheduler running...")

scheduler.start()