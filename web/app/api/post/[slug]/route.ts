import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Vercel 部署时 results 目录在项目根目录
function getResultsDir() {
  // Vercel: process.cwd() 是 /var/task/.next
  // 项目根目录是 /var/task
  const cwd = process.cwd();
  if (cwd.includes('.next')) {
    return path.join(cwd, '../../results/history');
  }
  // 本地开发
  return path.join(cwd, '../results/history');
}

const RESULTS_DIR = getResultsDir();

function parseMarkdownFile(content: string): any[] {
  const games: any[] = [];
  const lines = content.split('\n');

  for (const line of lines) {
    const linkMatch = line.match(/- \[([^\]]+)\]\(([^)]+)\)\s*(?:\(([^)]+)\))?/);
    if (linkMatch) {
      const title = linkMatch[1];
      const link = linkMatch[2];
      const date = linkMatch[3] || '';
      games.push({ title, link, date, image: '' });
    }

    const imgMatch = line.match(/!\[封面\]\(([^)]+)\)/);
    if (imgMatch && games.length > 0) {
      games[games.length - 1].image = imgMatch[1];
    }
  }

  return games;
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;
  const filename = `${slug}.md`;
  const filepath = path.join(RESULTS_DIR, filename);

  try {
    if (!fs.existsSync(filepath)) {
      return NextResponse.json({ error: 'Post not found' }, { status: 404 });
    }

    const content = fs.readFileSync(filepath, 'utf-8');

    const timeMatch = content.match(/更新时间：(\d{4}-\d{2}-\d{2} \d{2}:\d{2})/);
    const updateTime = timeMatch ? timeMatch[1] : '';

    const countMatch = content.match(/共找到 (\d+) 条/);
    const gameCount = countMatch ? parseInt(countMatch[1]) : 0;

    const games = parseMarkdownFile(content);

    return NextResponse.json({
      filename,
      updateTime,
      games,
      gameCount
    });
  } catch (error) {
    console.error('Post API Error:', error);
    return NextResponse.json({ error: 'Failed to load post' }, { status: 500 });
  }
}
