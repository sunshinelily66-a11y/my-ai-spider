import requests
import feedparser
from bs4 import BeautifulSoup
import os

# 1. 抓取逻辑 (保持不变)
def get_ai_news():
    news_list = []
    
    # --- 原有的技术源 (保持或微调) ---
    # arXiv (论文)
    arxiv_feed = feedparser.parse("https://rss.arxiv.org/rss/cs.AI")
    for entry in arxiv_feed.entries[:3]:
        news_list.append(f"【技术论文】来源: arXiv\n标题: {entry.title}\n摘要: {entry.summary}")

    # --- 新增：商业与投融资源 ---
    
    # TechCrunch AI (全球融资/并购)
    print("正在抓取 TechCrunch...")
    tc_feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
    for entry in tc_feed.entries[:3]:
        news_list.append(f"【商业动态】来源: TechCrunch\n标题: {entry.title}\n摘要: {entry.summary}")

    # VentureBeat AI (企业/投资)
    print("正在抓取 VentureBeat...")
    vb_feed = feedparser.parse("https://venturebeat.com/category/ai/feed/")
    for entry in vb_feed.entries[:3]:
        news_list.append(f"【行业大事件】来源: VentureBeat\n标题: {entry.title}\n摘要: {entry.summary}")

    # Crunchbase News (纯投融资)
    print("正在抓取 Crunchbase...")
    cb_feed = feedparser.parse("https://news.crunchbase.com/sections/ai-robotics/feed/")
    for entry in cb_feed.entries[:3]:
        news_list.append(f"【投融资】来源: Crunchbase\n标题: {entry.title}\n摘要: {entry.summary}")

    # 36Kr (国内行业大事件 - 建议通过 RSSHub 或直接抓取)
    # 提示：由于36kr对爬虫有限制，小白建议先加好上面三个，国内动态可以用你之前的“机器之心”
        
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
                    "请根据以下抓取到的信息，撰写一份【AI产业与技术深度简报】。要求如下：\n"
                    "1. **必须包含以下分类**：\n"
                    "   - 💰【投融资与并购】：重点列出哪家公司融了多少钱、谁投的、或者是谁收购了谁。\n"
                    "   - 👤【人事变动】：关注大厂高管、顶尖科学家的离职、入职或创业动态。\n"
                    "   - 🚀【重大技术突破】：整理前沿论文和新模型发布的要点。\n"
                    "   - 🏢【巨头/大厂动态】：OpenAI、Google、Meta 等公司的战略动作。\n"
                    "2. **每条内容要写深写透**：不要只写标题，要说明这件事为什么重要，对行业有什么影响。\n"
                    "3. **格式**：使用 Markdown 排版，重点公司和人名请加粗。\n\n"
                    f"内容如下：\n\n{raw_content}"
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
