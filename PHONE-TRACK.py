import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from pyfiglet import Figlet
import shutil
import json
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

LightGreen = "\033[92m"
DarkGray = "\033[90m"
White = "\033[97m"
Red = "\033[91m"

def print_banner():
    terminal_width = shutil.get_terminal_size().columns
    fig = Figlet(font="smslant")
    banner = fig.renderText('PHONE-TRACK')
    banner_lines = banner.split('\n')
    centered_banner = '\n'.join(line.center(terminal_width) for line in banner_lines)
    print(f"{LightGreen}{centered_banner}{White}")
    
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
        "/start - START THE BOT\n"
        "/help - DISPLAYS THE HELP MENU\n"
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
            parsed_number = phonenumbers.parse(user_phone)
        except phonenumbers.phonenumberutil.NumberParseException:
            update.message.reply_text("Invalid phone number format. Please enter the correct format.")
            return

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

        file_path = 'phone_info.json'
        with open(file_path, 'w') as json_file:
            json.dump(phone_info_dict, json_file, indent=4)

        with open(file_path, 'rb') as json_file:
            update.message.reply_document(document=json_file, filename='sparux-666-info.json')

        os.remove(file_path)
    else:
        update.message.reply_text("Please provide a phone number. Usage: /phone <phone_number>")

def main():
    print_banner()
    
    token = input("ENTER BOT TOKEN: ")

    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("phone", phone_info))
    
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
