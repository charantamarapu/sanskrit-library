'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { suggestionAPI, granthaAPI } from '@/lib/api';

export default function SuggestionsPage() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const granthaId = searchParams.get('grantha');

    const [granthas, setGranthas] = useState([]);
    const [formData, setFormData] = useState({
        grantha: granthaId || '',
        user_name: '',
        user_email: '',
        suggestion: '',
    });
    const [showSuccess, setShowSuccess] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchGranthas();
    }, []);

    const fetchGranthas = async () => {
        const response = await granthaAPI.list();
        setGranthas(response.data);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            await suggestionAPI.create(formData);
            setShowSuccess(true);
            setFormData({ grantha: '', user_name: '', user_email: '', suggestion: '' });
            setTimeout(() => setShowSuccess(false), 5000);
        } catch (error) {
            alert('Failed to submit suggestion.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Compact Header */}
            <header className="bg-gray-900 text-white shadow-md">
                <div className="container mx-auto px-6 py-3 flex items-center justify-between">
                    <h1 className="text-xl font-bold">Suggest Corrections</h1>
                    <button
                        onClick={() => router.back()}
                        className="bg-white text-gray-900 px-4 py-2 rounded text-sm font-medium hover:bg-gray-100"
                    >
                        ← Back
                    </button>
                </div>
            </header>

            <main className="container mx-auto px-6 py-6 max-w-2xl">
                {/* Compact Success Message */}
                {showSuccess && (
                    <div className="bg-green-50 border-2 border-green-600 rounded p-4 mb-6 flex items-center justify-between">
                        <div className="flex items-center">
                            <span className="text-2xl mr-3">✅</span>
                            <div>
                                <p className="font-bold text-green-900">Success!</p>
                                <p className="text-green-800 text-sm">Suggestion submitted</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setShowSuccess(false)}
                            className="text-green-900 hover:text-green-700 font-bold text-xl"
                        >
                            ×
                        </button>
                    </div>
                )}

                {/* Compact Form */}
                <div className="bg-white rounded shadow border border-gray-200 p-6">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Grantha */}
                        <div>
                            <label className="block font-bold mb-1 text-gray-900">
                                Grantha <span className="text-red-600">*</span>
                            </label>
                            <select
                                value={formData.grantha}
                                onChange={(e) => setFormData({ ...formData, grantha: e.target.value })}
                                required
                                className="w-full p-3 border-2 border-gray-300 rounded focus:outline-none focus:border-blue-600 text-gray-900 bg-white"
                            >
                                <option value="">-- Select --</option>
                                {granthas.map((g: any) => (
                                    <option key={g.id} value={g.id}>{g.title}</option>
                                ))}
                            </select>
                        </div>

                        {/* Name */}
                        <div>
                            <label className="block font-bold mb-1 text-gray-900">
                                Name <span className="text-gray-500 text-xs font-normal">(optional)</span>
                            </label>
                            <input
                                type="text"
                                value={formData.user_name}
                                onChange={(e) => setFormData({ ...formData, user_name: e.target.value })}
                                placeholder="Your name"
                                className="w-full p-3 border-2 border-gray-300 rounded focus:outline-none focus:border-blue-600 text-gray-900 bg-white placeholder-gray-400"
                            />
                        </div>

                        {/* Email */}
                        <div>
                            <label className="block font-bold mb-1 text-gray-900">
                                Email <span className="text-gray-500 text-xs font-normal">(optional)</span>
                            </label>
                            <input
                                type="email"
                                value={formData.user_email}
                                onChange={(e) => setFormData({ ...formData, user_email: e.target.value })}
                                placeholder="your@email.com"
                                className="w-full p-3 border-2 border-gray-300 rounded focus:outline-none focus:border-blue-600 text-gray-900 bg-white placeholder-gray-400"
                            />
                        </div>

                        {/* Suggestion */}
                        <div>
                            <label className="block font-bold mb-1 text-gray-900">
                                Suggestion <span className="text-red-600">*</span>
                            </label>
                            <textarea
                                value={formData.suggestion}
                                onChange={(e) => setFormData({ ...formData, suggestion: e.target.value })}
                                required
                                rows={6}
                                placeholder="Describe the correction..."
                                className="w-full p-3 border-2 border-gray-300 rounded focus:outline-none focus:border-blue-600 resize-none text-gray-900 bg-white placeholder-gray-400"
                            />
                        </div>

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={submitting}
                            className={`w-full py-3 rounded font-bold transition-all ${submitting
                                    ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                                    : 'bg-blue-600 text-white hover:bg-blue-700'
                                }`}
                        >
                            {submitting ? 'Submitting...' : 'Submit Suggestion'}
                        </button>
                    </form>
                </div>

                {/* Compact Tips */}
                <div className="mt-6 bg-blue-50 border border-blue-400 rounded p-4">
                    <p className="text-blue-900 font-bold text-sm mb-2">💡 Tips:</p>
                    <ul className="text-blue-800 text-sm space-y-1">
                        <li>• Mention specific location (page, verse, etc.)</li>
                        <li>• Quote the incorrect text if possible</li>
                        <li>• Provide correct text or reference</li>
                    </ul>
                </div>
            </main>
        </div>
    );
}
