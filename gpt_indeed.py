import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import time
import json
import pandas as pd
import os

# Initialize data list
job_data = []

# Set target URL and headers
target_url = "https://www.indeed.com/jobs?q=python&l=New+York%2C+NY&vjk=8bf2e735050604df"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="118"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

print("Sending request to Indeed...")
try:
    response = requests.get(target_url, headers=headers)
    print(f"Status code: {response.status_code}")

    # Parse HTML response
    soup = BeautifulSoup(response.text, 'html.parser')

    # Save HTML for debugging
    debug_dir = os.path.dirname(os.path.abspath(__file__))
    debug_file = os.path.join(debug_dir, "indeed_full_page.html")
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
        print(f"Saved full page HTML for debugging to {debug_file}")
    
    # Check if we got a valid response
    if not soup.body:
        print("WARNING: No <body> tag found in the response.")
        print("Using the root element instead.")
        root_element = soup.html if soup.html else soup
    else:
        root_element = soup.body
    
    # Inspect page structure - safely
    print("\n--- Page Structure Analysis ---")
    
    # Look for job cards throughout the entire document
    all_divs = soup.find_all(['div', 'li'])
    print(f"Total divs and li elements found: {len(all_divs)}")
    
    # Look for job containers first - they're more reliable
    job_containers = soup.find_all(['div', 'ul'], 
                    class_=lambda c: c and any(keyword in str(c).lower() 
                    for keyword in ["job", "result", "mosaic", "jobsearch"]))
    
    print(f"Found {len(job_containers)} elements with job-related classes")
    
    # Process containers if found
    if job_containers:
        for container in job_containers:
            print(f"Container with class {container.get('class', 'None')}")
            
            # Look for job cards in each container
            job_cards = container.find_all(['div', 'li'], 
                       class_=lambda c: c and any(keyword in str(c).lower() 
                       for keyword in ["job", "card", "result", "jobsearch"]))
            
            print(f"Found {len(job_cards)} potential job cards")
            
            # Process each job card
            for job_card in job_cards:
                job_info = {}
                
                # Try to get job title
                for title_tag in ['h2', 'h3', 'a', 'span']:
                    title_elem = job_card.find(title_tag)
                    if title_elem and title_elem.text.strip():
                        job_info["job_title"] = title_elem.text.strip()
                        break
                
                # Try to get company name
                company_elem = job_card.find(['span', 'div'], 
                              string=lambda s: s and len(s.strip()) > 0,
                              class_=lambda c: c and any(term in str(c).lower() for term in ["company"]))
                if company_elem:
                    job_info["company_name"] = company_elem.text.strip()
                
                # Try to get location
                location_elem = job_card.find(['div', 'span'], 
                               class_=lambda c: c and any(term in str(c).lower() for term in ["location"]))
                if location_elem:
                    job_info["location"] = location_elem.text.strip()
                
                # Add any job that has some data
                if job_info.get("job_title") or job_info.get("company_name"):
                    job_data.append(job_info)
                    print(f"Added job: {job_info.get('job_title', 'Unknown')} at {job_info.get('company_name', 'Unknown')}")
    
    # Fallback: if no jobs found, look for specific patterns
    if not job_data:
        print("\nFallback method: Looking for specific Indeed patterns...")
        
        # Check for common Indeed job card patterns
        job_cards = soup.find_all(['div', 'li'], class_=lambda c: c and 'job_' in str(c).lower())
        
        for card in job_cards:
            job_info = {}
            
            # Try to find job title - often in an anchor tag
            title_elem = card.find('a', href=lambda h: h and '/job/' in str(h))
            if title_elem:
                job_info["job_title"] = title_elem.text.strip()
            
            # Find any span that might contain company name
            spans = card.find_all('span')
            for span in spans:
                text = span.text.strip()
                if text and len(text) > 0 and '(' not in text and ')' not in text:
                    job_info["company_name"] = text
                    break
            
            # Add job if we found useful data
            if job_info:
                job_data.append(job_info)
                print(f"Found job via fallback: {job_info.get('job_title', 'Unknown')}")
    
    # If still no data, do a deep search
    if not job_data:
        print("\nDeep search for any text that might be job information...")
        
        # Look for all standalone text blocks that might have job information
        all_links = soup.find_all('a')
        for link in all_links[:20]:  # Consider the first 20 links only
            if link.text.strip() and len(link.text.strip()) > 5:
                print(f"Potential job listing text: {link.text.strip()[:50]}...")
                job_data.append({"job_title": link.text.strip(), "source": "deep_search"})

    print(f"\nTotal jobs found: {len(job_data)}")
    
    # Save results
    if job_data:
        # Create DataFrame and save to CSV
        df = pd.DataFrame(job_data)
        csv_path = os.path.join(debug_dir, "indeed_jobs.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved {len(df)} jobs to '{csv_path}'")
        
        # Save to JSON
        json_path = os.path.join(debug_dir, "indeed_jobs.json")
        with open(json_path, "w") as f:
            json.dump(job_data, f, indent=4)
        print(f"Saved {len(job_data)} jobs to '{json_path}'")
    else:
        print("No jobs found to save.")

except Exception as e:
    print(f"Error during scraping: {str(e)}")
    import traceback
    traceback.print_exc()