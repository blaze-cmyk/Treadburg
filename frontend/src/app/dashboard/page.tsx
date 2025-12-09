"use client";

import React, { useState, useEffect } from "react";
import { useUser } from "@/contexts/UserContext";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts";

// Mock data - in production this would come from your API
const portfolioData = [
  { date: "Jan", value: 10000 },
  { date: "Feb", value: 12000 },
  { date: "Mar", value: 9800 },
  { date: "Apr", value: 11200 },
  { date: "May", value: 14500 },
  { date: "Jun", value: 18000 },
  { date: "Jul", value: 19200 },
];

const assetAllocation = [
  { name: "Stocks", value: 45 },
  { name: "Crypto", value: 30 },
  { name: "Bonds", value: 15 },
  { name: "Cash", value: 10 },
];

const recentTrades = [
  { name: "BTC", type: "Buy", amount: 0.5, value: 15000, change: 2.5 },
  { name: "AAPL", type: "Sell", amount: 10, value: 1750, change: -1.2 },
  { name: "ETH", type: "Buy", amount: 2, value: 3600, change: 4.7 },
  { name: "TSLA", type: "Buy", amount: 5, value: 920, change: 0.8 },
];

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

export default function DashboardPage() {
  const { profile, isLoading, isAuthenticated } = useUser();
  const router = useRouter();
  const [totalPortfolioValue, setTotalPortfolioValue] = useState(0);

  // Calculate total portfolio value
  useEffect(() => {
    if (portfolioData.length) {
      // Use the latest value
      setTotalPortfolioValue(portfolioData[portfolioData.length - 1].value);
    }
  }, []);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container max-w-7xl mx-auto p-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="text-right">
          <p className="text-muted-foreground">Welcome back,</p>
          <p className="text-xl font-medium">{profile?.name || "User"}</p>
        </div>
      </div>

      {/* Portfolio Value */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Portfolio Value</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <span className="text-3xl font-bold">
              ${totalPortfolioValue.toLocaleString()}
            </span>
            <span className="ml-2 text-green-500">+7.2%</span>
          </div>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={portfolioData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [`$${value}`, "Value"]} 
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#8884d8"
                  fillOpacity={1}
                  fill="url(#colorValue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Asset Allocation */}
        <Card>
          <CardHeader>
            <CardTitle>Asset Allocation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={assetAllocation}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) =>
                      `${name}: ${(percent * 100).toFixed(0)}%`
                    }
                  >
                    {assetAllocation.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value}%`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Recent Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Trading Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={recentTrades}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                  <XAxis dataKey="name" />
                  <YAxis yAxisId="left" />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip />
                  <Legend />
                  <Bar
                    yAxisId="left"
                    dataKey="value"
                    name="Value ($)"
                    fill="#8884d8"
                  />
                  <Bar
                    yAxisId="right"
                    dataKey="change"
                    name="Change (%)"
                    fill={({ change }) => (change > 0 ? "#82ca9d" : "#ff7875")}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Trades</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2 font-medium">Asset</th>
                  <th className="text-left p-2 font-medium">Type</th>
                  <th className="text-left p-2 font-medium">Amount</th>
                  <th className="text-right p-2 font-medium">Value</th>
                  <th className="text-right p-2 font-medium">Change</th>
                </tr>
              </thead>
              <tbody>
                {recentTrades.map((trade, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="p-2 font-medium">{trade.name}</td>
                    <td className={`p-2 ${
                      trade.type === "Buy" ? "text-green-500" : "text-red-500"
                    }`}>
                      {trade.type}
                    </td>
                    <td className="p-2">{trade.amount}</td>
                    <td className="p-2 text-right">${trade.value}</td>
                    <td className={`p-2 text-right ${
                      trade.change > 0 ? "text-green-500" : "text-red-500"
                    }`}>
                      {trade.change > 0 ? '+' : ''}{trade.change}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
