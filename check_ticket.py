#!/usr/bin/env python3

import os                  # 用來讀取環境變數，例如 token
import re                  # 正規表達式，可能用來清洗 HTML
import requests            # 發 HTTP 請求，包含爬網頁與推 LINE 訊息
from bs4 import BeautifulSoup  # 爬蟲解析 HTML
from openai import OpenAI      # 呼叫 OpenAI API

def notify(message):
    access_token = os.environ["LINE_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    resp = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)
    if resp.status_code != 200:
        print(f"❌ LINE push failed: {resp.status_code} - {resp.text}")
    else:
        print("✅ Message pushed to LINE")

def ask_openai(prompt, model="o4-mini"):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    try:
        response = client.chat.completions.create(model=model,
        messages=[
            {"role": "system", "content": """
                你是一個判定售票資訊的中文助手。請用簡潔的中文回答。
                """},
            {"role": "user", "content": f"""
    這是一個售票網站的網站文字。我目標是要買日本2026 F1賽道的票。
    請問有什麼票務資訊？
    請簡潔用中文回答，只需要跟購票相關資訊就好。
    尤其是「是否/何時開賣」
    或是「網頁已不再明確提供售票資訊請盡早檢查網址」
    {prompt}
                """
        }
        ],
        #temperature=0.3, #no temperature supported for this model
        max_completion_tokens=1000)

        content = response.choices[0].message.content.strip()
        usage = response.usage  # includes prompt_tokens / completion_tokens

        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        # 估價邏輯（你可以之後改）
        input_cost = input_tokens * 1.10 / 1e6
        output_cost = output_tokens * 4.40 / 1e6
        total_cost = input_cost + output_cost

        # 結果句尾加上 token 數與費用
        result = f"""{content}
🔢 token 使用：輸入 {input_tokens}、輸出 {output_tokens}
💰 預估費用：${total_cost:.5f} USD"""

        return result

    except Exception as e:
        print(f"❌ OpenAI API 錯誤: {e}")
        return None

def check_ticket():
    url = "https://motorsporttickets.com/en/f1/japan"  # 你要監控的網址
    html = requests.get(url).text
    html = extract_visible_text(html)
    soup = BeautifulSoup(html, "html.parser")

    response = ask_openai(soup)
    print(response)
    notify(response)

def extract_visible_text(html):

    soup = BeautifulSoup(html, "html.parser")

    # Remove script, style, nav, footer, etc
    for tag in soup(["script", "style", "footer", "nav", "noscript"]):
        tag.decompose()

    # Get text chunks
    text = soup.get_text(separator="\n")

    # 去除空行 & 多餘空白
    lines = [line.strip() for line in text.splitlines()]
    visible_text = "\n".join(line for line in lines if line)

    return visible_text

if __name__ == "__main__":
    check_ticket()

