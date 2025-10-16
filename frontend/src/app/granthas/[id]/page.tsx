'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { granthaAPI } from '@/lib/api';
import WordViewer from '@/components/WordViewer';

export default function GranthaViewPage() {
    const params = useParams();
    const router = useRouter();
    const id = Number(params.id);

    const [grantha, setGrantha] = useState<any>(null);
    const [selectedCommentaries, setSelectedCommentaries] = useState<string[]>([]);
    const [allChecked, setAllChecked] = useState(true);
    const [downloading, setDownloading] = useState(false);

    useEffect(() => {
        fetchGrantha();
    }, [id]);

    const fetchGrantha = async () => {
        try {
            const response = await granthaAPI.get(id);
            setGrantha(response.data);
            setSelectedCommentaries(['all']);
            setAllChecked(true);
        } catch (error) {
            console.error('Error:', error);
        }
    };

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
        try {
            const response = await granthaAPI.filter(id, selectedCommentaries);
            const blob = new Blob([response.data], {
                type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${grantha.title}_filtered.docx`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            alert('Download failed!');
        } finally {
            setDownloading(false);
        }
    };

    if (!grantha) return <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent"></div>
    </div>;

    return (
        <div className="h-screen flex flex-col bg-white">
            {/* Top Bar */}
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
                {/* Compact Sidebar */}
                <aside className="w-80 bg-white border-r border-gray-200 flex flex-col">
                    <div className="p-4 border-b border-gray-200">
                        <h2 className="text-lg font-bold text-gray-900">Filter Commentaries</h2>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4">
                        {/* All */}
                        <label className="flex items-center p-3 bg-gray-50 border-2 border-gray-900 rounded mb-4 cursor-pointer hover:bg-gray-100">
                            <input
                                type="checkbox"
                                checked={allChecked}
                                onChange={handleAllToggle}
                                className="w-5 h-5 mr-3"
                            />
                            <span className="font-bold text-gray-900">All</span>
                        </label>

                        {/* Individual */}
                        {grantha.commentaries && grantha.commentaries.length > 0 ? (
                            <div className="space-y-2">
                                {grantha.commentaries.map((c: string) => (
                                    <label
                                        key={c}
                                        className={`flex items-center p-3 rounded cursor-pointer border-2 ${allChecked
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

                    {/* Actions */}
                    <div className="p-4 border-t border-gray-200 space-y-3">
                        <button
                            onClick={handleDownload}
                            disabled={downloading}
                            className={`w-full py-3 rounded font-bold ${downloading
                                    ? 'bg-gray-400 text-gray-200'
                                    : 'bg-blue-600 text-white hover:bg-blue-700'
                                }`}
                        >
                            {downloading ? 'Downloading...' : '📥 Download'}
                        </button>

                        <button
                            onClick={() => router.push(`/suggestions?grantha=${id}`)}
                            className="w-full bg-gray-900 text-white py-3 rounded hover:bg-black font-bold"
                        >
                            ✍️ Suggest
                        </button>
                    </div>
                </aside>

                {/* Viewer */}
                <main className="flex-1 bg-gray-100">
                    <WordViewer fileUrl={grantha.file} title={grantha.title} />
                </main>
            </div>
        </div>
    );
}
