'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Game {
  title: string;
  link: string;
  date: string;
  image: string;
}

export default function Home() {
  const [posts, setPosts] = useState<any[]>([]);
  const [monthStats, setMonthStats] = useState<Array<{ month: string; count: number }>>([]);
  const [searchResults, setSearchResults] = useState<Game[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'home' | 'archive'>('home');

  useEffect(() => {
    fetch('/api/posts')
      .then(res => res.json())
      .then(data => {
        setPosts(data.posts || []);
        setMonthStats(data.monthStats || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load posts:', err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      fetch(`/api/search?q=${encodeURIComponent(searchQuery)}`)
        .then(res => res.json())
        .then(data => setSearchResults(data.results || []));
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const totalGames = posts.reduce((sum, p) => sum + p.gameCount, 0);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
              🎮 Nintendo Switch 游戏资讯
            </h1>
            <div className="flex gap-2">
              <button
                onClick={() => setView('home')}
                className={`px-4 py-2 rounded-lg transition-colors ${view === 'home' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                首页
              </button>
              <button
                onClick={() => setView('archive')}
                className={`px-4 py-2 rounded-lg transition-colors ${view === 'archive' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                归档
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {view === 'home' && (
          <>
            {/* Stats Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-500">{totalGames}</div>
                  <div className="text-gray-500 text-sm">游戏总数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-500">{posts.length}</div>
                  <div className="text-gray-500 text-sm">更新次数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-500">{monthStats.length}</div>
                  <div className="text-gray-500 text-sm">月份归档</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-500">
                    {posts[0]?.updateTime?.split(' ')[0] || '-'}
                  </div>
                  <div className="text-gray-500 text-sm">最后更新</div>
                </div>
              </div>
            </div>

            {/* Search */}
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="🔍 搜索游戏名称..."
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {searchResults.length > 0 && (
                <div className="mt-4 space-y-2 max-h-96 overflow-y-auto">
                  {searchResults.map((game, i) => (
                    <Link
                      key={i}
                      href={game.link}
                      target="_blank"
                      className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="font-medium text-gray-800">{game.title}</div>
                      <div className="text-sm text-gray-500">{game.date}</div>
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Month Archive */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">📅 月份归档</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                {monthStats.map((stat) => (
                  <div
                    key={stat.month}
                    className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => setView('archive')}
                  >
                    <div className="text-sm font-medium text-gray-700">{stat.month}</div>
                    <div className="text-xs text-gray-500">{stat.count} 条</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {view === 'archive' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-gray-800">📚 全部更新记录</h2>
            {posts.map((post) => (
              <Link
                key={post.filename}
                href={`/post/${post.filename.replace('.md', '')}`}
                className="block bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-800">
                      {post.updateTime}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      {post.gameCount} 条游戏信息
                    </div>
                  </div>
                  <div className="text-blue-500">→</div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-6 text-center text-gray-500 text-sm">
          <p>数据来源: crawler | 部署于 Vercel | 更新时间: {posts[0]?.updateTime || '-'}</p>
        </div>
      </footer>
    </div>
  );
}
