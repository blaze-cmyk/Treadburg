import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MoreHorizontal } from 'lucide-react';
import { ChartConfig } from '../types';

export const ChartWidget = ({ data }: { data: ChartConfig }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(600);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  
  const height = 320;
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };

  useEffect(() => {
    if (containerRef.current) {
      setWidth(containerRef.current.offsetWidth);
      const resizeObserver = new ResizeObserver((entries) => {
        for (let entry of entries) {
           setWidth(entry.contentRect.width);
        }
      });
      resizeObserver.observe(containerRef.current);
      return () => resizeObserver.disconnect();
    }
  }, []);

  const allValues = data.series.flatMap(s => s.data);
  const maxValue = Math.max(...allValues.filter(v => v !== null)) || 100;
  const minValue = Math.min(...allValues.filter(v => v !== null)) || 0;
  
  const yMax = maxValue > 0 ? maxValue * 1.2 : 0; 
  const yMin = data.type === 'bar' && minValue >= 0 ? 0 : Math.min(0, minValue * 1.2);
  
  const getX = (index: number) => {
    const usableWidth = width - padding.left - padding.right;
    if (data.labels.length === 1 && data.type === 'bar') {
        return padding.left + usableWidth / 2;
    }
    return padding.left + (index / (data.labels.length - 1 || 1)) * usableWidth;
  };

  const getY = (value: number) => {
    const usableHeight = height - padding.top - padding.bottom;
    const range = yMax - yMin;
    if (range === 0) return height - padding.bottom;
    const ratio = (value - yMin) / range;
    return height - padding.bottom - (ratio * usableHeight);
  };

  const getLinePath = (values: number[]) => {
    if (values.length === 0) return "";
    let path = `M ${getX(0)} ${getY(values[0])}`;
    for (let i = 0; i < values.length - 1; i++) {
        const x0 = getX(i);
        const y0 = getY(values[i]);
        const x1 = getX(i + 1);
        const y1 = getY(values[i + 1]);
        const cpX1 = x0 + (x1 - x0) / 2;
        const cpY1 = y0;
        const cpX2 = x0 + (x1 - x0) / 2;
        const cpY2 = y1;
        path += ` C ${cpX1} ${cpY1}, ${cpX2} ${cpY2}, ${x1} ${y1}`;
    }
    return path;
  };

  const getBarLayout = (seriesIndex: number, dataIndex: number) => {
    const groupCount = data.labels.length;
    const seriesCount = data.series.length;
    const maxBarWidth = 80;

    const groupWidth = (width - padding.left - padding.right) / groupCount;
    const groupBarAreaWidth = groupWidth * 0.7; // Use 70% of group space for bars
    let barWidth = groupBarAreaWidth / seriesCount;

    if (barWidth > maxBarWidth) {
        barWidth = maxBarWidth;
    }

    const totalBarBlockWidth = barWidth * seriesCount;
    const groupPadding = (groupWidth - totalBarBlockWidth) / 2;
    
    const x = padding.left + (dataIndex * groupWidth) + groupPadding + (seriesIndex * barWidth);
    const val = data.series[seriesIndex].data[dataIndex];
    const y = getY(val);
    
    const zeroY = getY(0);
    const isNegative = val < 0;
    
    return {
        x,
        y: isNegative ? zeroY : y,
        width: barWidth,
        height: Math.abs(zeroY - y),
        r: 4
    };
  };

  const yTicks = 5;
  const yAxisTicks = Array.from({ length: yTicks }).map((_, i) => {
    const val = yMin + ((yMax - yMin) / (yTicks - 1)) * i;
    return val;
  });

  const formatValue = (val: number) => {
      if (Math.abs(val) >= 1000000000) return (val/1000000000).toFixed(1) + 'B';
      if (Math.abs(val) >= 1000000) return (val/1000000).toFixed(1) + 'M';
      if (Math.abs(val) >= 1000) return (val/1000).toFixed(1) + 'k';
      return val.toFixed(1);
  };

  if (data.type === 'arc') {
      return (
        <div className="my-6 text-center text-zinc-400 text-sm p-4 bg-black/20 rounded-lg">
          Arc chart visualization is not yet implemented.
        </div>
      )
  }

  return (
    <div ref={containerRef} className="w-full my-6 bg-[#18181b] p-6 rounded-lg border border-border select-none font-sans">
      <div className="flex justify-between items-center px-1 mb-4">
        <h3 className="text-xl font-bold text-white tracking-tight">{data.title}</h3>
        <button className="text-zinc-400 hover:text-white transition-colors"><MoreHorizontal size={20} /></button>
      </div>

      <div className="relative" onMouseLeave={() => setHoveredIndex(null)}>
        <svg width="100%" height={height} className="overflow-visible">

          {yAxisTicks.map((tick, i) => (
            <g key={i}>
              <line 
                x1={padding.left} 
                y1={getY(tick)} 
                x2={width - padding.right} 
                y2={getY(tick)} 
                stroke="#3f3f46" 
                strokeWidth="1" 
                strokeDasharray="2 2"
                opacity="0.5"
              />
              <text 
                x={padding.left - 10} 
                y={getY(tick)} 
                fill="#71717a" 
                fontSize="10" 
                textAnchor="end" 
                dy="3"
                className="font-mono font-medium"
              >
                {data.valuePrefix}{formatValue(tick)}{data.valueSuffix}
              </text>
            </g>
          ))}

          {yMin < 0 && (
               <line 
                x1={padding.left} 
                y1={getY(0)} 
                x2={width - padding.right} 
                y2={getY(0)} 
                stroke="#71717a" 
                strokeWidth="1" 
                opacity="0.5"
              />
          )}

          {data.type === 'line' && data.series.map((s, i) => {
             const path = getLinePath(s.data);
             const color = s.color || "#0ea5e9";
             return (
               <g key={i}>
                 <motion.path 
                   initial={{ pathLength: 0, opacity: 0 }}
                   animate={{ pathLength: 1, opacity: 1 }}
                   transition={{ duration: 1.5, ease: "circOut" }}
                   d={path} 
                   fill="none" 
                   stroke={color} 
                   strokeWidth="3" 
                   strokeLinecap="round" 
                   strokeLinejoin="round" 
                 />
                 {hoveredIndex !== null && s.data[hoveredIndex] !== null && (
                   <circle 
                      cx={getX(hoveredIndex)} 
                      cy={getY(s.data[hoveredIndex])} 
                      r={5}
                      fill="#18181b" 
                      stroke={color}
                      strokeWidth="2"
                   />
                 )}
               </g>
             );
          })}

          {data.type === 'bar' && data.series.map((s, i) => (
              <g key={i}>
                  {s.data.map((val, dIdx) => {
                      if (val === null) return null;
                      const layout = getBarLayout(i, dIdx);
                      return (
                          <motion.rect 
                              key={dIdx}
                              initial={{ height: 0, y: getY(0) }}
                              animate={{ height: layout.height, y: layout.y }}
                              transition={{ duration: 0.8, delay: dIdx * 0.05 }}
                              x={layout.x}
                              y={layout.y}
                              width={layout.width}
                              height={layout.height}
                              rx={layout.r}
                              fill={s.color || "#0ea5e9"}
                              opacity={hoveredIndex === dIdx || hoveredIndex === null ? 1 : 0.4}
                          />
                      );
                  })}
              </g>
          ))}

          {data.labels.map((label, i) => {
             const groupWidth = (width - padding.left - padding.right) / (data.labels.length || 1);
             const hitAreaX = padding.left + (i * groupWidth);
             const textX = hitAreaX + groupWidth / 2;

             return (
                 <g key={i}>
                      <text 
                          x={textX} 
                          y={height - 15} 
                          fill={hoveredIndex === i ? "#fff" : "#71717a"} 
                          fontSize="10" 
                          textAnchor="middle"
                          className="font-medium transition-colors"
                      >
                          {label}
                      </text>
                      
                      <rect
                          x={hitAreaX}
                          y={padding.top}
                          width={groupWidth}
                          height={height - padding.top - padding.bottom}
                          fill="transparent"
                          onMouseEnter={() => setHoveredIndex(i)}
                          style={{ cursor: 'crosshair' }}
                      />
                 </g>
             );
          })}
        </svg>

        {hoveredIndex !== null && (
           <div 
             className="absolute pointer-events-none z-20 flex flex-col gap-1.5 p-3 rounded-lg bg-[#27272a]/95 backdrop-blur border border-white/10 shadow-xl"
             style={{ 
               top: 20,
               left: Math.min(width - 150, Math.max(10, getX(hoveredIndex) - 60)),
             }}
           >
              <div className="text-[11px] font-bold text-zinc-300 mb-0.5 border-b border-white/5 pb-1">
                 {data.labels[hoveredIndex]}
              </div>
              {data.series.map((s, i) => {
                const val = s.data[hoveredIndex];
                if (val === null || val === undefined) return null;
                return (
                 <div key={i} className="flex items-center gap-3 text-[11px]">
                    <div className="w-2 h-2 rounded-sm" style={{ background: s.color || "#0ea5e9" }} />
                    <span className="text-zinc-400">{s.name}</span>
                    <span className="text-white font-mono ml-auto">
                       {data.valuePrefix}{formatValue(val)}{data.valueSuffix}
                    </span>
                 </div>
              )})}
           </div>
        )}
      </div>

      <div className="flex flex-wrap gap-x-6 gap-y-2 mt-4 px-1 justify-center">
        {data.series.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: s.color || "#0ea5e9" }}></div>
            <span className="text-xs text-zinc-400 font-medium">{s.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
