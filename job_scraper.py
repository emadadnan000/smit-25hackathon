import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Initialize lists for data storage
jobs_data = []

def setup_driver():
    """Set up and configure the Chrome WebDriver"""
    options = Options()
    # Comment out the headless option if you want to see the browser
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Add anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Create and return the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # Disguise webdriver usage
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrape_indeed():
    """Scrape Indeed for job listings"""
    driver = setup_driver()
    
    # Parameters for the search
    job_title = "python"
    location = "New York, NY"
    
    # Format the URL
    search_url = f"https://www.indeed.com/jobs?q={job_title}&l={location}"
    print(f"Searching for: {job_title} in {location}")
    print(f"URL: {search_url}")
    
    try:
        # Navigate to Indeed
        driver.get(search_url)
        print("Page loaded, waiting for content...")
        time.sleep(3)  # Allow time for the page to fully load
        
        # Save the page source for debugging
        with open("indeed_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            print("Saved page source for debugging")
        
        # Parse with BeautifulSoup for easier HTML navigation
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Try to find job cards using multiple possible selectors
        job_cards = []
        
        # Check for the mosaic container first (old Indeed structure)
        mosaic_container = soup.find("div", {"id": "mosaic-provider-jobcards"})
        if mosaic_container:
            print("Found mosaic container")
            job_cards = mosaic_container.find_all("li")
        
        # If that didn't work, try the newer structure
        if not job_cards:
            print("Trying alternative job card selectors...")
            job_cards = soup.select(".job_seen_beacon, .jobCard, .job-card")
        
        # If we still don't have job cards, try a more general approach
        if not job_cards:
            print("Trying general selectors...")
            # Look for elements that have job-related content
            job_cards = [div for div in soup.find_all("div") 
                        if div.find("h2") or div.find("a", href=lambda h: h and "/rc/clk" in h)]
        
        print(f"Found {len(job_cards)} potential job listings")
        
        # Process each job card
        for i, card in enumerate(job_cards):
            job_info = {}
            
            # Try to extract job title with multiple selector patterns
            try:
                # Try standard selectors first
                title_elem = (card.find("h2", {"class": "jobTitle"}) or 
                             card.find("a", {"class": "jcs-JobTitle"}) or
                             card.select_one("h2 span"))
                
                if title_elem:
                    job_info["title"] = title_elem.text.strip()
                else:
                    # Look for any link that might be a job title
                    title_link = card.find("a")
                    if title_link and title_link.text.strip():
                        job_info["title"] = title_link.text.strip()
            except Exception as e:
                print(f"Error extracting job title: {e}")
            
            # Try to extract company name
            try:
                company_elem = (card.find("span", {"data-testid": "company-name"}) or
                              card.find("span", {"class": "companyName"}))
                if company_elem:
                    job_info["company"] = company_elem.text.strip()
            except Exception as e:
                print(f"Error extracting company name: {e}")
            
            # Try to extract location
            try:
                location_elem = (card.find("div", {"data-testid": "text-location"}) or
                               card.find("div", {"class": "companyLocation"}))
                if location_elem:
                    job_info["location"] = location_elem.text.strip()
            except Exception as e:
                print(f"Error extracting location: {e}")
            
            # Try to extract job details/description
            try:
                details_elem = (card.find("div", {"class": "job-snippet"}) or
                              card.find("div", {"class": "jobMetaDataGroup"}) or
                              card.find("div", {"class": "summary"}))
                if details_elem:
                    job_info["details"] = details_elem.text.strip()
            except Exception as e:
                print(f"Error extracting job details: {e}")
            
            # Only add if we have at least a title or company
            if job_info.get("title") or job_info.get("company"):
                print(f"Job {i+1}: {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}")
                jobs_data.append(job_info)
        
        print(f"Successfully scraped {len(jobs_data)} jobs")
        
        # Save the data to CSV
        if jobs_data:
            df = pd.DataFrame(jobs_data)
            df.to_csv("indeed_jobs.csv", index=False)
            print(f"Data saved to indeed_jobs.csv")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    scrape_indeed()