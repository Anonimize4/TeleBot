import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)logger = logging.getLogger(__name__)# Function to scrape social media data based on contact information
def scrape_social_media(platform, contact_info):    urls = {
        'instagram': f'https://www.instagram.com/{contact_info}/',
        'tiktok': f'https://www.tiktok.com/@{contact_info}',  # Adjust if necessary
        # Add more platforms here}    if platform not in urls:
        return"Platform not supported."    url = urls[platform]    
    try:
        response = requests.get(url)        response.raise_for_status()        soup = BeautifulSoup(response.text, 'html.parser')        # Example scraping logic; adjust based on the actual structure of the page
        if platform == 'instagram':
            user_data = soup.find('div', class_='user-data')  # Replace with actual class
        elif platform == 'tiktok':
            user_data = soup.find('div', class_='tiktok-data')  # Replace with actual class

        return user_data.text.strip() if user_data else"No data found."    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error accessing {url}: {e}")        return f"An error occurred: {e}"# Command handler for the start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Please choose a platform to scrape data from:",                              reply_markup=platform_menu())# Function to create the inline keyboard for platform selection
def platform_menu():    keyboard = [
        [InlineKeyboardButton("Instagram", callback_data='instagram')],        [InlineKeyboardButton("TikTok", callback_data='tiktok')],        # Add more buttons for other platforms] return InlineKeyboardMarkup(keyboard)# Callback function to handle button presses
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()    query.edit_message_text(text="Please enter your phone number or email:")    context.user_data['platform'] = query.data  # Store the selected platform
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)logger = logging.getLogger(__name__)# Function to scrape social media data based on contact information
def scrape_social_media(platform, contact_info):    urls = {
        'instagram': f'https://www.instagram.com/{contact_info}/',
        'tiktok': f'https://www.tiktok.com/@{contact_info}',  # Adjust if necessary
        # Add more platforms here}    if platform not in urls:
        return"Platform not supported."    url = urls[platform]    
    try:
        response = requests.get(url)        response.raise_for_status()        soup = BeautifulSoup(response.text, 'html.parser')        # Example scraping logic; adjust based on the actual structure of the page
        if platform == 'instagram':
            user_data = soup.find('div', class_='user-data')  # Replace with actual class
        elif platform == 'tiktok':
            user_data = soup.find('div', class_='tiktok-data')  # Replace with actual class

        return user_data.text.strip() if user_data else"No data found."    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error accessing {url}: {e}")        return f"An error occurred: {e}"# Command handler for the start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Please choose a platform to scrape data from:",                              reply_markup=platform_menu())# Function to create the inline keyboard for platform selection
def platform_menu():    keyboard = [
        [InlineKeyboardButton("Instagram", callback_data='instagram')],        [InlineKeyboardButton("TikTok", callback_data='tiktok')],        # Add more buttons for other platforms] return InlineKeyboardMarkup(keyboard)# Callback function to handle button presses
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()    query.edit_message_text(text="Please enter your phone number or email:")    context.user_data['platform'] = query.data  # Store the selected platform

# Message handler to capture the contact info
def handle_contact_info(update: Update, context: CallbackContext) -> None:
    contact_info = update.message.text
    platform = context.user_data.get('platform')    if platform:
        data = scrape_social_media(platform, contact_info)        update.message.reply_text(data)    else:
        update.message.reply_text("Please select a platform first using /start.")# Help command to list available commands
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Available commands:\n/start - Welcome message\n/help - List of commands')# Logging errors
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update"{update}" caused error"{context.error}"')# Main function to run the bot
def main():    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")    dispatcher = updater.
dispatcher.add_handler(CommandHandler("start", start))    dispatcher.add_handler(CallbackQueryHandler(button))    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_contact_info))    dispatcher.add_handler(CommandHandler("help", help_command))    dispatcher.add_error_handler(error)    updater.start_polling()    updater.idle()if __name__ == '__main__':    main()```### Complete Code Explanation
