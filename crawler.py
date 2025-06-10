import requests
from bs4 import BeautifulSoup
import json

url = "http://news.163.com"

response = requests.get(url, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# 更精确的选择器（请根据实际网页结构替换）
news_links = soup.select("a")  # 示例，请替换成 .news-title 等

results = []
keywords = ["switch", "任天堂", "Nintendo", "游戏主机"]

print(f"正在抓取: {url}")
print(f"共解析到 {len(news_links)} 个链接")

print("前5个链接文本：")
for link in news_links[:5]:
    text = link.get_text().strip()
    print(text)

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

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

if results:
    print(f"✅ 成功找到 {len(results)} 条 Nintendo Switch 新闻")
else:
    print("❌ 没有找到任何 Nintendo Switch 新闻")
