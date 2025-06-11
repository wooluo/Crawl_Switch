import requests
from bs4 import BeautifulSoup
import json
import os

base_url = "https://www.gamer520.com/switchyouxi"
for page in range(1, 6):
    url = f'{base_url}/page/{page}' if page > 1 else base_url
    results = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
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
with open(md_file, "w", encoding="utf-8") as f:
    f.write("# Nintendo Switch 游戏信息\n")
    f.write(f"更新时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    if all_results:
        f.write(f"共找到 {len(all_results)} 条游戏信息：\n\n")
        for item in all_results:
            f.write(f"- [{item['title']}]({item['link']})({item['image']})\n")
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
