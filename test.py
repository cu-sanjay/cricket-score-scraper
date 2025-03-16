from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import pytz
import logging
from guara.transaction import AbstractTransaction, Application

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Chrome options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1200")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
options.add_argument("--log-level=0")  
options.add_experimental_option('excludeSwitches', ['enable-logging']) 

# Transaction Classes
class NavigateToWPL(AbstractTransaction):
    def do(self, url, **kwargs):
        logger.info(f"Navigating to {url}")
        self._driver.get(url)
        try:
            WebDriverWait(self._driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info("Page loaded successfully")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            logger.debug(f"Page source: {self._driver.page_source[:1000]}") 
            raise

class FetchUpcomingMatch(AbstractTransaction):
    def do(self, **kwargs):
        soup = BeautifulSoup(self._driver.page_source, "html.parser")
        upcoming_match = {}
        try:
            match_card = soup.find("div", class_="card-wrap")
            if match_card:
                upcoming_match = {
                    "match_title": match_card.find("h2", class_="title").text.strip(),
                    "match_subtitle": match_card.find("span", class_="sub-title").text.strip(),
                    "match_date": match_card.find("span", class_="meta date").text.strip(),
                    "match_time": match_card.find("span", class_="meta time").text.strip(),
                    "match_status": match_card.find("span", class_="status").text.strip(),
                    "team_a": match_card.find("div", class_="team-a").find("span", class_="fullname").text.strip(),
                    "team_b": match_card.find("div", class_="team-b").find("span", class_="fullname").text.strip(),
                    "venue": match_card.find("div", class_="team-venue").find("span", class_="text").text.strip(),
                }
                logger.info("Upcoming match fetched successfully")
            else:
                logger.info("No upcoming match found (tournament may have ended)")
        except AttributeError as e:
            logger.warning(f"No upcoming match data available: {e}")
        except Exception as e:
            logger.error(f"Error fetching upcoming match: {e}")
        return upcoming_match

class FetchPreviousMatches(AbstractTransaction):
    def do(self, **kwargs):
        soup = BeautifulSoup(self._driver.page_source, "html.parser")
        previous_matches = []
        try:
            match_cards = soup.find_all("div", class_="swiper-slide")
            if not match_cards:
                logger.warning("No match cards found on page")
                return previous_matches

            for card in match_cards:
                status_elem = card.find("span", class_="status")
                if not status_elem or "Match Ended" not in status_elem.text:
                    continue

                match_data = {
                    "match_number": card.find("div", class_="card-number").find("span", class_="number").text.strip() if card.find("div", class_="card-number") else "N/A",
                    "status": status_elem.text.strip(),
                    "date": card.find("span", class_="meta date").text.strip() if card.find("span", class_="meta date") else "N/A",
                    "venue": card.find("span", class_="card-venue").text.strip() if card.find("span", class_="card-venue") else "N/A",
                    "team_a": card.find("div", class_="team-a").find("p", class_="team-name").text.strip() if card.find("div", class_="team-a") else "N/A",
                    "team_a_score": card.find("div", class_="team-a").find("span", class_="score").text.strip() if card.find("div", class_="team-a") and card.find("div", class_="team-a").find("span", class_="score") else "N/A",
                    "team_b": card.find("div", class_="team-b").find("p", class_="team-name").text.strip() if card.find("div", class_="team-b") else "N/A",
                    "team_b_score": card.find("div", class_="team-b").find("span", class_="score").text.strip() if card.find("div", class_="team-b") and card.find("div", class_="team-b").find("span", class_="score") else "N/A",
                    "result": card.find("p", class_="card-footer-text").text.strip() if card.find("p", class_="card-footer-text") else "N/A",
                }
                previous_matches.append(match_data)
            logger.info(f"Fetched {len(previous_matches)} previous matches")
        except Exception as e:
            logger.error(f"Error fetching previous matches: {e}")
        return previous_matches

class SaveData(AbstractTransaction):
    def do(self, upcoming_match, previous_matches, **kwargs):
        ist = pytz.timezone("Asia/Kolkata")
        timestamp_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
        wpl_data = {
            "upcoming_match": upcoming_match,
            "previous_matches": previous_matches,
            "last_updated": timestamp_ist,
        }
        try:
            with open("wpl_data.json", "w") as json_file:
                json.dump(wpl_data, json_file, indent=4)
            logger.info("Data saved to wpl_data.json")
        except Exception as e:
            logger.error(f"Error saving data: {e}")

# Main Script
if __name__ == "__main__":
    logger.info("Starting scraping process")
    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
        try:
            app = Application(driver)
            app.at(NavigateToWPL, url="https://www.wplt20.com/")
            upcoming_match = app.at(FetchUpcomingMatch).result
            previous_matches = app.at(FetchPreviousMatches).result
            app.at(SaveData, upcoming_match=upcoming_match, previous_matches=previous_matches)
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            logger.debug(f"Final page source: {driver.page_source[:1000]}")
    logger.info("Scraping process completed")
