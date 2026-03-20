import { NextResponse } from 'next/server';
import { getAllPosts, getMonthStats } from '@/lib/posts';

export const revalidate = 3600; // 每小时重新验证

export async function GET() {
  try {
    const posts = getAllPosts();
    const monthStats = getMonthStats(posts);

    return NextResponse.json({
      posts,
      monthStats,
      total: posts.length
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to load posts', posts: [], monthStats: [] },
      { status: 500 }
    );
  }
}
