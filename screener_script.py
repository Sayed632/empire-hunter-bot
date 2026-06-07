import os
import requests
from bs4 import BeautifulSoup
import telebot

# --- ENVIRONMENT VARIABLES SETUP ---
USERNAME = os.getenv('SCREENER_USERNAME')
PASSWORD = os.getenv('SCREENER_PASSWORD')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MY_CHAT_ID = os.getenv('MY_CHAT_ID')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

LOGIN_URL = "https://www.screener.in/login/"
RUN_QUERY_URL = "https://www.screener.in/screen/raw/"

# --- QUERIES DEFINITION ---
QUERIES = {
    "🎯 BIG_MONEY HITS": (
        "(Change in FII holding > 0.5 OR Change in DII holding > 0.5) AND "
        "Market Capitalization > 1000 AND "
        "Return on equity > 10 AND "
        "Sales growth > 10 AND "
        "Debt to equity < 1 AND "
        "Promoter holding > 50 AND "
        "Pledged percentage < 5"
    ),
    "💎 SMALL STOCKS HITS": (
        "Current price < 50 AND "
        "Market Capitalization > 200 AND "
        "Volume > 100000 AND "
        "Debt to equity < 0.5 AND "
        "Promoter holding > 40 AND "
        "Pledged percentage == 0 AND "
        "(Change in FII holding > 0 OR Change in DII holding > 0) AND "
        "Sales growth 3Years > 10 AND "
        "Profit growth 3Years > 10"
    )
}

def parse_screener_query(session, query_string):
    """Submits search constraints via the browser-aligned GET query model."""
    try:
        # Match browser query parameters explicitly
        params = {
            'page': '1',
            'q': query_string
        }
        
        response = session.get(RUN_QUERY_URL, params=params)
        if response.status_code != 200:
            print(f"Server rejection status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Isolate the data table container
        table = soup.find('table', {'class': 'data-table'})
        if not table:
            print("Could not locate data table. Check if query format contains structural bugs.")
            return []
            
        rows = table.find_all('tr')[1:]  # Drops table header row
        stocks = []
        for row in rows[:15]:  # Capture top 15 target hits
            cols = row.find_all('td')
            if len(cols) > 2:
                # Isolate target stock name and link text elements
                name_element = cols[1].find('a')
                name = name_element.text.strip() if name_element else cols[1].text.strip()
                price = cols[2].text.strip()
                stocks.append(f"🔹 **{name}** - CMP: ₹{price}")
        return stocks
    except Exception as e:
        print(f"Error parsing raw table text elements: {str(e)}")
        return []

def run_screener_automation():
    print("🔒 Building a secure scraping session tunnel to Screener.in...")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Upgrade-Insecure-Requests': '1'
    })
    
    try:
        # Extract anti-forgery verification tokens from login DOM elements
        login_init = session.get(LOGIN_URL)
        init_soup = BeautifulSoup(login_init.text, 'html.parser')
        csrf_token = init_soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        payload = {
            'username': USERNAME,
            'password': PASSWORD,
            'csrfmiddlewaretoken': csrf_token
        }
        
        # Execute validation authorization handshake
        post_response = session.post(LOGIN_URL, data=payload, headers={'Referer': LOGIN_URL})
        
        # Double check login success by looking for dashboard elements
        if "login" in post_response.url or "logout" not in post_response.text.lower():
            print("❌ Authentication failed. Re-verify account credential secrets.")
            return
            
    except Exception as e:
        print(f"Connection failure to logging routing services: {str(e)}")
        return

    print("✅ Authenticated! Running your screen criteria profiles...")
    
    for screen_name, text_query in QUERIES.items():
        print(f"Scanning metrics for system block: {screen_name}")
        hits = parse_screener_query(session, text_query)
        
        if hits:
            message_payload = f"🔥 **{screen_name}** 🔥\n\n" + "\n".join(hits)
            bot.send_message(MY_CHAT_ID, message_payload, parse_mode='Markdown')
            print(f"🚀 Telegram update shipped for {screen_name}")
        else:
            bot.send_message(MY_CHAT_ID, f"📋 **{screen_name}**\n\nNo stock triggers met criteria today.")
            print(f"📁 Scan finished: 0 hits for {screen_name}")

if __name__ == "__main__":
    run_screener_automation()
    
