import requests
import feedparser
from bs4 import BeautifulSoup
import os

# 1. 抓取逻辑
def get_ai_news():
    news_list = []
    
    # --- arXiv (论文) ---
    print("正在抓取 arXiv...")
    arxiv_feed = feedparser.parse("https://rss.arxiv.org/rss/cs.AI")
    for entry in arxiv_feed.entries[:3]:
        news_list.append(f"【论文】{entry.title}\n链接：{entry.link}")

    # --- Hacker News (聚合) ---
    print("正在抓取 Hacker News...")
    hn_res = requests.get("https://hn.algolia.com/api/v1/search?query=AI&tags=story").json()
    for item in hn_res['hits'][:3]:
        news_list.append(f"【热议】{item['title']}\n链接：{item['url']}")

    # --- GitHub Trending (代码) ---
    print("正在抓取 GitHub...")
    gh_res = requests.get("https://github.com/trending/python?since=daily")
    soup = BeautifulSoup(gh_res.text, 'html.parser')
    for item in soup.select('article.Box-row h2 a')[:3]:
        news_list.append(f"【项目】{item.get_text(strip=True)}\n链接：https://github.com{item.get('href')}")

    return "\n\n".join(news_list)

# 2. 推送逻辑 (使用 Server酱)
def send_wechat(content):
    key = os.getenv("PUSH_KEY") # 稍后我们会去设置这个“保险箱”
    if not key:
        print("未检测到 PUSH_KEY，取消推送")
        return
    url = f"https://sctapi.ftqq.com/{key}.send"
    requests.post(url, data={"title": "今日 AI 资讯汇总", "desp": content})
    print("推送成功！")

if __name__ == "__main__":
    content = get_ai_news()
    send_wechat(content)
