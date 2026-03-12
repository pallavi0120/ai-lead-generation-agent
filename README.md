
# AI Lead Generation Agent (Task 02)

## Overview

This autonomous AI agent monitors online signals to identify potential leads in the Real Estate and PropTech sectors. It uses RSS feeds and web scraping to find news, classifies the intent and urgency of those signals using Llama-3, and discovers key executives (CEOs/CTOs) via LinkedIn.

## Architecture

1. The system follows a four-step pipeline:Signal Monitoring: Polls Google News RSS and scrapes Inman PropTech for relevant keywords.
2. Intent Classification: Uses an LLM (Groq/Llama-3) to determine if a signal indicates a "buying" opportunity and assigns an urgency score.
3. Contact Discovery: Searches for executive LinkedIn profiles based on the identified company.
4. Reporting: Deduplicates data and exports it to a structured CSV and Excel lead list.

## Setup Instructions

1. Prerequisites
Python 3.8+
A Groq API Key (for Llama-3 inference)

2. Installation
Clone the repository and install the required dependencies:
pip install -r requirements.txt

3. Environment Configuration
Create a .env file in the root directory and add your Groq API key:
GROQ_API_KEY=your_groq_api_key_here

## Configuration

You can customize the agent's focus by modifying the following variables in the script:
Keywords/Sources: Update rss_sources or the scrape_proptech_news function to target different industries.
Filtering: Use the ignore_companies and media_domains lists to filter out news publishers and focus on private companies.
Ideal Customer Profile (ICP): The agent is currently configured for Real Estate companies adopting PropTech solutions.

## How to Run

### Manual Trigger

To run the agent once and generate the lead list immediately:
python main.py

### Scheduled Execution

The script includes a built-in scheduler that runs the agent every 24 hours by default. To keep the agent running, simply leave the script executing in your terminal.

## Output
The agent generates two files:
leads.csv: An append-only historical log of all leads found.

leads.xlsx: A structured Excel sheet containing the most recent batch of deduplicated leads.

