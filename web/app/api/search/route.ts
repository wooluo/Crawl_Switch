import { NextRequest, NextResponse } from 'next/server';
import { getAllPosts, searchPosts } from '@/lib/posts';

export const revalidate = 3600;

export async function GET(request: NextRequest) {
  try {
    const query = request.nextUrl.searchParams.get('q') || '';
    const posts = getAllPosts();
    const results = searchPosts(posts, query);

    return NextResponse.json({ results, count: results.length });
  } catch (error) {
    console.error('Search API Error:', error);
    return NextResponse.json({ results: [], count: 0 }, { status: 500 });
  }
}
