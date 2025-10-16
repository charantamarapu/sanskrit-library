'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
    const pathname = usePathname();

    return (
        <nav className="bg-gray-900 text-white shadow-md">
            <div className="container mx-auto px-6 py-3">
                <div className="flex items-center justify-between">
                    <Link href="/" className="text-2xl font-bold hover:text-blue-400 transition-colors">
                        📚 Sanskrit Library
                    </Link>

                    <div className="flex gap-4">
                        <Link
                            href="/granthas"
                            className={`px-4 py-2 rounded font-medium transition-colors ${pathname?.startsWith('/granthas')
                                    ? 'bg-blue-600 text-white'
                                    : 'hover:bg-gray-800'
                                }`}
                        >
                            Library
                        </Link>

                        <Link
                            href="/suggestions"
                            className={`px-4 py-2 rounded font-medium transition-colors ${pathname === '/suggestions'
                                    ? 'bg-blue-600 text-white'
                                    : 'hover:bg-gray-800'
                                }`}
                        >
                            Suggestions
                        </Link>

                        <a
                            href="http://localhost:8000/admin/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-4 py-2 rounded font-medium hover:bg-gray-800 transition-colors"
                        >
                            Admin
                        </a>
                    </div>
                </div>
            </div>
        </nav>
    );
}
