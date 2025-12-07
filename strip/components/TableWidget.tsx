import React from 'react';
import { TableConfig } from '../types';

export const TableWidget = ({ data }: { data: TableConfig }) => {
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
    <div className="w-full my-8 overflow-hidden rounded-2xl border border-white/10 shadow-2xl bg-black/30 backdrop-blur-xl ring-1 ring-white/5">
       {data.title && (
         <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center bg-white/5">
            <h3 className="text-sm font-semibold text-white/90">{data.title}</h3>
            <div className="flex gap-2">
                <div className="w-2 h-2 rounded-full bg-red-500/50 shadow-[0_0_5px_rgba(239,68,68,0.4)]"></div>
                <div className="w-2 h-2 rounded-full bg-yellow-500/50 shadow-[0_0_5px_rgba(234,179,8,0.4)]"></div>
                <div className="w-2 h-2 rounded-full bg-green-500/50 shadow-[0_0_5px_rgba(34,197,94,0.4)]"></div>
            </div>
         </div>
       )}
       <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
             <thead>
                <tr className="bg-black/10 border-b border-white/5">
                   {data.headers.map((h, i) => (
                      <th key={i} className={`px-6 py-4 text-[11px] font-bold uppercase tracking-wider text-zinc-300 whitespace-nowrap ${i===0 ? 'sticky left-0 bg-black/30 backdrop-blur-md z-10 border-r border-white/5' : ''}`}>
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
