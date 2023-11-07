# Websites.py

import webbrowser
import asyncio

# A dictionary mapping keywords to URLs
COMMAND_URLS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    # Add more mappings here as needed
}

async def open_website(command):
    for keyword, url in COMMAND_URLS.items():
        if keyword in command:
            webbrowser.open(url)
            break  # If a keyword matches, open the site and stop checking
    else:
        print("No website found in command.")
