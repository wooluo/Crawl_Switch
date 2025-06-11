from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import pytz

# 存储所有结果
all_results = []

# 配置
base_url = "https://www.gamer520.com/switchyouxi"
pages_to_crawl = 5  # 抓取前5页
timeout = 40000  # 增加超时时间
max_retries = 3  # 单页最大重试次数

# 启动浏览器
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
    )
    
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080},
        # 屏蔽图片和字体加载加速
        bypass_csp=True
    )
    page = context.new_page()

    for page_num in range(1, pages_to_crawl + 1):
        url = f"{base_url}/page/{page_num}" if page_num > 1 else base_url
        print(f"\n=== 正在抓取第 {page_num} 页 ===")

        retry_count = 0
        while retry_count < max_retries:
            try:
                # 访问页面（强制等待完全加载）
                page.goto(url, timeout=timeout, wait_until="networkidle")
                page.wait_for_load_state("load", timeout=timeout)

                # 检查是否被拦截
                if "anti-bot" in page.content().lower():
                    raise Exception("检测到反爬验证")

                # 滚动页面（模拟人工操作）
                for _ in range(3):
                    page.evaluate("window.scrollBy(0, window.innerHeight * 0.8)")
                    time.sleep(random.uniform(0.5, 2))

                # 等待内容加载
                page.wait_for_selector("article:has(h2)", timeout=15000)
                html = page.content()

                # 解析数据
                soup = BeautifulSoup(html, 'html.parser')
                game_items = soup.find_all('article', class_=lambda x: x and ('post' in x or 'grid' in x))
                print(f"找到 {len(game_items)} 个游戏条目")

                for item in game_items:
                    try:
                        title = item.find('h2').get_text().strip()
                        link = item.find('a')['href']
                        
                        # 处理日期（兼容多种格式）
                        time_tag = item.find('time')
                        date_str = time_tag['datetime'] if time_tag and 'datetime' in time_tag.attrs else ''
                        if date_str:
                            try:
                                date_obj = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
                                date_obj = date_obj.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Asia/Shanghai"))
                                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
                            except:
                                formatted_date = date_str
                        else:
                            formatted_date = ""

                        # 处理图片
                        img = item.find('img')
                        image = (img.get('data-src') or img.get('src') or '').split('?')[0]

                        all_results.append({
                            'title': title,
                            'link': link,
                            'date': formatted_date,
                            'image': image
                        })
                    except Exception as e:
                        print(f"条目解析失败: {str(e)[:50]}...")
                        continue

                break  # 成功则跳出重试循环

            except Exception as e:
                retry_count += 1
                print(f"第 {retry_count} 次重试，错误: {str(e)[:100]}...")
                if retry_count == max_retries:
                    print(f"⚠️ 页面 {page_num} 抓取失败，跳过")
                time.sleep(random.uniform(5, 10))

        # 随机延迟（更自然）
        if page_num < pages_to_crawl:
            delay = random.uniform(5, 15)
            print(f"等待 {delay:.1f} 秒后继续...")
            time.sleep(delay)

    # 关闭浏览器
    context.close()
    browser.close()

# 保存结果
current_time = datetime.now(pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M')
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

with open("switch_news.md", "w", encoding="utf-8") as f:
    f.write(f"# Nintendo Switch 游戏信息\n更新时间：{current_time} (UTC+8)\n\n")
    if all_results:
        f.write(f"✅ 共抓取 {len(all_results)} 条游戏信息（来自 {pages_to_crawl} 页）:\n\n")
        for idx, game in enumerate(all_results, 1):
            f.write(f"{idx}. [{game['title']}]({game['link']})")
            if game['date']:
                f.write(f" - 发布时间: {game['date']}")
            if game['image']:
                f.write(f"\n   ![封面]({game['image']})")
            f.write("\n")
    else:
        f.write("❌ 未获取到任何游戏信息\n")

print(f"\n🎉 完成！共抓取 {len(all_results)} 条数据")
print(f"📄 JSON 文件: results.json")
print(f"📝 Markdown 文件: switch_news.md")
