import os
import requests
from bs4 import BeautifulSoup
import telebot
import matplotlib.pyplot as plt

# --- ENVIRONMENT VARIABLES SETUP ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MY_CHAT_ID = os.getenv('MY_CHAT_ID')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Your Live Screener Links
URLS = {
    "🎯 BIG_MONEY HITS": "https://www.screener.in/screens/3708803/big-money-inflow/",
    "💎 SMALL STOCKS HITS": "https://www.screener.in/screens/3708883/small-stocks/"
}

def parse_saved_screen(url):
    """Parses your live screener screens cleanly."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'data-table'})
        if not table:
            return []

        rows = table.find_all('tr')[1:]  # Skips header row
        stocks = []
        for row in rows[:8]:  # Limit to top 8 to keep the donut chart perfectly clean
            cols = row.find_all('td')
            if len(cols) > 2:
                name = cols[1].text.strip().replace('\n', '').split('  ')[0]
                price = float(cols[2].text.strip().replace(',', ''))
                stocks.append({'name': name, 'price': price})
        return stocks
    except Exception as e:
        print(f"Scraping error: {str(e)}")
        return []

def generate_donut_chart(stocks, title, filename):
    """Generates a beautiful donut chart matching premium market layouts."""
    names = [stock['name'] for stock in stocks]
    prices = [stock['price'] for stock in stocks]
    
    # Elegant color palette for market tracking
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
    
    plt.figure(figsize=(6, 6), facecolor='#111827') # Dark theme background matching your setup
    ax = plt.subplot()
    
    # Plot pie chart slices
    wedges, texts, autotexts = ax.pie(
        prices, 
        labels=names, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors[:len(stocks)],
        textprops=dict(color="w", weight="bold"),
        pctdistance=0.75
    )
    
    # Turn it into a donut chart by drawing a center circle
    centre_circle = plt.Circle((0,0), 0.55, fc='#111827')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    # Fine-tune layout text presentation
    plt.setp(autotexts, size=9, weight="bold")
    plt.setp(texts, size=10)
    
    ax.set_title(title, color='w', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    
    # Save chart locally as an image file
    plt.savefig(filename, facecolor=plt.facecolor, edgecolor='none', dpi=150)
    plt.close()

def main():
    print("🎬 Initializing public URL stream readers & visual chart engine...")
    
    # Make sure matplotlib dependencies are installed dynamically if missing in yml
    os.system("pip install matplotlib")
    
    for screen_name, link_url in URLS.items():
        print(f"Fetching rows for: {screen_name}")
        stocks = parse_saved_screen(link_url)
        
        if stocks:
            filename = f"{screen_name.lower().replace(' ', '_')}.png"
            
            # Generate the visualization
            generate_donut_chart(stocks, screen_name, filename)
            
            # Construct a clean text breakdown caption to accompany the image
            caption = f"🔥 <b>{screen_name} VISUALIZATION</b> 🔥\n\n"
            for s in stocks:
                caption += f"🔹 <b>{s['name']}</b> - CMP: ₹{s['price']}\n"
                
            # Ship image directly to your Telegram channel
            with open(filename, 'rb') as photo:
                bot.send_photo(MY_CHAT_ID, photo, caption=caption, parse_mode='HTML')
            print(f"🚀 Visual donut chart shipped for {screen_name}")
            
            # Clean up local image file
            if os.path.exists(filename):
                os.remove(filename)
        else:
            bot.send_message(MY_CHAT_ID, f"📋 <b>{screen_name}</b>\n\nNo stock triggers met criteria today.", parse_mode='HTML')
            print(f"📁 Completed: 0 matches found for {screen_name}")

if __name__ == "__main__":
    main()
    
