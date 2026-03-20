import fs from 'fs';
import path from 'path';

export interface Game {
  title: string;
  link: string;
  date: string;
  image: string;
}

export interface NewsPost {
  filename: string;
  updateTime: string;
  timestamp: string;
  date: Date;
  games: Game[];
  gameCount: number;
}

// Vercel 部署时 results 目录在项目根目录
function getResultsDir() {
  const cwd = process.cwd();
  if (cwd.includes('.next')) {
    return path.join(cwd, '../../results/history');
  }
  return path.join(cwd, '../results/history');
}

const RESULTS_DIR = getResultsDir();

function parseMarkdownFile(content: string): Game[] {
  const games: Game[] = [];
  const lines = content.split('\n');

  for (const line of lines) {
    // 匹配格式: - [标题](链接) (日期)
    const linkMatch = line.match(/- \[([^\]]+)\]\(([^)]+)\)\s*(?:\(([^)]+)\))?/);
    if (linkMatch) {
      const title = linkMatch[1];
      const link = linkMatch[2];
      const date = linkMatch[3] || '';

      // 检查下一行是否有图片
      games.push({ title, link, date, image: '' });
    }

    // 匹配图片行
    const imgMatch = line.match(/!\[封面\]\(([^)]+)\)/);
    if (imgMatch && games.length > 0) {
      games[games.length - 1].image = imgMatch[1];
    }
  }

  return games;
}

function parseFilename(filename: string): { date: Date; timestamp: string } {
  // switch_news_YYYYMMDD_HHMMSS.md
  const match = filename.match(/switch_news_(\d{8})_(\d{6})\.md/);
  if (match) {
    const dateStr = match[1];
    const timeStr = match[2];
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    const hour = timeStr.substring(0, 2);
    const minute = timeStr.substring(2, 4);
    const second = timeStr.substring(4, 6);

    return {
      date: new Date(parseInt(year), parseInt(month) - 1, parseInt(day)),
      timestamp: `${year}-${month}-${day} ${hour}:${minute}`
    };
  }
  return { date: new Date(), timestamp: '' };
}

export function getAllPosts(): NewsPost[] {
  if (!fs.existsSync(RESULTS_DIR)) {
    return [];
  }

  const filenames = fs.readdirSync(RESULTS_DIR)
    .filter(f => f.startsWith('switch_news_') && f.endsWith('.md'))
    .sort()
    .reverse();

  const posts: NewsPost[] = [];

  for (const filename of filenames) {
    const filepath = path.join(RESULTS_DIR, filename);
    const content = fs.readFileSync(filepath, 'utf-8');

    // 提取更新时间
    const timeMatch = content.match(/更新时间：(\d{4}-\d{2}-\d{2} \d{2}:\d{2})/);
    const updateTime = timeMatch ? timeMatch[1] : '';

    // 提取游戏数量
    const countMatch = content.match(/共找到 (\d+) 条/);
    const gameCount = countMatch ? parseInt(countMatch[1]) : 0;

    const { date, timestamp } = parseFilename(filename);

    posts.push({
      filename,
      updateTime,
      timestamp,
      date,
      games: parseMarkdownFile(content),
      gameCount
    });
  }

  return posts;
}

export function getPostsByMonth(posts: NewsPost[]): Map<string, NewsPost[]> {
  const byMonth = new Map<string, NewsPost[]>();

  for (const post of posts) {
    const key = `${post.date.getFullYear()}年${String(post.date.getMonth() + 1).padStart(2, '0')}月`;
    if (!byMonth.has(key)) {
      byMonth.set(key, []);
    }
    byMonth.get(key)!.push(post);
  }

  return byMonth;
}

export function getMonthStats(posts: NewsPost[]): Array<{ month: string; count: number }> {
  const stats = new Map<string, number>();

  for (const post of posts) {
    const key = `${post.date.getFullYear()}年${String(post.date.getMonth() + 1).padStart(2, '0')}月`;
    stats.set(key, (stats.get(key) || 0) + post.gameCount);
  }

  return Array.from(stats.entries())
    .map(([month, count]) => ({ month, count }))
    .sort((a, b) => b.month.localeCompare(a.month));
}

export function searchPosts(posts: NewsPost[], query: string): Game[] {
  if (!query.trim()) return [];

  const results: Game[] = [];
  const lowerQuery = query.toLowerCase();

  for (const post of posts) {
    for (const game of post.games) {
      if (game.title.toLowerCase().includes(lowerQuery)) {
        results.push({ ...game, date: post.updateTime });
      }
    }
  }

  return results.slice(0, 50); // 限制结果数量
}
