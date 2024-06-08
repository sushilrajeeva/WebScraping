# First install beautifulsoup4 from your terminal
# pip install beautifulsoup4
# Then install lxml to parse the html web content to python objects
# pip install lxml
# Install request library to request from internet

from bs4 import BeautifulSoup
import requests
import httpx
import random
import time
from tqdm import tqdm

import re

import pandas as pd

# To avoid 403 scraping https error i am using scrapfly sdk python api to retrieve the data
from scrapfly import ScrapflyClient, ScrapeConfig


def find_jobs():
    # getting all software engineer role job opening from linkedin in last 24 hours in USA

    #skills = input('Enter your skill: ').strip()
    skills = "Software Engineering"
    place = "New York"
    res_len = 10

    # Scrapfly API key and configuration
    SCRAPFLY_API_KEY = "scp-live-ed3f3d4921444e129c9e2fda5d65ce16"

    # Define headers to mimic a real browser request
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
    }

    # URL to scrape
    url = 'https://www.indeed.com/jobs?q=software+engineer&l=new+york%2C+ny&radius=50&fromage=1&vjk=551e32423889effc'

    # Scrapfly API endpoint
    scrapfly_url = f"https://api.scrapfly.io/scrape?key={SCRAPFLY_API_KEY}&url={url}&tags=player,project:default&asp=true&render_js=true"

    # Make the request to Scrapfly
    response = requests.get(scrapfly_url, headers=HEADERS)
    data = response.json()

    # Check if the response is successful
    if response.status_code == 200 and data.get('result'):
        # Extract HTML content from Scrapfly response
        html_text = data['result']['content']
        
        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(html_text, 'lxml')

        print("success")
        
        # Print the parsed HTML (optional)
        # print(soup.prettify())
        
        # Find all the job listings
        jobs = soup.find_all('li', class_="css-5lfssm eu4oa1w0")


        
        # Initialize a list to hold the job data
        job_data = []

        # Iterate over each job listing
        for index, job in enumerate(jobs):
            # Extract job title
            job_title = job.find('h2', class_='jobTitle css-198pbd eu4oa1w0')
            job_title_text = job_title.text.strip() if job_title else "N/A"
            
            # Extract company name
            company_name = job.find('span', {'data-testid': 'company-name'})
            company_name_text = company_name.text.strip() if company_name else "N/A"
            
            # Extract job location
            job_location = job.find('div', {'data-testid': 'text-location'})
            job_location_text = job_location.text.strip() if job_location else "N/A"
            
            # Extract salary information
            salary_span = job.find('div', class_='metadata salary-snippet-container css-5zy3wz eu4oa1w0')
            salary_text = salary_span.text.strip() if salary_span else "N/A"
            
            
            # Initialize average salary values
            avg_yearly_salary = None
            avg_hourly_salary = None
            
            # Compute average yearly salary if salary information is available
            if 'a year' in salary_text:
                salary_range = re.findall(r'\$[\d,]+', salary_text)
                if salary_range and len(salary_range) == 2:
                    low = int(salary_range[0].replace('$', '').replace(',', ''))
                    high = int(salary_range[1].replace('$', '').replace(',', ''))
                    avg_yearly_salary = (low + high) / 2
                elif salary_range:
                    avg_yearly_salary = int(salary_range[0].replace('$', '').replace(',', ''))
            elif 'an hour' in salary_text:
                salary_range = re.findall(r'\$[\d,]+', salary_text)
                if salary_range and len(salary_range) == 2:
                    low = int(salary_range[0].replace('$', '').replace(',', ''))
                    high = int(salary_range[1].replace('$', '').replace(',', ''))
                    avg_hourly_salary = (low + high) / 2
                elif salary_range:
                    avg_hourly_salary = int(salary_range[0].replace('$', '').replace(',', ''))
                avg_yearly_salary = avg_hourly_salary * 1920
            
            # Compute average hourly salary if avg_yearly_salary is available
            if avg_yearly_salary:
                avg_hourly_salary = avg_yearly_salary / 1920
            
            # Append the job details to the list
            job_data.append([index + 1, job_title_text, company_name_text, job_location_text, avg_yearly_salary, avg_hourly_salary])
        
        # Create a DataFrame from the job data
        df = pd.DataFrame(job_data, columns=["Sl No", "Job Title", "Company Name", "Location", "Avg Yearly Salary", "Avg Hourly Salary"])

        # Print the DataFrame
        print(df)
        print("Size of the dataframe: ", df.size)


    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        print(data)

if __name__ == '__main__':
    while True:
        print("Fetching new Job Listing")
        find_jobs()
        time_wait = 30
        for remaining in tqdm(range(time_wait, 0, -1), desc="Fetching new data in", unit="s"):
            time.sleep(1)
