# Nintendo Switch 新闻自动爬虫 🎮

![GitHub Actions](https://img.shields.io/github/actions/workflow/status/wooluo/Crawl_Switch/switch-crawler.yml?label=自动更新)
![GitHub last commit](https://img.shields.io/github/last-commit/wooluo/Crawl_Switch?label=最后更新)
![GitHub License](https://img.shields.io/github/license/wooluo/Crawl_Switch)

## 项目简介

本仓库是一个自动化Nintendo Switch新闻爬虫，每天自动抓取最新Switch相关新闻并生成结构化数据报告。

[查看工作流运行状态](https://github.com/wooluo/Crawl_Switch/actions/workflows/switch-crawler.yml)

## ✨ 功能特性

- **定时自动运行**：每天UTC时间9:00自动执行
- **多格式输出**：
  - `results/results_latest.json` - 最新结构化数据
  - `results/switch_news_latest.md` - 最新格式化报告
- **浏览器自动化**：使用Playwright处理动态内容
- **自动提交更新**：结果自动推送至仓库

## 🛠 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.10 | 主程序语言 |
| Playwright | 浏览器自动化 |
| BeautifulSoup4 | HTML解析 |
| GitHub Actions | 自动化调度 |

## ⚙️ 工作流程

1. **定时触发**：每天UTC 9:00自动运行
2. **环境准备**：
   - 安装Python 3.10
   - 配置Playwright浏览器环境
3. **数据采集**：
   - 执行`crawler.py`脚本
4. **结果处理**：
   - 生成JSON和Markdown文件到 `results/` 目录
5. **自动提交**：
   - 检测变更并提交更新

## 📂 文件结构

```
Crawl_Switch/
├── .github/
│   └── workflows/
│       └── switch-crawler.yml  # GitHub Actions配置
├── results/
│   ├── results_YYYYMMDD_HHMMSS.json   # 历史JSON数据
│   ├── switch_news_YYYYMMDD_HHMMSS.md # 历史报告
│   ├── results_latest.json            # 最新JSON（软链接/副本）
│   └── switch_news_latest.md          # 最新报告（软链接/副本）
├── history/                  # 历史记录存档（已迁移）
├── crawler.py                # 主爬虫脚本
├── requirements.txt          # 依赖列表
└── README.md                 # 项目说明
```

## 🚀 使用方式

### 自动使用
- 系统每天自动更新
- 查看最新报告：
  - [JSON格式](./results/results_latest.json)
  - [Markdown格式](./results/switch_news_latest.md)

### 手动运行
```bash
git clone https://github.com/wooluo/Crawl_Switch.git
cd Crawl_Switch
pip install -r requirements.txt
python -m playwright install
python crawler.py
```

## 🤝 参与贡献
欢迎通过Issue或PR提交改进建议

## 📜 许可证
MIT License © 2024 wooluo
