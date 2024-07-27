import logging
import shutil
from queue import Queue
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import json
import os
from pyfiglet import Figlet

# Logging settings
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define color codes
LightGreen = "\033[92m"
White = "\033[97m"
Red = "\033[91m"

def print_banner():
    # Get terminal width
    terminal_width = shutil.get_terminal_size().columns
    fig = Figlet(font="smslant")
    banner = fig.renderText('PHONE-TRACK')
    # Center the banner according to terminal width
    banner_lines = banner.split('\n')
    centered_banner = '\n'.join(line.center(terminal_width) for line in banner_lines)
    print(f"{LightGreen}{centered_banner}{White}")
    
    # Print GitHub link and tool description centered
    github_line = "GitHub: SPARUX-666".center(terminal_width)
    tool_description_line = "PHONE NUMBER OSINT TOOL".center(terminal_width)
    print(f"{Red}{github_line}{White}")
    print(f"{Red}{tool_description_line}{White}")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Phone-Track Bot! 📱\n\n"
        "This bot provides detailed information about phone numbers using OSINT (Open Source Intelligence) techniques. "
        "You can use this bot to find the carrier, location, timezone, and validity of any phone number around the world.\n\n"
        "Available commands:\n"
        "/start - Display this welcome message\n"
        "/help - Show the help message with all commands\n"
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Phone-Track Bot Help\n\n"
        "This bot provides detailed information about phone numbers. Here are the available commands:\n\n"
        "/start - Display the welcome message\n\n"
        "/help - Show this help message with all commands\n\n"
        "/phone <number> - Get information about a specific phone number\n"
        "Example: /phone +901234567890\n\n"
        "The /phone command provides information such as location, region code, time zone, operator, and validity of the phone number."
    )

def phone_info(update: Update, context: CallbackContext):
    if context.args:
        user_phone = ' '.join(context.args)
        
        try:
            # Parse the entered phone number
            parsed_number = phonenumbers.parse(user_phone)
        except phonenumbers.phonenumberutil.NumberParseException:
            update.message.reply_text("Invalid phone number format. Please enter the correct format.")
            return

        # Retrieve information about the phone number
        region_code = phonenumbers.region_code_for_number(parsed_number)
        operator = carrier.name_for_number(parsed_number, "en")
        location = geocoder.description_for_number(parsed_number, "en")
        is_valid_number = phonenumbers.is_valid_number(parsed_number)
        is_possible_number = phonenumbers.is_possible_number(parsed_number)
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        formatted_number_for_mobile = phonenumbers.format_number_for_mobile_dialing(parsed_number, None, with_formatting=True)
        number_type = phonenumbers.number_type(parsed_number)
        timezones = timezone.time_zones_for_number(parsed_number)
        timezone_str = ', '.join(timezones)

        # Create information dictionary
        phone_info_dict = {
            "Location": location,
            "Region Code": region_code,
            "Time Zone": timezone_str,
            "Operator": operator,
            "Valid Number": is_valid_number,
            "Possible Number": is_possible_number,
            "International Format": formatted_number,
            "Mobile Format": formatted_number_for_mobile,
            "Original Number": parsed_number.national_number,
            "E.164 Format": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
            "Country Code": parsed_number.country_code,
            "National Number": parsed_number.national_number,
            "Type": {
                phonenumbers.PhoneNumberType.MOBILE: "Mobile number",
                phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed line number"
            }.get(number_type, "Other number type")
        }

        # Save to JSON file
        file_path = 'phone_info.json'
        with open(file_path, 'w') as json_file:
            json.dump(phone_info_dict, json_file, indent=4)

        # Send the JSON file to the user
        with open(file_path, 'rb') as json_file:
            update.message.reply_document(document=json_file, filename='phone_info.json')

        # Optionally, you can delete the file after sending
        os.remove(file_path)
    else:
        update.message.reply_text("Please provide a phone number. Usage: /phone <phone_number>")

def main():
    # Print the banner
    print_banner()

    # Bot token'ı kullanıcıdan alınacak
    token = input("Please enter your bot token: ")

    # Initialize the Bot and Updater
    bot = Bot(token=token)
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('phone', phone_info))

    # Start the bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
