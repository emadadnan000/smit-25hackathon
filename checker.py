import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrape_rozee_jobs(query="python", location="Pakistan", max_pages=3):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    base_url = "https://www.rozee.pk/job/jsearch/q/"
    search_url = f"{base_url}{query.replace(' ', '%20')}/l/{location.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(3)

    jobs = []

    for page in range(max_pages):
        print(f"Scraping page {page + 1}...")

        job_cards = driver.find_elements(By.CSS_SELECTOR, ".jobListing")

        for card in job_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, "h3 a").text.strip()
            except:
                title = "N/A"

            try:
                company = card.find_element(By.CSS_SELECTOR, ".job-info span").text.strip()
            except:
                company = "N/A"

            try:
                location = card.find_element(By.CSS_SELECTOR, ".job-location").text.strip()
            except:
                location = "N/A"

            try:
                date_posted = card.find_element(By.CSS_SELECTOR, ".job-date").text.strip()
            except:
                date_posted = "N/A"

            try:
                summary = card.find_element(By.CSS_SELECTOR, ".job-desc").text.strip()
                skills = ", ".join([kw for kw in ['Python', 'SQL', 'Excel', 'Communication', 'JavaScript']
                                    if kw.lower() in summary.lower()])
            except:
                skills = "N/A"

            jobs.append({
                "Title": title,
                "Company": company,
                "Location": location,
                "Date Posted": date_posted,
                "Skills": skills
            })

        # Try to go to the next page
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next")
            next_button.click()
            time.sleep(2)
        except:
            print("No more pages.")
            break

    driver.quit()
    return jobs


# Run the scraper
if __name__ == "__main__":
    results = scrape_rozee_jobs("python", "Pakistan", max_pages=3)
    for i, job in enumerate(results, 1):
        print(f"\nJob {i}")
        for k, v in job.items():
            print(f"{k}: {v}")
