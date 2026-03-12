# AI Lead Generation Agent

## Why I Chose This Task
I chose Task 02 because it allows me to demonstrate my skills in combining web scraping with Large Language Models (LLMs) to solve a real-world business problem: manual lead prospecting.This project showcases how AI can autonomously identify high-intent buying signals and enrich them with professional contact data.

## Overview
This autonomous AI agent monitors online platforms for buying signals within the Real Estate and PropTech sectors. It identifies companies undergoing digital transformation or adopting tech solutions, classifies their intent using Llama-3, and discovers key executives for outreach.

## Architecture
The system follows a four-step pipeline:
1. **Signal Monitoring:** Polls Google News RSS and scrapes industry-specific news (Inman PropTech) for keywords like 'proptech launch' or 'real estate digital'.
2. **Intent Classification:** Uses Llama-3.1-8b (via Groq) to analyze the news for intent (YES/NO), extract company names, and assign an urgency score from 1-10.
3. **Contact Discovery:** For every qualified lead, the agent performs a targeted search to find the CEO, CTO, or Founder's LinkedIn profile.
4. **Reporting:** Deduplicates entries and exports a structured lead list to CSV and Excel format.



## Setup Instructions

### 1. Prerequisites
* Python 3.8+
* A Groq API Key (for Llama-3 inference)

### 2. Installation
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a .env file in the root directory and add your Groq API key (refer to .env.example):

```bash
GROQ_API_KEY=your_groq_api_key_here
```

## How to Run

### Manual Trigger
To run the agent once and generate the lead list immediately:

```bash
python main.py
```

### Scheduled Execution
The script includes an APScheduler that runs the agent every 24 hours by default to ensure the lead list is updated daily.

## Output

The agent generates two files in the root directory:
**leads.csv:** An append-only historical log of all leads discovered.
**leads.xlsx:** A structured, deduplicated Excel sheet with columns for Company Name, Contact Name, Title, LinkedIn URL, and Intent Score.

## Known Limitations & Future Improvements

**LinkedIn Scraping:** Currently uses DuckDuckGo Search to find public profiles; integrating an official API would increase reliability.
**Email Enrichment:** The system finds LinkedIn URLs; adding a service like Hunter.io could help find verified business emails.
**Data Storage:** While CSV/Excel is used for this demo, a production version would utilize a PostgreSQL database for better scalability.


