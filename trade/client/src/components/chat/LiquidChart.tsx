import React, { useState, useRef, useEffect } from 'react';
import { MoreHorizontal } from 'lucide-react';
import { motion } from 'framer-motion';

// --- Types ---

type SeriesData = {
    name: string;
    data: number[];
    color?: string;
};

export type ChartConfig = {
    type: 'line' | 'bar' | 'arc';
    title: string;
    labels: string[];
    series: SeriesData[];
    yAxisLabel?: string;
    valuePrefix?: string;
    valueSuffix?: string;
};

export type TableConfig = {
    headers: string[];
    rows: (string | number)[][];
    title?: string;
};

export interface ChartData {
    type: 'area' | 'bar' | 'line' | 'arc' | 'table';
    title: string;
    data?: { label: string; value: number }[];
    labels?: string[];
    series?: SeriesData[];
    headers?: string[];
    rows?: (string | number)[][];
    valuePrefix?: string;
    valueSuffix?: string;
    yAxisLabel?: string;
}

// --- Professional Financial Chart Component ---
export const LiquidChart: React.FC<{ data: ChartData }> = ({ data }) => {
    // Handle table type
    if (data.type === 'table' && data.headers && data.rows) {
        return <TableWidget data={{ headers: data.headers, rows: data.rows, title: data.title }} />;
    }

    // Convert old format to new format if needed
    const chartConfig: ChartConfig = data.series ? {
        type: data.type as 'line' | 'bar' | 'arc',
        title: data.title,
        labels: data.labels || [],
        series: data.series,
        valuePrefix: data.valuePrefix,
        valueSuffix: data.valueSuffix,
        yAxisLabel: data.yAxisLabel
    } : {
        type: data.type === 'area' ? 'line' : (data.type as 'line' | 'bar'),
        title: data.title,
        labels: data.data?.map(d => d.label) || [],
        series: [{
            name: data.title,
            data: data.data?.map(d => d.value) || [],
            color: '#0ea5e9'
        }],
        valuePrefix: data.valuePrefix,
        valueSuffix: data.valueSuffix
    };

    return <ChartWidget data={chartConfig} />;
};

// --- Chart Widget Component ---
const ChartWidget = ({ data }: { data: ChartConfig }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [width, setWidth] = useState(600);
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

    const height = 320;
    const padding = { top: 20, right: 20, bottom: 40, left: 50 };

    useEffect(() => {
        if (containerRef.current) {
            const resizeObserver = new ResizeObserver((entries) => {
                for (let entry of entries) {
                    setWidth(entry.contentRect.width);
                }
            });
            resizeObserver.observe(containerRef.current);
            return () => resizeObserver.disconnect();
        }
    }, []);

    // Flatten all data to find min/max
    const allValues = data.series.flatMap(s => s.data);
    const maxValue = Math.max(...allValues) || 100;
    const minValue = Math.min(...allValues) || 0;

    // Calculate Scales
    const yMax = maxValue * 1.1;
    const yMin = data.type === 'bar' && minValue >= 0 ? 0 : Math.min(0, minValue * 1.1);

    const getX = (index: number) => {
        const usableWidth = width - padding.left - padding.right;
        return padding.left + (index / (data.labels.length - 1 || 1)) * usableWidth;
    };

    const getY = (value: number) => {
        const usableHeight = height - padding.top - padding.bottom;
        const ratio = (value - yMin) / (yMax - yMin);
        return height - padding.bottom - (ratio * usableHeight);
    };

    // Line Chart Logic
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

    // Bar Chart Logic
    const getBarLayout = (seriesIndex: number, dataIndex: number) => {
        const groupWidth = (width - padding.left - padding.right) / data.labels.length;
        const barPadding = groupWidth * 0.2;
        const usableGroupWidth = groupWidth - barPadding;
        const barWidth = usableGroupWidth / data.series.length;

        const x = padding.left + (dataIndex * groupWidth) + (barPadding / 2) + (seriesIndex * barWidth);
        const y = getY(data.series[seriesIndex].data[dataIndex]);

        const zeroY = getY(0);
        const isNegative = data.series[seriesIndex].data[dataIndex] < 0;

        if (isNegative) {
            return {
                x,
                y: zeroY,
                width: barWidth * 0.8,
                height: y - zeroY,
                r: 0
            };
        }

        return {
            x,
            y,
            width: barWidth * 0.8,
            height: zeroY - y,
            r: 4
        };
    };

    const yTicks = 5;
    const yAxisTicks = Array.from({ length: yTicks }).map((_, i) => {
        const val = yMin + ((yMax - yMin) / (yTicks - 1)) * i;
        return val;
    });

    const formatValue = (val: number) => {
        if (Math.abs(val) >= 1000000000) return (val / 1000000000).toFixed(1) + 'B';
        if (Math.abs(val) >= 1000000) return (val / 1000000).toFixed(1) + 'M';
        if (Math.abs(val) >= 1000) return (val / 1000).toFixed(1) + 'k';
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
        <div ref={containerRef} className="w-full my-6 select-none font-sans">
            {/* Header */}
            <div className="flex justify-between items-center px-1 mb-4">
                <h3 className="text-xl font-bold text-white tracking-tight">{data.title}</h3>
                <button className="text-zinc-400 hover:text-white transition-colors"><MoreHorizontal size={20} /></button>
            </div>

            {/* Chart Area with Liquid Glass Effect */}
            <div className="relative bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6 shadow-2xl" onMouseLeave={() => setHoveredIndex(null)}>
                <svg width="100%" height={height} className="overflow-visible">

                    {/* Grid Lines */}
                    {yAxisTicks.map((tick, i) => (
                        <g key={i}>
                            <line
                                x1={padding.left}
                                y1={getY(tick)}
                                x2={width - padding.right}
                                y2={getY(tick)}
                                stroke="#3f3f46"
                                strokeWidth="1"
                                strokeDasharray="4 4"
                                opacity="0.2"
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

                    {/* Zero Line */}
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

                    {/* Render Series based on Type */}
                    {data.type === 'line' && data.series.map((s, i) => {
                        const path = getLinePath(s.data);
                        const color = s.color || "#0ea5e9";
                        return (
                            <g key={i}>
                                {/* Line Stroke */}
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
                                {/* Hover Dots */}
                                {hoveredIndex !== null && (
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

                    {/* Interaction Layer */}
                    {data.labels.map((label, i) => {
                        const groupWidth = (width - padding.left - padding.right) / data.labels.length;
                        const x = data.type === 'bar'
                            ? padding.left + (i * groupWidth)
                            : getX(i) - (width / data.labels.length / 2);

                        const w = data.type === 'bar' ? groupWidth : width / data.labels.length;

                        return (
                            <g key={i}>
                                {/* X Axis Label */}
                                <text
                                    x={padding.left + (i * ((width - padding.left - padding.right) / (data.labels.length - (data.type === 'bar' ? 0 : 1)))) + (data.type === 'bar' ? groupWidth / 2 : 0)}
                                    y={height - 15}
                                    fill={hoveredIndex === i ? "#fff" : "#71717a"}
                                    fontSize="10"
                                    textAnchor="middle"
                                    className="font-medium transition-colors"
                                >
                                    {label}
                                </text>

                                {/* Hit Area */}
                                <rect
                                    x={x}
                                    y={padding.top}
                                    width={w}
                                    height={height - padding.top - padding.bottom}
                                    fill="transparent"
                                    onMouseEnter={() => setHoveredIndex(i)}
                                    style={{ cursor: 'crosshair' }}
                                />
                            </g>
                        );
                    })}
                </svg>

                {/* Tooltip */}
                {hoveredIndex !== null && (
                    <div
                        className="absolute pointer-events-none z-20 flex flex-col gap-1.5 p-3 rounded-lg bg-[#27272a]/95 backdrop-blur border border-white/10 shadow-xl"
                        style={{
                            top: 20,
                            left: data.type === 'bar'
                                ? padding.left + (hoveredIndex * ((width - padding.left - padding.right) / data.labels.length)) + 20
                                : Math.min(width - 150, Math.max(10, getX(hoveredIndex) - 60)),
                        }}
                    >
                        <div className="text-[11px] font-bold text-zinc-300 mb-0.5 border-b border-white/5 pb-1">
                            {data.labels[hoveredIndex]}
                        </div>
                        {data.series.map((s, i) => (
                            <div key={i} className="flex items-center gap-3 text-[11px]">
                                <div className="w-2 h-2 rounded-sm" style={{ background: s.color || "#0ea5e9" }} />
                                <span className="text-zinc-400">{s.name}</span>
                                <span className="text-white font-mono ml-auto">
                                    {data.valuePrefix}{formatValue(s.data[hoveredIndex])}{data.valueSuffix}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Legend */}
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

// --- Financial Table Component ---
const TableWidget = ({ data }: { data: TableConfig }) => {
    const renderCell = (content: string | number) => {
        const str = String(content);
        const match = str.match(/^(.*?)(\s+)(\(?\[?(\d+)[\]\)]?)$/);

        if (match) {
            const [_, val, space, rawBadge, num] = match;
            return (
                <div className="flex items-center justify-end md:justify-start">
                    <span className="text-white font-medium tabular-nums tracking-tight">{val}</span>
                    <span className="ml-2 inline-flex items-center justify-center bg-white/20 text-white text-[10px] h-5 min-w-[20px] px-1.5 rounded-md font-bold shadow-sm backdrop-blur-sm border border-white/10">
                        {num}
                    </span>
                </div>
            );
        }
        return <span className="text-white font-medium tabular-nums">{str}</span>;
    };

    return (
        <div className="w-full my-8 overflow-hidden rounded-2xl border border-white/10 shadow-2xl bg-black/20 backdrop-blur-xl ring-1 ring-white/5">
            {data.title && (
                <div className="px-6 py-4 border-b border-white/5 flex justify-start items-center bg-white/5">
                    <h3 className="text-sm font-semibold text-white/90">{data.title}</h3>
                </div>
            )}
            <div className="overflow-x-auto custom-scrollbar">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-black/10 border-b border-white/5">
                            {data.headers.map((h, i) => (
                                <th key={i} className={`px-6 py-4 text-[11px] font-bold uppercase tracking-wider text-zinc-300 whitespace-nowrap ${i === 0 ? 'sticky left-0 bg-black/30 backdrop-blur-md z-10 border-r border-white/5' : ''}`}>
                                    {h}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {data.rows.map((row, idx) => (
                            <tr key={idx} className="group hover:bg-white/5 transition-colors">
                                {row.map((cell, cellIdx) => (
                                    <td key={cellIdx} className={`px-6 py-4 whitespace-nowrap ${cellIdx === 0 ? 'sticky left-0 bg-black/30 backdrop-blur-xl group-hover:bg-black/40 z-10 border-r border-white/5' : 'text-right md:text-left'}`}>
                                        {cellIdx === 0 ? (
                                            <span className="text-sm font-medium text-zinc-200 group-hover:text-white transition-colors">{cell}</span>
                                        ) : (
                                            renderCell(cell)
                                        )}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
