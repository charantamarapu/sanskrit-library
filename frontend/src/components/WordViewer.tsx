'use client';

import React, { useEffect, useRef, useState } from 'react';
import { renderAsync } from 'docx-preview';

interface WordViewerProps {
  fileUrl: string;
  title: string;
}

export default function WordViewer({ fileUrl, title }: WordViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDocument = async () => {
      if (!containerRef.current) return;

      try {
        setLoading(true);
        setError(null);

        // Extract relative path from full URL
        // fileUrl might be: http://YOUR_IP:8000/media/word_files/sample.docx
        // We want: /media/word_files/sample.docx
        let documentUrl = fileUrl;
        
        if (fileUrl.includes('/media/')) {
          // Extract path starting from /media/
          const mediaPath = fileUrl.substring(fileUrl.indexOf('/media/'));
          documentUrl = mediaPath;
        }

        console.log('Loading document from:', documentUrl);

        const response = await fetch(documentUrl);
        if (!response.ok) {
          throw new Error(`Failed to fetch document: ${response.status}`);
        }
        
        const blob = await response.blob();
        containerRef.current.innerHTML = '';

        // Render full document
        await renderAsync(blob, containerRef.current, undefined, {
          className: 'docx-wrapper',
          inWrapper: true,
          ignoreWidth: false,
          ignoreHeight: false,
          ignoreFonts: false,
          breakPages: true,
          ignoreLastRenderedPageBreak: false,
          experimental: false,
          trimXmlDeclaration: true,
          useBase64URL: false,
          renderChanges: false,
          renderHeaders: true,
          renderFooters: true,
          renderFootnotes: true,
          renderEndnotes: true,
        });

        setLoading(false);
      } catch (err) {
        console.error('Error loading document:', err);
        setError('Failed to load document');
        setLoading(false);
      }
    };

    loadDocument();
  }, [fileUrl]);

  return (
    <div className="w-full h-full flex flex-col bg-gray-100">
      <div className="bg-white border-b-2 border-gray-200 px-6 py-4">
        <h2 className="text-xl font-bold text-gray-900">{title}</h2>
        <p className="text-gray-600 text-sm mt-1">Document Preview - Full Document</p>
      </div>

      {loading && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
            <p className="text-gray-700 font-medium">Loading full document...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="bg-red-50 border-2 border-red-500 text-red-900 px-6 py-4 rounded">
            <p className="font-bold">Error</p>
            <p>{error}</p>
          </div>
        </div>
      )}

      <div 
        ref={containerRef}
        className="flex-1 overflow-auto p-8 bg-gray-100"
        style={{ display: loading ? 'none' : 'block' }}
      />
    </div>
  );
}
