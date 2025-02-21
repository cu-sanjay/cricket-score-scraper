from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

# Setup Chrome options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1200")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def fetch_live_match():
    url = "https://www.icc-cricket.com/tournaments/champions-trophy-2025"
    
    try:
        print("Starting scraping...")
        driver.get(url)
        time.sleep(5)  # Allow page to load

        soup = BeautifulSoup(driver.page_source, "html.parser")

        teams = [elem.text.strip() for elem in driver.find_elements(By.CLASS_NAME, "si-team-name")]
        scores = [elem.text.strip() for elem in driver.find_elements(By.CLASS_NAME, "si-score")]

        try:
            run_rate = driver.find_element(By.CLASS_NAME, "si-over").text.strip()
        except:
            run_rate = "N/A"

        try:
            match_status = driver.find_element(By.CLASS_NAME, "si-text").text.strip()
        except:
            match_status = "N/A"

        standings = []
        table_body = soup.find("tbody")
        if table_body:
            for row in table_body.find_all("tr"):
                columns = row.find_all("td")
                if len(columns) >= 5:
                    standings.append({
                        "pos": columns[0].text.strip(),
                        "team": columns[1].text.strip(),
                        "played": columns[2].text.strip(),
                        "nrr": columns[3].text.strip(),
                        "points": columns[4].text.strip()
                    })

        match_data = {
            "teams": teams,
            "scores": scores,
            "run_rate": run_rate,
            "match_status": match_status,
            "standings": standings
        }

        # Save to JSON file
        with open("data.json", "w") as json_file:
            json.dump(match_data, json_file, indent=4)

        print("Scraping completed and data saved to data.json.")

    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        driver.quit()  # Close the browser session

# Execute the scraper once
fetch_live_match()
