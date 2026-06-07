import os
import requests
from bs4 import BeautifulSoup
import telebot

# --- ENVIRONMENT VARIABLES SETUP ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MY_CHAT_ID = os.getenv('MY_CHAT_ID')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Live Screener Links Provided By You
URLS = {
    "🎯 BIG_MONEY HITS": "https://www.screener.in/screens/3708803/big-money-inflow/",
    "💎 SMALL STOCKS HITS": "https://www.screener.in/screens/3708883/small-stocks/"
}

def parse_saved_screen(url):
    """Parses your live screener screens cleanly without needing an active login session."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Screener page rejected request with status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'data-table'})
        if not table:
            return []

        rows = table.find_all('tr')[1:]  # Skips table structural header row
        stocks = []
        for row in rows[:15]:  # Limit output to top 15 matches to keep Telegram clean
            cols = row.find_all('td')
            if len(cols) > 2:
                name = cols[1].text.strip().replace('\n', '').split('  ')[0]
                price = cols[2].text.strip()
                stocks.append(f"🔹 **{name}** - CMP: ₹{price}")
        return stocks
    except Exception as e:
        print(f"Scraping processing error: {str(e)}")
        return []

def main():
    print("🎬 Initializing public URL stream readers...")
    
    for screen_name, link_url in URLS.items():
        print(f"Fetching rows for: {screen_name}")
        hits = parse_saved_screen(link_url)
        
        if hits:
            message_payload = f"🔥 **{screen_name}** 🔥\n\n" + "\n".join(hits)
            bot.send_message(MY_CHAT_ID, message_payload, parse_mode='Markdown')
            print(f"🚀 Telegram update shipped for {screen_name}")
        else:
            bot.send_message(MY_CHAT_ID, f"📋 **{screen_name}**\n\nNo stock triggers met criteria today.")
            print(f"📁 Completed: 0 matches found for {screen_name}")

if __name__ == "__main__":
    main()
