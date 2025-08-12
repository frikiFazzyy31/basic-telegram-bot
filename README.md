# Telegram Order and Inquiry Bot

Telegram bot for small businesses that automates order and inquiry management, storing data directly into Google Sheets. Built with Python and gspread, designed for easy customization and possible future AI integration.

## ⚠️ (Language) Warning!

You will notice that in the main code some names of variables and functions/handlers or custom messages that the bot sends are in Spanish and that is because that is my main language and also because I forgot to code it English (I realized later on). However, I'm planning on changing it in the future or make two different versions, will see.

## Features

- `/pedido` command for collecting orders. (pedido = order)
- `/consulta` command for general inquiries. (consulta = inquiry)
- Responses and data are saved to Google Sheets.
- Friendly UI with reply buttons for basic info like hours and location.

## Technologies Used

- Python 3
- python-telegram-bot
- gspread
- Google Sheets API
- dotenv (for environment variables and/or sensitive data)

## Setup

0. Create the bot (follow along with this vid: https://www.youtube.com/watch?v=RIrIXLAj8bE)
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Create a .env file in the root folder:
   (you might need to type 'pip install python-dotenv' in your terminal for it to work (if you haven't done it before))
   Inside that file you might want to include lines like these:
   TELEGRAM_TOKEN="your-bot-token"
   GOOGLE_SHEETS_CREDENTIALS_PATH="yourCredentialsFile.json"
   GOOGLE_SHEETS_FILE_NAME="Sheet Name", etc.
4. Make sure your Google credentials file is downloaded from Google Cloud (here's a quick tutorial for this part: https://www.youtube.com/watch?v=brCkpzAD0gc PS: when he selects 'API Key' you should select 'Service account' instead, at least that's how I did it for this project and it works PS2: sorry, I don't know much about this language/environment yet for me to be able to explain it accurately, however, if you end up needing any help don't hesitate in reaching out!) and saved with the name credentials.json (or the name you would like it to have, just make sure it matches where it has to match)
5. Run the bot:
   python theFileWhereYouHaveTheCodeOfTheBot.py

## Security

- Sensitive data is stored in a .env file and should not be committed to version control.
- .gitignore excludes .env and credentials.json.
