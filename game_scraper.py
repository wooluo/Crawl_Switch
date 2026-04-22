import logging
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import pytz

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 加载配置文件
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("配置文件 config.json 未找到。")
        return {}

CONFIG = load_config()
USER_AGENTS = CONFIG.get('user_agents', [])

def get_timestamp():
    """获取当前时间戳"""
    return datetime.now(pytz.timezone("Asia/Shanghai")).strftime('%Y%m%d_%H%M%S')

def save_results(data):
    """保存结果到文件"""
    timestamp = get_timestamp()
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'history')
    os.makedirs(results_dir, exist_ok=True)
    json_filename = os.path.join(results_dir, f"results_{timestamp}.json")
    md_filename = os.path.join(results_dir, f"switch_news_{timestamp}.md")
    current_time = datetime.now(pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M')

    # 保存JSON文件
    try:
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"保存JSON文件时出错: {e}")
        return None, None

    # 生成Markdown文件
    try:
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(f"# Nintendo Switch 游戏信息\n更新时间：{current_time} (UTC+8)\n\n")
            if data:
                f.write(f"✅ 共找到 {len(data)} 条游戏信息：\n\n")
                for game in data:
                    f.write(f"- [{game['title']}]({game['link']})")
                    if game['image']:
                        f.write(f"\n  ![封面]({game['image']})")
                    f.write("\n")
            else:
                f.write("❌ 当前没有找到任何与 Nintendo Switch 相关的游戏信息。\n")
    except Exception as e:
        logging.error(f"生成Markdown文件时出错: {e}")
        return None, None

    logging.info(f"🎉 数据已保存至 {json_filename} 和 {md_filename}")
    return json_filename, md_filename

def extract_game_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    game_articles = soup.find_all('article', class_=lambda x: x and 'post' in x)
    results = []

    for article in game_articles:
        try:
            # 提取游戏名称
            title = article.find('h2', class_='entry-title').a.get_text().strip()

            # 提取游戏图片
            img = article.find('img', class_='lazyload')
            image = img.get('data-src') if img else ''

            # 提取游戏链接
            link = article.find('h2', class_='entry-title').a['href']

            if title and link:
                results.append({
                    'title': title,
                    'image': image,
                    'link': link
                })
        except Exception as e:
            logging.warning(f"解析游戏信息时出错: {e}")

    return results

def scrape_page(page, url, attempt=1):
    """抓取单个页面"""
    try:
        # 随机延迟避免被屏蔽
        time.sleep(random.uniform(CONFIG.get('min_delay', 3), CONFIG.get('max_delay', 8)))

        # 访问页面
        page.goto(
            url,
            timeout=CONFIG.get('timeout', 45000),
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
        game_info = extract_game_info(html)
        logging.info(f"🔍 找到 {len(game_info)} 个游戏条目")

        return game_info

    except Exception as e:
        logging.warning(f"⚠️ 第 {attempt} 次尝试失败: {str(e)[:200]}...")
        if attempt < CONFIG.get('max_retries', 3):
            time.sleep(CONFIG.get('retry_delay', 5))
            return scrape_page(page, url, attempt + 1)
        else:
            logging.error(f"❌ 页面抓取失败: {url}")
            return []

def main():
    # 检查并安装浏览器
    if not os.path.exists(os.path.expanduser('~/.cache/ms-playwright')):
        logging.info("Playwright 浏览器未安装，正在安装...")
        os.system("playwright install")
        logging.info("Playwright 浏览器安装完成。")

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
            url = CONFIG.get('base_url', 'https://www.gamer520.com/gameswitch')
            logging.info(f"\n正在访问页面: {url}")

            # 在GitHub Actions环境中保存调试截图
            if os.getenv('GITHUB_ACTIONS') == 'true':
                page.screenshot(path="debug_page.png")
                logging.info("已保存调试截图")

            page_results = scrape_page(page, url)
            all_results.extend(page_results)

        except Exception as e:
            logging.error(f"发生异常: {str(e)}")
        finally:
            # 确保资源释放
            context.close()
            browser.close()

    # 保存结果
    json_file, md_file = save_results(all_results)

    # 输出总抓取数量
    if json_file and os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logging.info(f"📊 总抓取数量: {len(data)}")
        except Exception as e:
            logging.error(f"读取JSON文件时出错: {e}")
    else:
        logging.info("📊 没有抓取到任何数据")

if __name__ == "__main__":
    start_time = time.time()
    main()
    logging.info(f"⏱️ 总耗时: {time.time() - start_time:.2f}秒")