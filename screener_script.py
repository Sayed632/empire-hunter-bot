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
RUN_QUERY_URL = "https://www.screener.in/api/v1/screen/raw/"

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
    """Submits raw query text directly to screener execution parser engines."""
    try:
        response = session.get(RUN_QUERY_URL, params={'q': query_string})
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'data-table'})
        if not table:
            return []
            
        rows = table.find_all('tr')[1:] # Skip headers
        stocks = []
        for row in rows[:12]: # Cap output at top 12 matches per screen
            cols = row.find_all('td')
            if len(cols) > 2:
                name = cols[1].text.strip().replace('\n', '').split('  ')[0]
                price = cols[2].text.strip()
                stocks.append(f"🔹 **{name}** - CMP: ₹{price}")
        return stocks
    except Exception as e:
        print(f"Error fetching data query elements: {str(e)}")
        return []

def run_screener_automation():
    print("🔒 Creating secure terminal session on Screener.in...")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # Authenticate and login to retrieve session cookies
    try:
        login_page = session.get(LOGIN_URL)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        payload = {
            'username': USERNAME,
            'password': PASSWORD,
            'csrfmiddlewaretoken': csrf_token
        }
        post_response = session.post(LOGIN_URL, data=payload, headers={'Referer': LOGIN_URL})
        
        if "logout" not in post_response.text.lower():
            print("❌ Authentication failed. Verify account secrets variables.")
            return
    except Exception as e:
        print(f"Connection failure to logging service: {str(e)}")
        return

    print("✅ Login active. Scanning data metrics...")
    
    # Process both queries sequentially
    for screen_name, text_query in QUERIES.items():
        print(f"Running profile scan for: {screen_name}")
        hits = parse_screener_query(session, text_query)
        
        if hits:
            message_payload = f"🔥 **{screen_name}** 🔥\n\n" + "\n".join(hits)
            bot.send_message(MY_CHAT_ID, message_payload, parse_mode='Markdown')
            print(f"🚀 Telegram package shipped for {screen_name}")
        else:
            bot.send_message(MY_CHAT_ID, f"📋 **{screen_name}**\n\nNo stock triggers met criteria today.")
            print(f"📁 Scan finished: 0 hits for {screen_name}")

if __name__ == "__main__":
    run_screener_automation()
  
