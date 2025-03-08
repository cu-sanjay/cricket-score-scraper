from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import pytz

# Set up Chrome options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1200")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def fetch_wpl_data():
    url = "https://www.wplt20.com/"
    
    try:
        print("Starting scraping...")
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Fetch upcoming match details
        try:
            match_card = soup.find("div", class_="card-wrap")
            match_title = match_card.find("h2", class_="title").text.strip()
            match_subtitle = match_card.find("span", class_="sub-title").text.strip()
            match_date = match_card.find("span", class_="meta date").text.strip()
            match_time = match_card.find("span", class_="meta time").text.strip()
            match_status = match_card.find("span", class_="status").text.strip()
            team_a = match_card.find("div", class_="team-a").find("span", class_="fullname").text.strip()
            team_b = match_card.find("div", class_="team-b").find("span", class_="fullname").text.strip()
            venue = match_card.find("div", class_="team-venue").find("span", class_="text").text.strip()

            upcoming_match = {
                "match_title": match_title,
                "match_subtitle": match_subtitle,
                "match_date": match_date,
                "match_time": match_time,
                "match_status": match_status,
                "team_a": team_a,
                "team_b": team_b,
                "venue": venue
            }
        except Exception as e:
            print(f"Error fetching upcoming match details: {e}")
            upcoming_match = {}

        # Fetch previous match results
        previous_matches = []
        try:
            match_cards = soup.find_all("div", class_="swiper-slide card-item recent")
            for card in match_cards:
                status = card.find("span", class_="status").text.strip()
                match_number = card.find("div", class_="card-number").find("span", class_="number").text.strip()
                match_date = card.find("span", class_="meta date").text.strip()
                venue = card.find("span", class_="card-venue").text.strip()
                team_a = card.find("div", class_="team-a").find("p", class_="team-name").text.strip()
                team_a_score = card.find("div", class_="team-a").find("span", class_="score").text.strip()
                team_b = card.find("div", class_="team-b").find("p", class_="team-name").text.strip()
                team_b_score = card.find("div", class_="team-b").find("span", class_="score").text.strip()
                result = card.find("p", class_="card-footer-text").text.strip()

                previous_matches.append({
                    "match_number": match_number,
                    "status": status,
                    "date": match_date,
                    "venue": venue,
                    "team_a": team_a,
                    "team_a_score": team_a_score,
                    "team_b": team_b,
                    "team_b_score": team_b_score,
                    "result": result
                })
        except Exception as e:
            print(f"Error fetching previous matches: {e}")

        # Get current timestamp in IST
        ist = pytz.timezone("Asia/Kolkata")
        timestamp_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")

        # Store data in JSON format
        wpl_data = {
            "upcoming_match": upcoming_match,
            "previous_matches": previous_matches,
            "last_updated": timestamp_ist
        }

        with open("wpl_data.json", "w") as json_file:
            json.dump(wpl_data, json_file, indent=4)

        print("Scraping completed. Data saved to wpl_data.json.")

    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        driver.quit()

# Run the function
fetch_wpl_data()
