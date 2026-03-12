# AI Lead Generation Agent (Task-02)

## Why I Chose This Task
I chose Task 02 because it allows me to demonstrate my skills in combining web scraping with Large Language Models (LLMs) to solve a real-world business problem.This project showcases how AI can autonomously identify high-intent buying signals and enrich them with professional contact data.

## Overview
This autonomous AI agent monitors online platforms for buying signals within the Real Estate and PropTech sectors. It identifies companies undergoing digital transformation or adopting tech solutions, classifies their intent using Llama-3, and discovers key people for outreach.

## Architecture
The system follows a five-step pipeline:
1. **Signal Monitoring:** Polls Google News RSS(top 10 from each feed) and scrapes industry-specific news (Inman PropTech) for keywords like 'proptech launch' or 'real estate digital'.
2. **Intent Classification:** Uses Llama-3.1-8b (via Groq) to analyze each signal for intent (YES/NO), extract the company name, provide a summary of the article, state the reason for choosing that article, and assign an urgency score from 1–10.
3. **Qualifying Leads:** A company is qualified if it is not from a media domain, is not a media company or government body, is not an invalid company (e.g., "none," "not specified," "n/a," etc.), and the intent is marked as YES.
4. **Contact Discovery:** For every qualified lead, the agent performs a targeted search to find the CEO, CTO, or Founder's LinkedIn profile.
5. **Reporting:** Deduplicates entries and rejects results if the LinkedIn URL is empty, a company page, a login page, or does not contain `linkedin.com/in`. It then exports a structured lead list to CSV and Excel formats.



## Setup Instructions

### 1. Prerequisites
* Python 3.8+
* A Groq API Key (for Llama-3 inference)

### 2. Installation
Clone the repository and install the required dependencies (in a virtual environment if possible) using:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Insert your Groq API key in the `.env.example` file:
`GROQ_API_KEY=[insert your_groq_api_key_here]`

Then, change the file name to `.env`.

## Configuration & Customization
To tailor the agent to a specific ICP or set of keywords, you can modify the following variables directly in `main.py`:
**Setting Keywords & Sources:** Update the `rss_sources` list or modify the keywords in the `scrape_proptech_news()` function to target different industry signals.
**Defining the ICP:** To change the target companies or roles, modify the `ignore_companies` list to filter out specific sectors and update the `find_contact()` search query (currently set to target CEOs, CTOs, and Founders).
**Intent Parameters:** You can adjust the LLM prompt within the `run_agent()` function to change the criteria for what constitutes a "YES" intent signal.
**Helper Function Customization:** The logic for verifying lead quality can be adjusted by modifying the helper functions (like `validate_contact` or `is_person_profile`) to enforce stricter matching rules for job titles and LinkedIn profile types.
**Processing Limits & Timing:** Adjust the number of articles fetched (currently top 10 per source), modify request `timeouts`, or change the `scheduler` interval (defaulted to 24 hours) to control the speed and volume of data collection.

## How to Run

### Manual Execution:
Run the file by entering python `main.py` in the terminal. The agent will run once, and collected articles will be exported to CSV/Excel files if they are qualifying leads and a contact is discovered.

### Scheduled Execution
The script includes an APScheduler that runs the agent every 24 hours by default to ensure the lead list is updated daily. Leave the terminal running to update the lead list automatically.

## Output

The agent generates two files in the root directory:

**leads.csv:** A log of all leads with columns: Company Name, Contact Name, Title, LinkedIn URL, Company Website, Signal Source, Signal Summary, Intent Score, and Date Found.

**leads.xlsx:** A structured, deduplicated Excel sheet containing the same columns as above.

## Demo Video
Click here to watch demo video - https://drive.google.com/file/d/1XXqlxr69qmAu4NmCv5yHn_8Xr9K2bWFm/view?usp=sharing

**Note on Live Data & Results:** This system processes real-time RSS feeds and live web signals. Because the agent monitors the most recent news, the leads and "Intent Scores" will vary across different runs (e.g., the demo video vs. the files currently in this repository). Additionally, the system is configured to filter out media domains and specific industry keywords to ensure high-quality, relevant prospecting.




## Known Limitations & Future Improvements

**LinkedIn Scraping:** Currently uses DuckDuckGo Search to find public profiles; integrating an official API would increase reliability.

**Profile Parsing:** Currently, multiple individual profiles can sometimes be mixed within the LinkedIn URL results. Improving the logic to parse them into the correct places is a priority.

**Email Enrichment:** The system finds LinkedIn URLs; adding a service like Hunter.io could help find verified business emails.

**Data Storage:** While CSV/Excel is used for this demo, a production version would utilize a PostgreSQL database for better scalability.






