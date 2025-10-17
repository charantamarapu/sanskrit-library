'use client';

import { useState, useEffect } from 'react';
import { granthaAPI } from '@/lib/api';
import Link from 'next/link';

interface Grantha {
  id: number;
  title: string;
  file: string;
  commentaries: string[];
  uploaded_at: string;
}

export default function GranthasPage() {
  const [granthas, setGranthas] = useState<Grantha[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGranthas();
  }, []);

  const fetchGranthas = async () => {
    try {
      setError(null);
      const response = await granthaAPI.list();
      setGranthas(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch granthas';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const filteredGranthas = granthas.filter((g) =>
    g.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
            <p className="text-lg text-gray-700 font-medium">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-gray-900 text-white shadow-md">
          <div className="container mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold">Library</h1>
            <Link href="/" className="bg-white text-gray-900 px-4 py-2 rounded font-medium hover:bg-gray-100">
              ← Home
            </Link>
          </div>
        </header>
        <div className="container mx-auto px-6 py-12">
          <div className="bg-white border-2 border-red-500 rounded p-8 max-w-2xl mx-auto">
            <p className="font-bold text-2xl mb-4 text-gray-900">Connection Error</p>
            <p className="text-lg mb-6 text-gray-700">{error}</p>
            <button 
              onClick={fetchGranthas}
              className="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700 font-medium"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gray-900 text-white shadow-md">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Library</h1>
            <p className="text-gray-300 text-sm mt-1">{granthas.length} granthas available</p>
          </div>
          <div className="flex gap-3">
            <a 
              href="/admin/"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-gray-700 text-white px-4 py-2 rounded font-medium hover:bg-gray-600 transition-colors"
            >
              Admin
            </a>
            <Link 
              href="/" 
              className="bg-white text-gray-900 px-4 py-2 rounded font-medium hover:bg-gray-100 transition-colors"
            >
              ← Home
            </Link>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-6 py-8">
        <input
          type="text"
          placeholder="🔍 Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded mb-8 focus:outline-none focus:border-blue-600 text-gray-900 bg-white placeholder-gray-500"
        />

        {granthas.length === 0 ? (
          <div className="text-center py-16 bg-white rounded border-2 border-gray-200">
            <div className="text-6xl mb-4">📚</div>
            <p className="text-2xl mb-4 font-bold text-gray-900">No Granthas</p>
            <p className="text-gray-600 mb-6">Upload from admin panel</p>
            <a 
              href="/admin/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 font-medium"
            >
              Admin Panel
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredGranthas.map((grantha) => (
              <Link
                key={grantha.id}
                href={`/granthas/${grantha.id}`}
                className="bg-white rounded p-6 shadow hover:shadow-lg transition-shadow border border-gray-200"
              >
                <div className="text-4xl mb-3">📖</div>
                <h3 className="text-xl font-bold mb-3 text-gray-900">{grantha.title}</h3>
                
                {grantha.commentaries && grantha.commentaries.length > 0 && (
                  <div className="mb-3">
                    <div className="flex flex-wrap gap-2">
                      {grantha.commentaries.map((c) => (
                        <span key={c} className="bg-gray-900 text-white px-2 py-1 rounded text-xs font-medium">
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                <p className="text-gray-500 text-sm">
                  {new Date(grantha.uploaded_at).toLocaleDateString('en-IN')}
                </p>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
