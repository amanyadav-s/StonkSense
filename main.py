from bs4 import BeautifulSoup
import telebot
from telebot import types
import requests
import csv
from dotenv import load_dotenv
import os

# Initializing bot
load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
  # Replace with your actual token
bot = telebot.TeleBot(ACCESS_TOKEN)


company_name = ""
url = ""

# Web scraping function to get the stock price
def get_current_stock_data(ticker):
    global url
    url = f"https://www.screener.in/company/{ticker[:-1]}/consolidated/"
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")
    spans = soup.find_all('span', class_='name')
    top_ratios = {}
    for span in spans:
        top_ratios[span.text.strip()] = span.find_next_sibling('span').text.strip()
        
        
    """

    #try:
        top_ul = soup.find('ul', id='top-ratios')
        print(top_ul)
        li = top_ul.find_all('li')
        print(li)
        
        current_stock_price = float(spans[1].text.replace(',', ''))  # Handle comma in numbers
        return current_stock_price
    except Exception as e:
        return f"Could not fetch stock data for {ticker}. Error: {e}"
    """
    for q,a in top_ratios.items():
        print(q,a)
        print(top_ratios)
    return top_ratios

# Bot handling

# Setting up the start message
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    search_button = types.InlineKeyboardButton(text="Search", switch_inline_query_current_chat="")
    help_button = types.InlineKeyboardButton(text="Help", callback_data="help")
    about_button = types.InlineKeyboardButton(text="About", callback_data="about")
    markup.add(search_button, help_button, about_button)

    bot.send_message(message.chat.id, """Welcome to the StonkSense Bot!

I can help you check the latest stock prices. Just type the name of the stock (like Vodafone Idea) and I'll give you the current details of the stock.

Let’s get started! 📈""", reply_markup=markup)

# Handle inline queries
@bot.inline_handler(lambda query: len(query.query) > 0)
def query_stock_recommendation(inline_query):
    global company_name
    stock_input = inline_query.query.strip().lower()
    results = []

    with open('stocks.csv', 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip header if exists

        for row in reader:
            ticker = row[0]
            company = row[1]
            
            if stock_input in ticker.lower() or stock_input in company.lower():
                # Create an inline result
                result = types.InlineQueryResultArticle(
                    id=ticker,
                    title=f"{ticker} - {company}",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"You selected {ticker}. Fetching data from site..."
                    ),
                    description=f"{company} - Click to select"
                )
                results.append(result)

    # Send the list of filtered results
    if results:
        bot.answer_inline_query(inline_query.id, results)

# handle user's inline selection and send the stock price
@bot.message_handler(func=lambda message: message.text.startswith("You selected"))
def handle_inline_selection(message):
    global company_name
    ticker = message.text.split(" ")[2]  # Extract the ticker from the message
    with open('stocks.csv', 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip header if exists
        for row in reader:
            
            if row[0].strip().lower() == ticker.strip().lower()[:-1]:
                company_name = row[1]
                break
    
    stock = get_current_stock_data(ticker)
    market_cap = stock['Market Cap'].replace('\n', '').replace(' ', '')
    current_price = stock['Current Price'].replace('\n', '').replace(' ', '')
    stock_pe = stock['Stock P/E'].replace('\n', '').replace(' ', '')
    if stock_pe == '':
        stock_pe = '-'
    high_low = stock['High / Low'].replace('\n', '').replace(' ', '')
    book_value = stock['Book Value'].replace('\n', '').replace(' ', '')
    dividend_yield = stock['Dividend Yield'].replace('\n', '').replace(' ', '')
    roe = stock['ROE'].replace('\n', '').replace(' ', '')
    roce = stock['ROCE'].replace('\n', '').replace(' ', '')
    face_value = stock['Face Value'].replace('\n', '').replace(' ', '')

    bot.send_message(message.chat.id, f"""🏢 Company Name: {company_name}

💰 Market Cap: {market_cap}  
💵 Current Price: {current_price}  
📊 Stock P/E: {stock_pe}  
🔼 High/Low: {high_low}  
📚 Book Value: {book_value}  
💸 Dividend Yield: {dividend_yield}  
📈 ROE: {roe}  
🔄 ROCE: {roce}  
⚖️ Face Value: {face_value}
For More Visit: {url}
""")

# Polling to keep the bot active
bot.polling()