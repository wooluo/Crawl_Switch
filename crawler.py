from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import random
import pytz  # 用于时区转换

# 存储所有结果
all_results = []

# 配置
base_url = "https://www.gamer520.com/switchyouxi"
pages_to_crawl = 2  # 抓取前2页
timeout = 15000  # 15秒超时

# 启动浏览器
with sync_playwright() as p:
    # 增加浏览器启动参数
    browser = p.chromium.launch(
        headless=True,
        timeout=timeout,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox'
        ]
    )
    
    # 创建上下文（可配置User-Agent等）
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    page = context.new_page()

    for page_num in range(1, pages_to_crawl + 1):
        url = f"{base_url}/page/{page_num}" if page_num > 1 else base_url
        print(f"正在访问第 {page_num} 页: {url}")

        try:
            # 增加页面访问配置
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            
            # 更可靠的等待方式
            page.wait_for_load_state("networkidle", timeout=timeout)
            
            # 备用选择器方案
            try:
                page.wait_for_selector("article.post-grid", timeout=15000)
            except:
                page.wait_for_selector("article.post", timeout=15000)  # 尝试备用选择器

            # 滚动页面触发懒加载
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)  # 等待懒加载完成

            # 获取 HTML 内容
            html = page.content()

            # 解析 HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # 更灵活的选择器方案
            game_items = soup.find_all('article', class_=lambda x: x and ('post-grid' in x or 'post' in x))

            print(f"🔍 找到 {len(game_items)} 个游戏条目")

            for item in game_items:
                try:
                    title = item.find('h2', class_=lambda x: x and 'title' in x).get_text().strip()
                    link = item.find('a')['href']
                    
                    # 更灵活的日期获取方式
                    time_tag = item.find('time')
                    date_str = time_tag.get('datetime') if time_tag else ''
                    
                    # 处理图片懒加载
                    img = item.find('img')
                    image = img.get('data-src') or img.get('src') if img else ''

                    # 时区转换逻辑（UTC+8）
                    if date_str:
                        try:
                            # 尝试解析ISO格式日期（如 "2023-05-01T12:00:00Z"）
                            date_utc = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
                            date_local = date_utc.astimezone(pytz.timezone("Asia/Shanghai"))  # UTC+8
                            formatted_date = date_local.strftime("%Y-%m-%d %H:%M")
                        except ValueError:
                            # 其他格式直接使用原始值（或自定义处理）
                            formatted_date = date_str
                    else:
                        formatted_date = ""

                    if title and link:
                        all_results.append({
                            'title': title,
                            'link': link,
                            'date': formatted_date,  # 修正后的日期
                            'image': image
                        })
                except Exception as item_error:
                    print(f"⚠️ 解析条目失败: {item_error}")
                    continue

            # 更自然的延迟
            time.sleep(random.uniform(3, 8))

        except Exception as e:
            print(f"⚠️ 页面加载失败（第 {page_num} 页）: {str(e)[:200]}...")
            continue

    # 确保资源释放
    context.close()
    browser.close()

# 获取当前时间（用于文件名）
current_time = datetime.now(pytz.timezone("Asia/Shanghai"))
timestamp = current_time.strftime('%Y%m%d_%H%M%S')

# 生成带时间戳的文件名
json_filename = f"results_{timestamp}.json"
md_filename = f"switch_news_{timestamp}.md"

# 写入JSON文件
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

# 生成Markdown文件（带UTC+8的当前时间）
formatted_time = current_time.strftime('%Y-%m-%d %H:%M')
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(f"# Nintendo Switch 游戏信息\n更新时间：{formatted_time} (UTC+8)\n\n")
    if all_results:
        f.write(f"✅ 共找到 {len(all_results)} 条游戏信息：\n\n")
        for game in all_results:
            f.write(f"- [{game['title']}]({game['link']})")
            if game['date']:
                f.write(f" ({game['date']})")
            if game['image']:
                f.write(f"\n  ![封面]({game['image']})")
            f.write("\n")
    else:
        f.write("❌ 当前没有找到任何与 Nintendo Switch 相关的游戏信息。\n")

print(f"🎉 数据已保存至 {json_filename} 和 {md_filename}")
