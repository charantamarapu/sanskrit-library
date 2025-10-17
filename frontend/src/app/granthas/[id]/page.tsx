'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { granthaAPI } from '@/lib/api';
import WordViewer from '@/components/WordViewer';

interface Grantha {
  id: number;
  title: string;
  file: string;
  commentaries: string[];
  uploaded_at: string;
}

export default function GranthaViewPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  
  const [grantha, setGrantha] = useState<Grantha | null>(null);
  const [selectedCommentaries, setSelectedCommentaries] = useState<string[]>([]);
  const [allChecked, setAllChecked] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<string>('');

  const fetchGrantha = useCallback(async () => {
    try {
      const response = await granthaAPI.get(id);
      setGrantha(response.data);
      setSelectedCommentaries(['all']);
      setAllChecked(true);
    } catch (err) {
      console.error('Error:', err);
    }
  }, [id]);

  useEffect(() => {
    fetchGrantha();
  }, [fetchGrantha]);

  const handleAllToggle = () => {
    setAllChecked(!allChecked);
    setSelectedCommentaries(allChecked ? [] : ['all']);
  };

  const handleCommentaryToggle = (commentary: string) => {
    setAllChecked(false);
    if (selectedCommentaries.includes(commentary)) {
      setSelectedCommentaries(selectedCommentaries.filter(c => c !== commentary && c !== 'all'));
    } else {
      setSelectedCommentaries([...selectedCommentaries.filter(c => c !== 'all'), commentary]);
    }
  };

  const handleDownload = async () => {
  setDownloading(true);
  setDownloadProgress('Starting download...');
  
  let progressCounter = 0;
  const progressMessages = [
    'Processing document...',
    'Filtering commentaries...',
    'This may take several minutes for large files...',
    'Still processing, please wait...',
    'Almost done...',
  ];
  
  const progressInterval = setInterval(() => {
    progressCounter++;
    const messageIndex = Math.min(progressCounter, progressMessages.length - 1);
    setDownloadProgress(progressMessages[messageIndex]);
  }, 5000);
  
  try {
    const response = await granthaAPI.filter(id, selectedCommentaries);
    
    clearInterval(progressInterval);
    setDownloadProgress('Download complete! Saving file...');
    
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    // Removed "_filtered" suffix
    link.download = `${grantha?.title}.docx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    setDownloadProgress('');
  } catch (err) {
    clearInterval(progressInterval);
    console.error('Download error:', err);
    
    if (err instanceof Error && err.message.includes('timeout')) {
      setDownloadProgress('');
      alert('Download timed out. The file might be very large. Please try again or contact support.');
    } else {
      setDownloadProgress('');
      alert('Download failed! Please try again.');
    }
  } finally {
    setDownloading(false);
    setDownloadProgress('');
  }
};

  if (!grantha) return <div className="h-screen flex items-center justify-center bg-gray-50">
    <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent"></div>
  </div>;

return (
    <div className="h-screen flex flex-col bg-white">
      <header className="bg-gray-900 text-white px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">{grantha.title}</h1>
        </div>
        <button
          onClick={() => router.push('/granthas')}
          className="bg-white text-gray-900 px-4 py-2 rounded font-medium hover:bg-gray-100"
        >
          ← Back
        </button>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-bold text-gray-900">Filter Commentaries</h2>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <label className="flex items-center p-3 bg-gray-50 border-2 border-gray-900 rounded mb-4 cursor-pointer hover:bg-gray-100">
              <input
                type="checkbox"
                checked={allChecked}
                onChange={handleAllToggle}
                className="w-5 h-5 mr-3"
              />
              <span className="font-bold text-gray-900">All</span>
            </label>
            
            {grantha.commentaries && grantha.commentaries.length > 0 ? (
              <div className="space-y-2">
                {grantha.commentaries.map((c) => (
                  <label 
                    key={c} 
                    className={`flex items-center p-3 rounded cursor-pointer border-2 ${
                      allChecked 
                        ? 'bg-gray-100 border-gray-300 opacity-50 cursor-not-allowed' 
                        : selectedCommentaries.includes(c)
                        ? 'bg-green-50 border-green-600'
                        : 'bg-white border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedCommentaries.includes(c)}
                      onChange={() => handleCommentaryToggle(c)}
                      disabled={allChecked}
                      className="w-5 h-5 mr-3"
                    />
                    <span className="font-medium text-gray-900">{c}</span>
                  </label>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No commentaries defined</p>
            )}
          </div>

          <div className="p-4 border-t border-gray-200 space-y-3">
            {/* Progress Indicator */}
            {downloading && downloadProgress && (
              <div className="bg-blue-50 border-2 border-blue-500 rounded p-3 mb-3">
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent mr-3"></div>
                  <p className="text-blue-900 font-medium text-sm">{downloadProgress}</p>
                </div>
              </div>
            )}
            
            <button
              onClick={handleDownload}
              disabled={downloading}
              className={`w-full py-3 rounded font-bold ${
                downloading
                  ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {downloading ? '⏳ Processing...' : '📥 Download'}
            </button>

            <button
              onClick={() => router.push(`/suggestions?grantha=${id}`)}
              className="w-full bg-gray-900 text-white py-3 rounded hover:bg-black font-bold"
              disabled={downloading}
            >
              ✍️ Suggest
            </button>
          </div>
        </aside>

        <main className="flex-1 bg-gray-100">
          <WordViewer fileUrl={grantha.file} title={grantha.title} />
        </main>
      </div>
    </div>
  );
}
