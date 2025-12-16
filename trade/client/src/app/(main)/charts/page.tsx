"use client";

import { motion } from "framer-motion";
import { TrendingUp, BarChart3, LineChart, PieChart } from "lucide-react";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";

export const dynamic = 'force-dynamic';

const mockChartData = [
  {
    id: "1",
    title: "Portfolio Performance",
    type: "line",
    description: "Track your portfolio's growth over time",
  },
  {
    id: "2",
    title: "Asset Allocation",
    type: "pie",
    description: "Visualize your investment distribution",
  },
  {
    id: "3",
    title: "Market Trends",
    type: "bar",
    description: "Analyze market movements and patterns",
  },
];

export default function ChartsPage() {
  const scrollRef = useMouseWheelScroll<HTMLDivElement>();

  return (
    <div
      ref={scrollRef}
      className="flex-1 flex flex-col h-full overflow-y-auto show-scrollbar-on-hover bg-background"
    >
      <div className="max-w-6xl mx-auto px-4 py-12 w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-2xl font-semibold text-foreground mb-2">
            Charts & Analytics
          </h1>
          <p className="text-muted-foreground">
            Visualize your trading data with interactive charts and analytics.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockChartData.map((chart, index) => {
            const Icon =
              chart.type === "line"
                ? LineChart
                : chart.type === "pie"
                  ? PieChart
                  : BarChart3;

            return (
              <motion.div
                key={chart.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="glass-strong rounded-2xl p-6 hover:scale-105 transition-transform cursor-pointer"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className="p-3 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                    <Icon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground mb-1">
                      {chart.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {chart.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
