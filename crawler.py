import requests
from bs4 import BeautifulSoup
import json
import os

url = "http://news.163.com"

response = requests.get(url, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# 更精确的选择器（请根据实际页面结构调整）
links = soup.find_all("a")

results = []
keywords = ["switch", "任天堂", "Nintendo", "游戏主机"]

for link in links:
    title = link.get_text().strip()
    href = link.get('href')
    if title and href and any(kw.lower() in title.lower() for kw in keywords):
        results.append({
            'title': title,
            'link': href
        })

# 写入 JSON
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# 写入 Markdown
md_file = "switch_news.md"
with open(md_file, "w", encoding="utf-8") as f:
    f.write("# Nintendo Switch 新闻日报\n")
    f.write(f"更新时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    if results:
        f.write(f"共找到 {len(results)} 条新闻：\n\n")
        for item in results:
            f.write(f"- [{item['title']}]({item['link']})\n")
    else:
        f.write("❌ 当前没有找到任何与 Nintendo Switch 相关的新闻。\n")

if results:
    print(f"✅ 成功找到 {len(results)} 条 Nintendo Switch 新闻")
else:
    print("❌ 没有找到任何 Nintendo Switch 新闻")
