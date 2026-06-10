"""
每日财经新闻采集器
从 RSS、NewsAPI 等渠道采集全球财经新闻头条
"""

import json
import os
import time
from datetime import datetime
from typing import Optional

import feedparser
import requests

# ============ 配置区 ============

# 中国财经媒体 RSS 源
CHINA_FINANCE_RSS = [
    ("第一财经", "https://www.yicai.com/rss"),
    ("经济观察报", "https://www.eeo.com.cn/rss/headline.xml"),
    ("21世纪经济报道", "http://www.21jingji.com/rss/feed.xml"),
    ("新华社财经", "https://www.xinhuanet.com/finance/rss/finance.xml"),
    ("人民网财经", "http://finance.people.com.cn/rss/finance.xml"),
]

# 美国/欧洲财经媒体 RSS 源
GLOBAL_FINANCE_RSS = [
    ("CNBC", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"),
    ("Bloomberg", "https://feeds.bloomberg.com/markets/news.rss"),
    ("Reuters", "https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best&best-sectors=business-finance"),
    ("FT", "https://www.ft.com/business-education?format=rss"),
    ("WSJ", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
]

# 科技媒体 RSS 源
TECH_RSS = [
    ("36氪", "https://36kr.com/feed"),
    ("虎嗅", "https://www.huxiu.com/rss/0.xml"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
]

# 自媒体的 RSS 源
SOCIAL_MEDIA_RSS = [
    ("Bloomberg Markets (YouTube)", "https://www.youtube.com/feeds/videos.xml?channel_id=UCC0RGR_tRHflRQR6KCaD3qA"),
    ("CNBC (YouTube)", "https://www.youtube.com/feeds/videos.xml?channel_id=UCr5nYCgGaRkyIhfDBV7WqZA"),
]


def fetch_rss(url: str, timeout: int = 15) -> list[dict]:
    """从 RSS 源获取新闻列表"""
    try:
        feed = feedparser.parse(url)
        entries = []
        for entry in feed.entries[:20]:  # 每个源取前20条
            entries.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", entry.get("description", ""))[:300],
                "link": entry.get("link", ""),
                "published": entry.get("published", datetime.now().isoformat()),
            })
        return entries
    except Exception as e:
        print(f"  [WARN] RSS 抓取失败: {url} - {e}")
        return []


def fetch_newsapi(api_key: str) -> list[dict]:
    """通过 NewsAPI 获取财经新闻"""
    entries = []
    queries = [
        "China economy", "Federal Reserve", "technology",
        "stock market", "AI artificial intelligence",
    ]
    for query in queries:
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "language": "en",
                "pageSize": 5,
                "sortBy": "publishedAt",
                "apiKey": api_key,
            }
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for article in data.get("articles", []):
                    entries.append({
                        "title": article.get("title", ""),
                        "summary": article.get("description", "") or ""[:300],
                        "link": article.get("url", ""),
                        "published": article.get("publishedAt", ""),
                        "source": article.get("source", {}).get("name", "NewsAPI"),
                    })
            time.sleep(0.5)  # 避免触发限流
        except Exception as e:
            print(f"  [WARN] NewsAPI 查询失败 ({query}): {e}")
    return entries


def collect_all(newsapi_key: Optional[str] = None) -> dict:
    """采集所有来源的新闻"""
    result = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "updated_at": datetime.now().isoformat(),
        "sections": {},
    }

    print("[1/6] 采集中国财经媒体...")
    china_news = []
    for name, url in CHINA_FINANCE_RSS:
        items = fetch_rss(url)
        for item in items:
            item["source"] = name
        china_news.extend(items)
        print(f"  ✓ {name}: {len(items)} 条")
        time.sleep(0.3)
    result["sections"]["china_finance"] = china_news

    print("[2/6] 采集全球财经媒体...")
    global_news = []
    for name, url in GLOBAL_FINANCE_RSS:
        items = fetch_rss(url)
        for item in items:
            item["source"] = name
        global_news.extend(items)
        print(f"  ✓ {name}: {len(items)} 条")
        time.sleep(0.3)
    if newsapi_key:
        api_news = fetch_newsapi(newsapi_key)
        for item in api_news:
            if not any(n["link"] == item["link"] for n in global_news):
                global_news.append(item)
        print(f"  ✓ NewsAPI: {len(api_news)} 条补充")
    result["sections"]["global_finance"] = global_news

    print("[3/6] 采集科技媒体...")
    tech_news = []
    for name, url in TECH_RSS:
        items = fetch_rss(url)
        for item in items:
            item["source"] = name
        tech_news.extend(items)
        print(f"  ✓ {name}: {len(items)} 条")
        time.sleep(0.3)
    result["sections"]["tech"] = tech_news

    print("[4/6] 采集自媒体观点...")
    social_news = []
    for name, url in SOCIAL_MEDIA_RSS:
        items = fetch_rss(url)
        for item in items:
            item["source"] = name
        social_news.extend(items)
        print(f"  ✓ {name}: {len(items)} 条")
        time.sleep(0.3)
    result["sections"]["social_media"] = social_news

    # 占位
    result["sections"]["research"] = []
    result["sections"]["sources"] = []

    # 统计
    total = sum(len(v) for v in result["sections"].values() if isinstance(v, list))
    print(f"\n✅ 采集完成！共 {total} 条新闻")

    return result


if __name__ == "__main__":
    api_key = os.environ.get("NEWSAPI_KEY")
    data = collect_all(api_key)
    os.makedirs("data", exist_ok=True)
    path = f"data/news_{data['date']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已保存到 {path}")
