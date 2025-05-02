# job-hunter
Two-part toolchain designed to automate job hunting using local language models. Built while learning AI stuff, the system scrapes job listings from across major platforms, then filters them using a custom LM Studio prompt to detect high-fit opportunities based on a detailed resume profile.


## 💼 Project Purpose
I created this project to:
- Streamline my search for work.
- Experiment with local LLM integration (LM Studio) for practical filtering use cases.
- Showcase how AI can automate niche job hunting for high-skill professionals.
- Help others in similar fields cut through irrelevant listings and spot ideal roles instantly.

## 📦 Features
### 🔎 job-search.py
- Scrapes jobs from LinkedIn, Indeed, Google, Glassdoor, ZipRecruiter, Bayt, and Naukri.
- Uses jobspy for robust multi-source crawling.
- Supports keyword + location + remote filtering.
- Outputs a single JSON file with cleaned and deduplicated job data.

### 🧠 job_filter_ai.py
- Uses a local LLM (LM Studio) to evaluate each job against a detailed resume.
- Simple YES/NO classification for “Is this job a good match?”
- Writes strong matches to a CSV file, with logging and colored CLI feedback.
- Resume and prompt can be customized for other professions.

## 🚀 Getting Started
Requirements
- Python 3.9+
- jobspy, requests, colorama
- A running instance of LM Studio or compatible OpenAI-style local API server (e.g., llama.cpp, LM Studio)

### Install dependencies
```pip install jobspy requests colorama```

Step 1: Run the job scraper
```python job-search.py```
This creates a job_results_<date>.json file with all job listings.

Step 2: Run the job filter
```python job_filter_ai.py --api-url http://localhost:1234/v1/chat/completions --model meta-llama-3.1-8b-instruct```
This filters jobs using your resume and saves results to filtered_jobs.csv.

## 🧬 Customization
- Resume (Prompt): Edit the MY_RESUME string in job_filter_ai.py to match your background.
- Keywords & Sites: Update SEARCH_TERMS, LOCATIONS, and SITE_NAMES in job-search.py.
- Model: Replace the model name/API URL with your preferred LLM endpoint (local or hosted).


## 🧠 Why This Is Cool
- ✅ Runs 100% locally (no OpenAI costs!)
- ✅ Real-world use of LLMs in job hunting
- ✅ Tailored to for your needs
- ✅ Easy to modify for any career path

## 📄 License
MIT License – free to use, modify, and share.


