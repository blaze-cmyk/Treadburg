import React from 'react';
import {
    AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

export interface ChartData {
    type: 'area' | 'bar';
    title: string;
    data: { label: string; value: number }[];
    valuePrefix?: string;
    valueSuffix?: string;
}

interface LiquidChartProps {
    data: ChartData;
}

export const LiquidChart: React.FC<LiquidChartProps> = ({ data }) => {
    const isArea = data.type === 'area';
    const color = '#22B5A3'; // TradeBerg Teal

    const formatValue = (val: number) =>
        `${data.valuePrefix || ''}${val.toLocaleString()}${data.valueSuffix || ''}`;

    return (
        <div className="w-full my-6 glass-panel rounded-xl overflow-hidden animate-in fade-in zoom-in-95 duration-700 border border-white/5 bg-[#1e1e1e]/50">
            <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-200 tracking-wide uppercase font-display">
                    {data.title}
                </h3>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-[#22B5A3] animate-pulse"></div>
                    <span className="text-xs text-gray-500 font-mono">LIVE DATA</span>
                </div>
            </div>

            <div className="w-full h-[280px] p-4">
                <ResponsiveContainer width="100%" height="100%">
                    {isArea ? (
                        <AreaChart data={data.data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={color} stopOpacity={0.4} />
                                    <stop offset="95%" stopColor={color} stopOpacity={0.0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                            <XAxis
                                dataKey="label"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#8D9191', fontSize: 11 }}
                                dy={10}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#8D9191', fontSize: 11 }}
                                tickFormatter={(val) => `${val}`}
                                width={40}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(32, 34, 34, 0.9)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                    boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                                    color: '#fff'
                                }}
                                itemStyle={{ color: '#fff' }}
                                cursor={{ stroke: 'rgba(255,255,255,0.2)', strokeWidth: 1 }}
                                formatter={(value: number) => [formatValue(value), '']}
                            />
                            <Area
                                type="monotone"
                                dataKey="value"
                                stroke={color}
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#colorValue)"
                                activeDot={{ r: 6, strokeWidth: 0, fill: '#fff' }}
                            />
                        </AreaChart>
                    ) : (
                        <BarChart data={data.data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                            <XAxis
                                dataKey="label"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#8D9191', fontSize: 11 }}
                                dy={10}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#8D9191', fontSize: 11 }}
                                width={40}
                            />
                            <Tooltip
                                cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                                contentStyle={{
                                    backgroundColor: 'rgba(32, 34, 34, 0.9)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                    color: '#fff'
                                }}
                                formatter={(value: number) => [formatValue(value), '']}
                            />
                            <Bar
                                dataKey="value"
                                fill={color}
                                radius={[4, 4, 0, 0]}
                                fillOpacity={0.8}
                            />
                        </BarChart>
                    )}
                </ResponsiveContainer>
            </div>
        </div>
    );
};
