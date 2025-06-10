import requests
from bs4 import BeautifulSoup
import json
import os

url = "http://news.163.com"

response = requests.get(url)
response.encoding = 'utf-8'  # 设置正确的编码
soup = BeautifulSoup(response.text, 'html.parser')

# 假设新闻标题在 a 标签里，class 包含 title
links = soup.find_all('a')

results = []

for link in links:
    title = link.get_text().strip()
    href = link.get('href')
    if title and href and ("北京" in title.lower() or "中国" in title):
        results.append({
            'title': title,
            'link': href
        })

# 写入文件
output_file = "results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"找到 {len(results)} 条关于 中国 的新闻")
