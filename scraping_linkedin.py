from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pandas as pd 
import os 

# LinkedIn credentials - replace with your own
LINKEDIN_EMAIL = "your_email@example.com"  # Replace with your LinkedIn email
LINKEDIN_PASSWORD = "your_password"  # Replace with your LinkedIn password

# Initialize data list and webdriver
data = []
driver = webdriver.Chrome()
driver.maximize_window()

# First login to LinkedIn
driver.get('https://www.linkedin.com/login')
print("Navigating to LinkedIn login page...")

try:
    # Wait for login page to load and enter credentials
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    
    # Enter email/username
    email_elem = driver.find_element(By.ID, "username")
    email_elem.clear()
    email_elem.send_keys(LINKEDIN_EMAIL)
    print("Email entered...")
    
    # Enter password
    password_elem = driver.find_element(By.ID, "password")
    password_elem.clear()
    password_elem.send_keys(LINKEDIN_PASSWORD)
    print("Password entered...")
    
    # Click login button
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    print("Login button clicked...")
    
    # Wait for login to complete
    time.sleep(5)  # Allow time for login to process
    
    # Check if we're successfully logged in by looking for the feed
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "global-nav"))
        )
        print("Successfully logged in!")
    except TimeoutException:
        print("Login may have failed or encountered additional verification.")
        
    # Now navigate to the jobs search
    search_term = "frontend developer"  # You can make this variable
    driver.get(f'https://www.linkedin.com/jobs/search/?keywords={search_term}&origin=SUGGESTION&position=1&pageNum=0')
    print(f"Navigating to jobs search for '{search_term}'...")
    
    # Wait for the job listings to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
    )
    
    # Give time for dynamic content to fully load
    print("Page loaded. Waiting for dynamic content...")
    time.sleep(3)
    
    # Get the list of job postings
    job_listings = driver.find_elements(By.CSS_SELECTOR, ".jobs-search__results-list li")
    print(f"Found {len(job_listings)} job listings")
    
    # Scroll through the page to ensure all elements load
    for i in range(3):
        driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(0.5)
    
    for job in job_listings:
        try:
            job_title = job.find_element(By.CLASS_NAME, 'base-search-card__title').text
            company_name = job.find_element(By.CSS_SELECTOR, '.base-search-card__subtitle').text.strip()
            location = job.find_element(By.CSS_SELECTOR, '.job-search-card__location').text.strip()
            current_date = pd.Timestamp.now().strftime('%Y-%m-%d')
            
            data.append({
                'job_title': job_title,
                'company_name': company_name,
                'location': location,
                'scrapped_date': current_date
            })
            
            print(f"Scraped: {job_title} at {company_name}")
        except Exception as e:
            print(f"Error extracting job details: {e}")
    
    # Add a delay to keep the browser open for a while
    print("Finished scraping, waiting for 5 seconds before closing...")
    time.sleep(5)
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Save the data before closing the browser
    if data:
        # Convert the collected data into a DataFrame
        df = pd.DataFrame(data)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        current_date = pd.Timestamp.now().strftime('%Y-%m-%d')
        custom_name = f'linkedin_jobs_{current_date}.csv'
        file_path = os.path.join(script_dir, custom_name)
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"Data saved to {file_path}")
    else:
        print("No data was collected to save")
    
    # Close the browser
    driver.quit()