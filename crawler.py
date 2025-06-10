import requests
from bs4 import BeautifulSoup
import json
import os

url = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&ie=utf-8&word=switch"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# 获取Nintendo官网新闻列表
news_items = soup.find_all('div', class_='news-item')

results = []
keywords = ["switch", "任天堂", "Nintendo", "游戏主机"]

for item in news_items:
    title = item.find('h2').get_text().strip() if item.find('h2') else ''
    href = item.find('a')['href'] if item.find('a') else ''
    if title and href:
        # 确保链接是完整的URL
        if not href.startswith('http'):
            href = f"https://baijiahao.baidu.com/s?id=1834513450802434398&wfr=spider&for=pc{href}"
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
