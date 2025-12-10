"use client";

import React, { useEffect, useRef, useState } from 'react';
import { Camera } from 'lucide-react';
import ScreenshotModal from './ScreenshotModal';

interface TradingViewChartProps {
  symbol?: string;
  onScreenshot?: (imageData: string, message?: string) => void;
}

export default function TradingViewChart({ 
  symbol = "BTCUSD", 
  onScreenshot 
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    // Load TradingView widget script
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => initWidget();
    document.head.appendChild(script);

    return () => {
      // Cleanup
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [symbol]);

  const initWidget = () => {
    if (typeof (window as any).TradingView !== 'undefined' && containerRef.current) {
      new (window as any).TradingView.widget({
        autosize: true,
        symbol: symbol,
        interval: "15",
        timezone: "Etc/UTC",
        theme: "dark",
        style: "1",
        locale: "en",
        toolbar_bg: "#f1f3f6",
        enable_publishing: false,
        hide_top_toolbar: false,
        hide_legend: false,
        save_image: false,
        container_id: "tradingview_chart",
        studies: [
          "Volume@tv-basicstudies"
        ],
        show_popup_button: true,
        popup_width: "1000",
        popup_height: "650"
      });
    }
  };

  const captureChartDirectly = async () => {
    // Simply open the modal - user will capture manually
    setIsModalOpen(true);
  };

  const handleScreenshotSubmit = (imageData: string, message: string) => {
    if (onScreenshot) {
      onScreenshot(imageData, message);
    }
    // Clear temp image
    (window as any).tempChartImage = null;
  };

  return (
    <>
      <div className="relative w-full h-full bg-[#131722] rounded-lg overflow-hidden">
        {/* Screenshot Button */}
        <button
          onClick={captureChartDirectly}
          className="absolute top-4 right-4 z-10 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-lg transition-all"
          title="Capture Chart Screenshot"
        >
          <Camera size={20} />
          Capture Chart
        </button>

        {/* TradingView Chart Container */}
        <div 
          ref={containerRef} 
          id="tradingview_chart" 
          className="w-full h-full"
        />
      </div>

      {/* Screenshot Modal */}
      <ScreenshotModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleScreenshotSubmit}
      />
    </>
  );
}
