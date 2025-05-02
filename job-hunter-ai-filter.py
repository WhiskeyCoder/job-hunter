#!/usr/bin/env python3

import json
import csv
import os
import sys
import argparse
import logging
import requests
from datetime import datetime
from typing import List, Dict
from colorama import Fore, Style, init

# Init color output
init()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("job_filter_ai_gpt4all.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Sample generic tech-focused resume
CANDIDATE_RESUME = """
  An experienced IT professional with a strong background in software development, automation, and cloud infrastructure.
  Skilled in designing and deploying scalable systems, building machine learning tools, and automating data pipelines using Python, Bash, and containerized environments. 
  
  Core competencies include:
  - Full-stack software development
  - Cloud computing (AWS, Azure, GCP)
  - CI/CD and DevOps practices
  - Python scripting, REST APIs, and data transformation
  - ML model integration and inference workflows
  - Automation of repetitive tasks and reporting
  - Database engineering (SQL, MongoDB)
  - Working with large datasets and distributed systems
  
  Education:
  - BSc in Computer Science or related technical field
  
  Certifications (examples):
  - AWS Certified Solutions Architect
  - Microsoft Azure Administrator Associate
  - Certified Kubernetes Administrator (CKA)
  
  Preferences:
  - Focus on remote or hybrid opportunities
  - Open to international and contract-based work
"""

# GPT4All wrapper
class LocalLLM:
    def __init__(self, api_url: str, model: str):
        self.api_url = api_url
        self.model = model

    def query(self, job_post: str) -> str:
        prompt = f"""
                  You are an expert recruiter helping a highly skilled IT professional assess job fit.
                  
                  Resume:
                  ---
                  {CANDIDATE_RESUME}
                  ---
                  
                  Job Listing:
                  ---
                  {job_post}
                  ---
                  
                  Is this job a strong match for the candidate?
                  Only reply: YES or NO
                """

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.28,
            "max_tokens": 20
        }

        try:
            res = requests.post(self.api_url, json=payload, timeout=30)
            res.raise_for_status()
            data = res.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
            elif "response" in data:
                return data["response"].strip()
        except Exception as e:
            logger.error(f"Query failed: {e}")
        return "NO"

def find_today_json_file():
    today_str = datetime.today().strftime('%Y-%m-%d')
    prefix = f"job_results_{today_str}"
    for f in os.listdir('.'):
        if f.startswith(prefix) and f.endswith('.json'):
            return f
    return None

def ensure_csv_header(file_path: str, fieldnames: List[str]):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

def main():
    parser = argparse.ArgumentParser(description="Filter jobs using local GPT4All model")
    parser.add_argument('--api-url', default='http://localhost:1234/v1/chat/completions', help='GPT4All API endpoint')
    parser.add_argument('--model', default='meta-llama-3.1-8b-instruct', help='Model name to use')
    parser.add_argument('--output', default='filtered_jobs.csv', help='Output CSV file')
    args = parser.parse_args()

    input_file = find_today_json_file()
    if not input_file:
        logger.error("❌ No job_results_<today>.json file found.")
        sys.exit(1)

    logger.info(f"📂 Loading job data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    jobs = data.get("jobs", [])
    if not jobs:
        logger.warning("⚠️ No jobs found in the file.")
        sys.exit(0)

    llm = LocalLLM(api_url=args.api_url, model=args.model)

    fieldnames = ['title', 'company', 'location', 'url', 'site', 'snippet']
    ensure_csv_header(args.output, fieldnames)

    with open(args.output, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for job in jobs:
            job_text = f"""Title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location')}
Description: {job.get('description')}"""

            decision = llm.query(job_text)
            if "YES" in decision.upper():
                print(f"{Fore.GREEN}✅ MATCH: {job.get('title')} at {job.get('company')}{Style.RESET_ALL}")
                writer.writerow({
                    'title': job.get('title'),
                    'company': job.get('company'),
                    'location': job.get('location'),
                    'url': job.get('job_url') or job.get('url', 'none'),
                    'site': job.get('site', 'none'),
                    'snippet': (job.get('description') or 'none')[:300]
                })
                csvfile.flush()
            else:
                print(f"{Fore.RED}❌ NO MATCH: {job.get('title')} at {job.get('company')}{Style.RESET_ALL}")

    logger.info(f"🎯 Matching complete. Filtered jobs saved in: {args.output}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Interrupted.")
        sys.exit(0)
