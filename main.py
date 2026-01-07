import requests
import feedparser
from bs4 import BeautifulSoup
import os

# 1. 抓取逻辑 (保持不变)
def get_ai_news():
    news_list = []
    # arXiv
    arxiv_feed = feedparser.parse("https://rss.arxiv.org/rss/cs.AI")
    for entry in arxiv_feed.entries[:5]:
        news_list.append(f"标题: {entry.title}\n摘要: {entry.summary}")
    
    # Hacker News
    hn_res = requests.get("https://hn.algolia.com/api/v1/search?query=AI&tags=story").json()
    for item in hn_res['hits'][:5]:
        news_list.append(f"标题: {item['title']}\n链接: {item['url']}")
        
    return "\n---\n".join(news_list)

# 2. 新增：让大模型帮你总结
def summarize_with_ai(raw_content):
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return raw_content # 如果没配置Key，就返回原样内容

    print("正在请求大模型进行总结...")
    
    # 这里以 DeepSeek 为例，如果你用其他模型，修改 url 即可
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 这是你给大模型的指令 (Prompt)
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个AI领域的资深专家。请将我提供的一堆杂乱的新闻和论文信息进行整理。"},
            {"role": "user", "content": f"请帮我把以下内容总结成一份简洁的日报，要求：1.用中文；2.分门别类；3.每条只保留核心要点。内容如下：\n\n{raw_content}"}
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"总结出错: {e}")
        return raw_content

# 3. 推送逻辑 (保持不变)
def send_wechat(content):
    key = os.getenv("PUSH_KEY")
    if not key: return
    url = f"https://sctapi.ftqq.com/{key}.send"
    requests.post(url, data={"title": "🤖 智能 AI 每日简报", "desp": content})

if __name__ == "__main__":
    # 第一步：抓取
    raw_data = get_ai_news()
    # 第二步：总结 (新增)
    summary = summarize_with_ai(raw_data)
    # 第三步：推送
    send_wechat(summary)
