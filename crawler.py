from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

# 存储所有结果
all_results = []

# 配置
base_url = "https://www.gamer520.com/switchyouxi" 
pages_to_crawl = 5  # 抓取前 5 页

# 启动浏览器
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for page_num in range(1, pages_to_crawl + 1):
        url = f"{base_url}/page/{page_num}" if page_num > 1 else base_url
        print(f"正在访问第 {page_num} 页: {url}")

        try:
            # 访问页面并等待内容加载完成（根据实际网页结构调整 selector）
            page.goto(url)
            page.wait_for_selector("article.post-grid", timeout=30000)

            # 获取 HTML 内容
            html = page.content()

            # 解析 HTML
            soup = BeautifulSoup(html, 'html.parser')
            game_items = soup.find_all('article', class_='post-grid')

            print(f"🔍 找到 {len(game_items)} 个游戏条目")

            for item in game_items:
                title_tag = item.find('h2', class_='entry-title')
                link_tag = item.find('a')
                time_tag = item.find('time')
                image_tag = item.find('img', class_='lazyload')

                title = title_tag.get_text().strip() if title_tag else ''
                href = link_tag['href'] if link_tag else ''
                date = time_tag.get('datetime') if time_tag else ''
                image = image_tag.get('data-src') if image_tag else ''

                if title and href:
                    all_results.append({
                        'title': title,
                        'link': href,
                        'date': date,
                        'image': image
                    })

            # 随机延迟 2~5 秒
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            print(f"⚠️ 页面加载失败（第 {page_num} 页）: {e}")
            continue

    browser.close()

# 写入 JSON 文件
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

# 写入 Markdown 文件
with open("switch_news.md", "w", encoding="utf-8") as f:
    f.write(f"# Nintendo Switch 游戏信息\n更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    if all_results:
        f.write(f"✅ 共找到 {len(all_results)} 条游戏信息：\n\n")
        for game in all_results:
            f.write(f"- [{game['title']}]({game['link']})\n")
            if game['image']:
                f.write(f"  ![封面]({game['image']})\n")
    else:
        f.write("❌ 当前没有找到任何与 Nintendo Switch 相关的游戏信息。\n")
