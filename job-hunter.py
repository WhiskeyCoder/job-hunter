import json
import os
import threading
import time
import random
import re
from datetime import datetime, date, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from jobspy import scrape_jobs

# --- Search Parameters ---
SEARCH_TERMS = [
    "Term 1", "Term 2", "Term 3", "Term 4", "Term 5",
    "Term 6", "Term 7", "Term 8", "Term 9"
]
LOCATIONS = ["Location 1", "Location 2", "Location 3"]
SITE_NAMES = ["indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "bayt", "naukri"]

# --- Output File Setup ---
DATE_STR = datetime.now().strftime('%Y-%m-%d')
OUTPUT_FILE = f"job_results_{DATE_STR}.json"
MAX_WORKERS = 4
RESULTS_WANTED = 25
HOURS_OLD = 24

write_lock = threading.Lock()
seen_hashes = set()

# --- Utilities ---
def clean_html(text):
    return re.sub(r'<[^>]+>', '', text).strip() if isinstance(text, str) else "none"

def fill_none(job: dict) -> dict:
    cleaned = {}
    for k, v in job.items():
        if isinstance(v, (datetime, date)):
            cleaned[k] = v.isoformat()
        elif v is None or str(v).strip().lower() == "none":
            cleaned[k] = "none"
        elif isinstance(v, str):
            cleaned[k] = v.strip()
        else:
            cleaned[k] = str(v)
    return cleaned

def hash_job(job):
    return hash(json.dumps(job, sort_keys=True))

def write_job_to_json(job: dict):
    with write_lock:
        job = fill_none(job)
        job["description"] = clean_html(job.get("description", "none"))
        job["fetched_at"] = datetime.now(timezone.utc).isoformat()
        job_hash = hash_job(job)

        if job_hash in seen_hashes:
            return
        seen_hashes.add(job_hash)

        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump({"timestamp": datetime.now().isoformat(), "job_count": 0, "jobs": []}, f)

        with open(OUTPUT_FILE, 'r+', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                data = {"timestamp": datetime.now().isoformat(), "job_count": 0, "jobs": []}
            data["jobs"].append(job)
            data["job_count"] = len(data["jobs"])
            f.seek(0)
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.truncate()

# --- Core Scraper Function ---
def fetch_and_save(site, term, location):
    print(f"\n🔍 Searching: {term} in {location} from {site} (remote=True)...", flush=True)
    time.sleep(random.uniform(2, 4))  # polite delay

    try:
        jobs = scrape_jobs(
            site_name=site,
            search_term=term,
            location=location,
            results_wanted=RESULTS_WANTED,
            hours_old=HOURS_OLD,
            is_remote=True
        )

        if len(jobs) == 0 and site == "linkedin":
            print(f"⚠️ No jobs with is_remote=True → retrying with is_remote=None", flush=True)
            jobs = scrape_jobs(
                site_name=site,
                search_term=term,
                location=location,
                results_wanted=RESULTS_WANTED,
                hours_old=HOURS_OLD,
                is_remote=False
            )

        count = len(jobs)
        for _, row in jobs.iterrows():
            write_job_to_json(row.to_dict())

        print(f"✅ {site} → {term} in {location} → {count} job(s) found", flush=True)

    except Exception as e:
        print(f"💥 ERROR: {site} → {term} in {location} → {e}", flush=True)

# --- Main Execution ---
def main():
    print("🕵️ Starting full scrape...\n", flush=True)

    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump({"timestamp": datetime.now().isoformat(), "job_count": 0, "jobs": []}, f)

    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for site in SITE_NAMES:
            for term in SEARCH_TERMS:
                for location in LOCATIONS:
                    tasks.append(executor.submit(fetch_and_save, site, term, location))

        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                print(f"💥 Uncaught exception in thread: {e}", flush=True)

    print(f"\n📁 Done! Results saved to: {OUTPUT_FILE}", flush=True)

if __name__ == "__main__":
    main()
