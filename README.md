# SecurityCheckBot

## Introduction
SecurityCheckBot is a LINE messaging bot designed to analyze web pages for potential security risks. It uses OpenAI's GPT-3.5 Turbo model for risk assessment of `<script>` tags, identifying any malicious code, phishing links, or other potential dangers.

## Features
- **Webpage Analysis**: Fetches the content of a webpage and extracts potential risk elements.
- **Risk Assessment**: Utilizes OpenAI's GPT-3.5 Turbo model to evaluate the safety of script elements based on their source and content characteristics.
- **Asynchronous Processing**: Handles operations asynchronously to improve performance and response time.
- **LINE Messaging Interface**: Integrates with LINE messaging for user interaction and notification.

## Requirements
- Python 3.x
- aiohttp
- BeautifulSoup
- OpenAI Python Client
- LINE Messaging API SDK
- Flask

## Environment Variables
The bot requires the following environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key.
- `LINE_CHANNEL_SECRET`: Your LINE channel secret.
- `LINE_CHANNEL_ACCESS_TOKEN`: Your LINE channel access token.

## Setup
1. Install required Python packages.
2. Set up the necessary environment variables.
3. Deploy the application to a hosting platform or run it locally.

## Usage
Send a URL to the bot through a LINE message. The bot will respond with the analysis of the webpage content, highlighting potential risks and providing a risk score.

## Webhook Endpoint
The Flask application listens for POST requests at the `/callback` endpoint for LINE webhook events.

## Asynchronous Task Execution
The bot uses an event loop to run asynchronous tasks, such as fetching webpage content and processing it with OpenAI's model.

## Error Handling
Includes error handling for exceptions in API calls and processing.

## Note
This bot is for educational and development purposes. Always ensure compliance with OpenAI's usage policies and LINE's guidelines.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


