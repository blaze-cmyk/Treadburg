"use client";

import React, { useState } from 'react';
import { X, Camera, Send } from 'lucide-react';

interface ScreenshotModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (imageData: string, message: string) => void;
}

export default function ScreenshotModal({ isOpen, onClose, onSubmit }: ScreenshotModalProps) {
  const [message, setMessage] = useState('');
  const [imageData, setImageData] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);

  // Check for pre-captured image when modal opens
  React.useEffect(() => {
    if (isOpen) {
      const tempImage = (window as any).tempChartImage;
      if (tempImage) {
        setImageData(tempImage);
      }
    } else {
      // Reset when modal closes
      setImageData(null);
      setMessage('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCapture = async () => {
    setIsCapturing(true);
    try {
      // Show instructions
      const proceed = window.confirm(
        '📸 SCREENSHOT INSTRUCTIONS:\n\n' +
        '1. Click OK\n' +
        '2. Select "Window" or "Chrome Tab"\n' +
        '3. Choose the TradeBerg tab\n' +
        '4. Click "Share"\n\n' +
        'This will capture ONLY the chart area!'
      );

      if (!proceed) {
        setIsCapturing(false);
        return;
      }

      // Use browser's native screenshot API
      const stream = await (navigator.mediaDevices as any).getDisplayMedia({
        video: { 
          mediaSource: 'window',
          displaySurface: 'window'
        },
        preferCurrentTab: true
      });

      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      await new Promise(resolve => {
        video.onloadedmetadata = resolve;
      });

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx?.drawImage(video, 0, 0);

      stream.getTracks().forEach((track: MediaStreamTrack) => track.stop());

      const capturedImage = canvas.toDataURL('image/png');
      setImageData(capturedImage);

    } catch (error) {
      console.error('Screenshot capture error:', error);
      alert('Screenshot cancelled or failed. Please try again.');
    } finally {
      setIsCapturing(false);
    }
  };

  const handleSubmit = () => {
    if (imageData && message.trim()) {
      onSubmit(imageData, message);
      setMessage('');
      setImageData(null);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#1a1a1a] rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden border border-gray-800">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <Camera size={24} />
            Capture Chart Screenshot
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Screenshot Preview */}
          {imageData ? (
            <div className="space-y-2">
              <label className="text-sm text-gray-400">Screenshot Preview:</label>
              <div className="relative rounded-lg overflow-hidden border border-gray-700">
                <img src={imageData} alt="Chart screenshot" className="w-full" />
              </div>
            </div>
          ) : (
            <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center">
              <Camera size={48} className="mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 mb-4 font-semibold">Ready to capture chart</p>
              <button
                onClick={handleCapture}
                disabled={isCapturing}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-8 py-3 rounded-lg transition-colors text-lg font-semibold"
              >
                {isCapturing ? '📸 Capturing...' : '📸 Capture Chart Now'}
              </button>
              <div className="mt-6 text-left bg-gray-800/50 rounded-lg p-4">
                <p className="text-sm text-gray-300 font-semibold mb-2">📋 Quick Steps:</p>
                <ol className="text-xs text-gray-400 space-y-1 list-decimal list-inside">
                  <li>Click the button above</li>
                  <li>Select <span className="text-blue-400 font-semibold">"Window"</span> or <span className="text-blue-400 font-semibold">"Chrome Tab"</span></li>
                  <li>Choose this TradeBerg tab</li>
                  <li>Click "Share"</li>
                </ol>
                <p className="text-xs text-green-400 mt-3">✅ This captures ONLY the chart, not your entire screen!</p>
              </div>
            </div>
          )}

          {/* Message Input */}
          <div className="space-y-2">
            <label className="text-sm text-gray-400">
              What would you like to analyze? *
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Example: Analyze this chart for support and resistance levels, identify patterns, or suggest entry points..."
              className="w-full bg-[#2a2a2a] text-white border border-gray-700 rounded-lg p-3 min-h-[100px] focus:outline-none focus:border-blue-500 transition-colors resize-none"
              disabled={!imageData}
            />
            <p className="text-xs text-gray-500">
              Describe what you want the AI to analyze in the chart
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-gray-800 bg-[#151515]">
          <div className="flex gap-2">
            {imageData && (
              <button
                onClick={handleCapture}
                disabled={isCapturing}
                className="text-gray-400 hover:text-white px-4 py-2 rounded-lg transition-colors text-sm"
              >
                Recapture
              </button>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-400 hover:text-white transition-colors rounded-lg"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!imageData || !message.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Send size={18} />
              Send to Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
