import os
import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from openai import AsyncClient
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from flask import Flask, request, abort

# 使用 Render 環境變數
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

async def fetch_website_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

def extract_risk_points(html_content, max_length=4096):
    soup = BeautifulSoup(html_content, 'lxml')
    risk_elements = []

    for script in soup.find_all('script'):
        element_str = str(script)
        if ('src' in script.attrs and 'http' in script.attrs['src']) or not script.attrs.get('src'):
            if len(element_str) + len(' '.join(risk_elements)) <= max_length:
                risk_elements.append(element_str)

    return ' '.join(risk_elements)[:max_length]

async def process_content_with_gpt35_turbo(html_content):
    client = AsyncClient(api_key=OPENAI_API_KEY)
    results = []
    try:
        risk_content = extract_risk_points(html_content)
        if risk_content:
            prompt = (
                "以下是從一個網頁提取的潛在高風險 `<script>` 標籤元素。"
                "這些元素包括來自外部連結的腳本以及內嵌的腳本。請基於腳本的來源、內容特徵"
                "和任何可識別的代碼模式，進行風險評估，判斷它們是否可能包含惡意代碼、"
                "釣魚連結或其他潛在危險元素。"
                "對於每個腳本，請提供是否安全的判斷依據，並對需要進一步驗證的腳本提出建議，並給個評分1-10的風險結論，用正體中文。"
                "風險分析：\n"
                f"{risk_content}\n"
            )
            completion = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            if completion.choices and completion.choices[0].message:
                results.append(completion.choices[0].message.content)
            else:
                results.append("(無回應)")
        return ' '.join(results)
    except Exception as e:
        print(f"發生錯誤：{e}")
        return None

# 定義一個執行異步任務的函數
def run_async_task(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))

# LINE Bot 訊息處理函數
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    # 立即回應用戶
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="收到您的請求，正在處理中..."))

    # 異步處理
    run_async_task(analyze_and_notify_user, user_message, event.source.user_id)

async def analyze_and_notify_user(url, user_id):
    html_content = await fetch_website_content(url)
    if html_content:
        processed_content = await process_content_with_gpt35_turbo(html_content)
        if processed_content:
            # 處理完成，向用戶發送結果
            line_bot_api.push_message(user_id, TextSendMessage(text=processed_content))
        else:
            line_bot_api.push_message(user_id, TextSendMessage(text="無法處理內容。"))
    else:
        line_bot_api.push_message(user_id, TextSendMessage(text="無法抓取網頁內容。"))


# Webhook 端點處理器（使用 Flask）
app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        abort(400)

    return 'OK'

if __name__ == "__main__":
    app.run()
