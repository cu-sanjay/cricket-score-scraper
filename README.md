# **Live Cricket Score Scraper**  

A **Python-based web scraper** that fetches **live and past match data** from the **[Women's Premier League (WPL)](https://www.wplt20.com/) website** using **Selenium, BeautifulSoup, and GitHub Actions**. The script runs automatically every **Hour** and updates a JSON file with match details.  
> [!IMPORTANT]
> This project is for **educational purposes only**. It does not store, redistribute, or claim ownership over any third-party data. Users are responsible for complying with website terms of service.  

## **Features**  

1. **Automated Web Scraping** – Uses **Selenium + BeautifulSoup** to extract match details dynamically.  
2. **GitHub Actions Integration** – Runs automatically on schedule without manual execution.  
3. **Web Development Ready** – Data is stored in **wpl_data.json**, which can be used in web applications.  
4. **Bypass Restrictions** – Implements **headless browsing, user-agent rotation**, and **dynamic content handling**.  

## **Usage**  

### **Run Locally**  

1. **Clone the repository**  
   ```sh
   git clone https://github.com/cu-sanjay/cricket-score-scraper
   cd cricket-score-scraper
   ```

2. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the script**  
   ```sh
   python test.py
   ```

### **Automated Execution via GitHub Actions**  

- The script is scheduled to run every **1 hour** using **GitHub Actions**.  
- It fetches live match data and commits changes automatically.  
- No manual intervention is needed once set up.  

## **Enhancements & Workarounds**  

1. **Handling Strict Websites**
2. Rotate **user-agents** to prevent detection.
3. Use **headless browsing** for minimal footprint.
4. Simulate **human interactions** (scrolling, waiting, retries).
5. Extract data from **network requests** instead of the rendered page.  
> [!TIP]
> **Web Development Integration**
> - Serve **wpl_data.json** via **Flask/Django API**.
> - Fetch and display match data in **React/Next.js frontend**.
> - Automate updates via **Telegram/Reddit/Discord bot**.  
