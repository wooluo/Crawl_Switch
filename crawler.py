import requests
from bs4 import BeautifulSoup
import json

url = "http://news.163.com"

response = requests.get(url, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# 更精确的选择器（根据实际页面结构调整）
news_links = soup.select("a")  # 示例，请替换为实际选择器如 ".news-title"

results = []
keywords = ["switch", "任天堂", "Nintendo", "游戏主机"]

print(f"正在抓取: {url}")
print(f"共解析到 {len(news_links)} 个链接")

for link in news_links:
    title = link.get_text().strip()
    href = link.get("href")
    
    if not title or not href:
        continue

    if any(kw.lower() in title.lower() for kw in keywords):
        results.append({
            "title": title,
            "link": href
        })

output_file = "results.json"

if results:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ 成功找到 {len(results)} 条 Nintendo Switch 新闻")
else:
    print("❌ 没有找到任何 Nintendo Switch 新闻")
