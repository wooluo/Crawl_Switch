import requests
from bs4 import BeautifulSoup
import json
import os

from datetime import datetime

base_url = "https://www.gamer520.com/switchyouxi"
for page in range(1, 6):
    url = f'{base_url}/page/{page}' if page > 1 else base_url
    results = []

import random
import time

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

headers = {
    'User-Agent': random.choice(user_agents),
    'Referer': 'https://www.gamer520.com/'
}

# 随机延迟1-3秒
time.sleep(random.uniform(1, 3))
response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

all_results = []
keywords = ["中文", "3A", "下载"]

# 获取游戏列表
game_items = soup.find_all('article', class_='post-grid')
print(f"🔍 找到 {len(game_items)} 个游戏条目")

for item in game_items:
    title = item.find('h2', class_='entry-title').get_text().strip() if item.find('h2', class_='entry-title') else ''
    href = item.find('a')['href'] if item.find('a') else ''
    date = item.find('time')['datetime'] if item.find('time') else ''
    image = item.find('img', class_='lazyload')['data-src'] if item.find('img', class_='lazyload') else ''
    
    # 打印调试信息
    print(f"找到游戏: {title}")
    print(f"链接: {href}")
    print(f"封面: {image}")
    
    if title and href:  # 移除关键词过滤，因为所有条目都在switch游戏下载分类下
        # 添加调试信息
        print(f"🔍 处理条目: {title}")
        print(f"  链接: {href}")
        print(f"  匹配结果: {any(keyword.lower() in title.lower() for keyword in keywords)}")
        results.append({
            'title': title,
            'link': href,
            'date': date,
            'image': image
        })
        if results:
            all_results.extend(results)

# 写入 JSON
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

# 写入 Markdown
md_file = "switch_news.md"
# 修改写入Markdown文件的代码部分
with open('switch_news.md', 'w', encoding='utf-8') as f:
    f.write(f"# Nintendo Switch 游戏信息\n更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    for game in all_results:
        # 确保字典中有需要的键
        if 'title' in game and 'href' in game and 'cover' in game:
            f.write(f"找到游戏: {game['title']}\n")
            # 修改封面图片写入部分
             # 或者如果您想控制图片大小
            f.write(f"封面: (`{game['cover']}`)\n")
            f.write(f"链接: `{game['href']}`\n")
            f.write(f"🔍 处理条目: {game['title']}\n")
            f.write(f"  链接: `{game['href']}`\n")
    f.write(f"✅ 共找到 {len(all_results)} 条 Nintendo Switch 游戏信息")
    if all_results:
        f.write(f"共找到 {len(all_results)} 条游戏信息：\n\n")
        for item in all_results:
            f.write(f"- [{item['title']}]\n下载链接：({item['link']})\n![游戏截图]({item['image']})\n")
    else:
        f.write("❌ 当前没有找到任何与 Nintendo Switch 游戏信息。\n")

if all_results:
    print(f"✅ 成功找到 {len(all_results)} 条 Nintendo Switch 游戏信息 (共抓取 {page} 页)")
else:
    print("❌ 没有找到任何 Nintendo Switch 游戏信息")
    print("⚠️ 调试信息:")
    print(f"- 响应状态码: {response.status_code}")
    print(f"- 找到的游戏条目数: {len(game_items)}")
    if game_items:
        first_item = game_items[0]
        print(f"- 第一个条目内容示例: {str(first_item)[:200]}...")
    print(f"- 页面标题: {soup.title.string if soup.title else '无标题'}")
