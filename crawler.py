from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import pytz
import os

# 配置参数
CONFIG = {
    "base_url": "https://www.gamer520.com/gameswitch",
    "pages_to_crawl": 5,
    "timeout": 45000,  # 45秒超时
    "max_retries": 3,  # 最大重试次数
    "retry_delay": 5,  # 重试延迟(秒)
    "min_delay": 3,    # 最小请求间隔
    "max_delay": 8     # 最大请求间隔
}

# 用户代理列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def get_timestamp():
    """获取当前时间戳"""
    return datetime.now(pytz.timezone("Asia/Shanghai")).strftime('%Y%m%d_%H%M%S')

def save_results(data):
    """保存结果到文件"""
    timestamp = get_timestamp()

    # 确保输出目录存在
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)

    json_filename = os.path.join(output_dir, f"results_{timestamp}.json")
    md_filename = os.path.join(output_dir, f"switch_news_{timestamp}.md")

    # 同时创建 latest 软链接/副本
    json_latest = os.path.join(output_dir, "results_latest.json")
    md_latest = os.path.join(output_dir, "switch_news_latest.md")

    current_time = datetime.now(pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M')

    # 保存JSON文件
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # 复制一份为 latest
    with open(json_latest, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 生成Markdown文件
    md_content = f"# Nintendo Switch 游戏信息\n更新时间：{current_time} (UTC+8)\n\n"
    if data:
        md_content += f"✅ 共找到 {len(data)} 条游戏信息：\n\n"
        for game in data:
            md_content += f"- [{game['title']}]({game['link']})"
            if game['date']:
                md_content += f" ({game['date']})"
            if game['image']:
                md_content += f"\n  ![封面]({game['image']})"
            md_content += "\n"
    else:
        md_content += "❌ 当前没有找到任何与 Nintendo Switch 相关的游戏信息。\n"

    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(md_latest, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"🎉 数据已保存至 {json_filename} 和 {md_filename}")
    return json_filename, md_filename

def scrape_page(page, url, attempt=1):
    """抓取单个页面"""
    try:
        # 随机延迟避免被屏蔽
        time.sleep(random.uniform(CONFIG['min_delay'], CONFIG['max_delay']))
        
        # 访问页面
        page.goto(
            url,
            timeout=CONFIG['timeout'],
            wait_until="networkidle"  # 更宽松的等待条件
        )
        
        # 等待主要内容加载
        page.wait_for_selector("article.post", timeout=20000)
        
        # 滚动页面触发懒加载
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(1, 3))
        
        # 获取页面内容
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # 解析游戏条目
        game_items = soup.find_all('article', class_=lambda x: x and ('post-grid' in x or 'post' in x))
        print(f"🔍 找到 {len(game_items)} 个游戏条目")
        
        results = []
        for item in game_items:
            try:
                title = item.find('h2', class_=lambda x: x and 'title' in x).get_text().strip()
                link = item.find('a')['href']
                
                # 处理日期
                time_tag = item.find('time')
                date_str = time_tag.get('datetime') if time_tag else ''
                formatted_date = ""
                
                if date_str:
                    try:
                        date_utc = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
                        date_local = date_utc.astimezone(pytz.timezone("Asia/Shanghai"))
                        formatted_date = date_local.strftime("%Y-%m-%d %H:%M")
                    except ValueError:
                        formatted_date = date_str
                
                # 处理图片
                img = item.find('img')
                image = img.get('data-src') or img.get('src') if img else ''
                
                if title and link:
                    results.append({
                        'title': title,
                        'link': link,
                        'date': formatted_date,
                        'image': image
                    })
            except Exception as e:
                print(f"⚠️ 解析条目失败: {str(e)[:100]}")
                continue
        
        return results
        
    except Exception as e:
        print(f"⚠️ 第 {attempt} 次尝试失败: {str(e)[:200]}...")
        if attempt < CONFIG['max_retries']:
            time.sleep(CONFIG['retry_delay'])
            return scrape_page(page, url, attempt + 1)
        else:
            print(f"❌ 页面抓取失败: {url}")
            return []

def main():
    """主函数"""
    all_results = []
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'  # 针对Docker环境的优化
            ]
        )
        
        # 创建上下文
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            for page_num in range(1, CONFIG['pages_to_crawl'] + 1):
                url = f"{CONFIG['base_url']}/page/{page_num}" if page_num > 1 else CONFIG['base_url']
                print(f"\n正在访问第 {page_num} 页: {url}")
                
                # 在GitHub Actions环境中保存调试截图
                if os.getenv('GITHUB_ACTIONS') == 'true':
                    page.screenshot(path=f"debug_page_{page_num}.png")
                    print("已保存调试截图")
                
                page_results = scrape_page(page, url)
                all_results.extend(page_results)
                
                # 随机延迟避免频繁请求
                time.sleep(random.uniform(CONFIG['min_delay'], CONFIG['max_delay']))
        
        finally:
            # 确保资源释放
            context.close()
            browser.close()
    
    # 保存结果
    return save_results(all_results)

if __name__ == "__main__":
    start_time = time.time()
    json_file, md_file = main()
    print(f"⏱️ 总耗时: {time.time() - start_time:.2f}秒")
# 原始有问题的代码：
# print(f"📊 总抓取数量: {len(json.load(open(json_file, 'r', encoding='utf-8')) if os.path.exists(json_file) else 0}")

# 修正后的代码：
if os.path.exists(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"📊 总抓取数量: {len(data)}")
else:
    print("📊 没有抓取到任何数据")
