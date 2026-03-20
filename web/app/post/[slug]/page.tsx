'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

interface Game {
  title: string;
  link: string;
  date: string;
  image: string;
}

interface PostData {
  filename: string;
  updateTime: string;
  games: Game[];
  gameCount: number;
}

export default function PostPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [post, setPost] = useState<PostData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/post/${slug}`)
      .then(res => res.json())
      .then(data => {
        setPost(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load post:', err);
        setLoading(false);
      });
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">文章不存在</p>
          <Link href="/" className="text-blue-500 hover:underline">返回首页</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            ← 返回首页
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            Nintendo Switch 游戏信息
          </h1>
          <p className="text-gray-500">
            更新时间：{post.updateTime} (UTC+8)
          </p>
          <p className="text-blue-500 font-medium mt-2">
            共找到 {post.gameCount} 条游戏信息
          </p>
        </div>

        <div className="space-y-4">
          {post.games.map((game, index) => (
            <Link
              key={index}
              href={game.link}
              target="_blank"
              className="block bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex gap-4">
                {game.image && (
                  <div className="flex-shrink-0">
                    <img
                      src={game.image}
                      alt={game.title}
                      className="w-24 h-24 object-cover rounded-lg"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-800 hover:text-blue-500 transition-colors line-clamp-2">
                    {game.title}
                  </h3>
                  {game.date && (
                    <p className="text-sm text-gray-500 mt-1">{game.date}</p>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
