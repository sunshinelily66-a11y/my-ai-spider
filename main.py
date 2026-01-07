import requests
import feedparser
from bs4 import BeautifulSoup
import os

# 1. 抓取逻辑 (保持不变)
def get_ai_news():
    news_list = []
    
    # arXiv (论文通常有很长的摘要，非常适合深度分析)
    arxiv_feed = feedparser.parse("https://rss.arxiv.org/rss/cs.AI")
    for entry in arxiv_feed.entries[:5]:
        # 把摘要也传给大模型
        news_list.append(f"来源: arXiv\n标题: {entry.title}\n摘要: {entry.summary}")
    
    # Hacker News (HN通常只有标题，效果会略差)
    hn_res = requests.get("https://hn.algolia.com/api/v1/search?query=AI&tags=story").json()
    for item in hn_res['hits'][:5]:
        news_list.append(f"来源: Hacker News\n标题: {item['title']}\n链接: {item['url']}")
        
    return "\n\n===\n\n".join(news_list)
    
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
    
   # 这是你给大模型的“深度指令”
    payload = {
        "model": "deepseek-chat", # 或者你使用的其他模型
        "messages": [
            {
                "role": "system", 
                "content": "你是一个严谨的AI科技记者。你的任务是将杂乱的信息转化为高质量的深度简报。"
            },
            {
                "role": "user", 
                "content": (
                    "请根据以下抓取到的信息，撰写一份深度AI日报。要求如下：\n"
                    "1. **禁止简短的一句话总结**，每条内容必须包含：\n"
                    "   - 【主体】涉及的公司、团队或关键人物是谁；\n"
                    "   - 【核心动态】具体做了什么（发布了什么、突破了什么）；\n"
                    "   - 【核心观点/技术细节】他们提出了什么新观点或技术亮点；\n"
                    "   - 【原因与影响】为什么要这么做，对行业有什么潜在影响。\n"
                    "2. **格式要求**：使用清晰的 Markdown 格式，分条目列出。\n"
                    "3. **语言**：必须使用专业、易懂的中文。\n\n"
                    f"待处理的内容如下：\n\n{raw_content}"
                )
            }
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
