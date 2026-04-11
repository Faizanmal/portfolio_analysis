'use client';

import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Card, Stat, Button, Badge } from '@/components/common';
import { api } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { formatCurrency, formatPercent } from '@/lib/utils';
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import Link from 'next/link';

// Mock data for charts
const mockPerformanceData = [
  { date: 'Jan 1', value: 100000 },
  { date: 'Jan 8', value: 102500 },
  { date: 'Jan 15', value: 100800 },
  { date: 'Jan 22', value: 105200 },
  { date: 'Jan 29', value: 107500 },
  { date: 'Feb 5', value: 106200 },
  { date: 'Feb 12', value: 109800 },
  { date: 'Feb 19', value: 112300 },
  { date: 'Feb 26', value: 111500 },
];

const mockAgentActivity = [
  { name: '12 AM', trades: 2, decisions: 5 },
  { name: '4 AM', trades: 1, decisions: 3 },
  { name: '8 AM', trades: 5, decisions: 12 },
  { name: '12 PM', trades: 8, decisions: 18 },
  { name: '4 PM', trades: 6, decisions: 15 },
  { name: '8 PM', trades: 3, decisions: 8 },
];

const recentAlerts = [
  { id: 1, type: 'warning', title: 'High Volatility Detected', message: 'Market volatility increased 15%' },
  { id: 2, type: 'success', title: 'Trade Executed', message: 'Successfully bought 100 shares of AAPL' },
  { id: 3, type: 'info', title: 'Portfolio Rebalanced', message: 'Portfolio rebalanced to target allocation' },
  { id: 4, type: 'warning', title: 'Risk Alert', message: 'VaR exceeded threshold by 2%' },
];

const recentTrades = [
  { id: 1, symbol: 'AAPL', action: 'BUY', quantity: 100, price: 150.25, total: 15025, time: '2 hours ago' },
  { id: 2, symbol: 'MSFT', action: 'SELL', quantity: 50, price: 380.50, total: 19025, time: '3 hours ago' },
  { id: 3, symbol: 'GOOGL', action: 'BUY', quantity: 20, price: 140.75, total: 2815, time: '5 hours ago' },
  { id: 4, symbol: 'TSLA', action: 'BUY', quantity: 30, price: 240.30, total: 7209, time: '1 day ago' },
];

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolioData] = useState({
    totalValue: 512750,
    cash: 25000,
    dailyReturn: 2.5,
    ytdReturn: 12.8,
  });
  const [risk, setRiskData] = useState({
    var95: 0.85,
    sharpeRatio: 1.45,
    maxDrawdown: -5.2,
  });
  const [agents, setAgentsData] = useState({
    active: 5,
    pendingDecisions: 3,
    successRate: 0.87,
  });

  const { addAlert } = useAppStore();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setTimeout(() => {
          setLoading(false);
          addAlert({
            type: 'success',
            title: 'Dashboard Loaded',
            message: 'All systems operational',
          });
        }, 1000);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
        addAlert({
          type: 'error',
          title: 'Load Failed',
          message: 'Failed to load dashboard data',
        });
      }
    };

    fetchData();
  }, [addAlert]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-gray-400">Welcome to your AI-powered portfolio management system</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary">Export Report</Button>
          <Button variant="primary">Run Analysis</Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat
          label="Portfolio Value"
          value={formatCurrency(portfolio.totalValue)}
          change={portfolio.dailyReturn}
          changeLabel="Today"
          icon="💼"
        />
        <Stat
          label="Daily Return"
          value={formatPercent(portfolio.dailyReturn / 100)}
          change={portfolio.dailyReturn}
          changeLabel="vs Yesterday"
          icon="📈"
        />
        <Stat
          label="YTD Return"
          value={formatPercent(portfolio.ytdReturn / 100)}
          change={12.8}
          changeLabel="vs Last Year"
          icon="📊"
        />
        <Stat
          label="Cash Available"
          value={formatCurrency(portfolio.cash)}
          change={5}
          changeLabel="Available"
          icon="💰"
        />
      </div>

      {/* Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="Risk Metrics">
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Value at Risk (95%)</span>
                <span className="text-sm font-semibold text-white">{risk.var95}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-red-500 h-2 rounded-full" style={{ width: '15%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Sharpe Ratio</span>
                <span className="text-sm font-semibold text-green-400">{risk.sharpeRatio}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '72%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Max Drawdown</span>
                <span className="text-sm font-semibold text-red-400">{risk.maxDrawdown}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-red-500 h-2 rounded-full" style={{ width: '26%' }} />
              </div>
            </div>
          </div>
        </Card>

        <Card title="Agent Status">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Active Agents</span>
              <Badge label={`${agents.active}/6`} variant="success" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Pending Decisions</span>
              <Badge label={agents.pendingDecisions} variant="info" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Success Rate</span>
              <Badge label={`${(agents.successRate * 100).toFixed(0)}%`} variant="success" />
            </div>
            <Link href="/agents">
              <Button variant="ghost" className="w-full mt-4">
                View Agents →
              </Button>
            </Link>
          </div>
        </Card>

        <Card title="System Status">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <CheckCircle size={18} className="text-green-400" />
              <span className="text-sm text-gray-300">All Systems Operational</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle size={18} className="text-green-400" />
              <span className="text-sm text-gray-300">Data Connection Active</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock size={18} className="text-yellow-400" />
              <span className="text-sm text-gray-300">Auto-rebalance in 4d 3h</span>
            </div>
            <Link href="/settings">
              <Button variant="ghost" className="w-full mt-4">
                Settings →
              </Button>
            </Link>
          </div>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Portfolio Performance */}
        <Card title="Portfolio Performance" subtitle="Last 30 days">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockPerformanceData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#3b82f6"
                  fillOpacity={1}
                  fill="url(#colorValue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Agent Activity */}
        <Card title="Agent Trading Activity" subtitle="Last 24 hours">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockAgentActivity}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Bar dataKey="trades" fill="#3b82f6" name="Trades" />
                <Bar dataKey="decisions" fill="#10b981" name="Decisions" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Alerts */}
        <Card title="Recent Alerts" subtitle="Latest system alerts">
          <div className="space-y-3">
            {recentAlerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-start gap-3 p-3 bg-gray-700 rounded-lg border border-gray-600"
              >
                <div className="mt-1">
                  {alert.type === 'warning' && (
                    <AlertCircle size={18} className="text-yellow-400" />
                  )}
                  {alert.type === 'success' && (
                    <CheckCircle size={18} className="text-green-400" />
                  )}
                  {alert.type === 'info' && (
                    <AlertCircle size={18} className="text-blue-400" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-white text-sm">{alert.title}</p>
                  <p className="text-gray-400 text-xs mt-1">{alert.message}</p>
                </div>
              </div>
            ))}
            <Link href="/alerts">
              <Button variant="ghost" className="w-full">
                View All Alerts →
              </Button>
            </Link>
          </div>
        </Card>

        {/* Recent Trades */}
        <Card title="Recent Trades" subtitle="Latest executed trades">
          <div className="space-y-3">
            {recentTrades.map((trade) => (
              <div
                key={trade.id}
                className="flex items-center justify-between p-3 bg-gray-700 rounded-lg border border-gray-600"
              >
                <div>
                  <p className="font-semibold text-white">
                    {trade.action === 'BUY' ? '📈' : '📉'} {trade.symbol}
                  </p>
                  <p className="text-gray-400 text-xs mt-1">
                    {trade.quantity} units @ {trade.price}
                  </p>
                  <p className="text-gray-500 text-xs">{trade.time}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-white">
                    {formatCurrency(trade.total)}
                  </p>
                  <Badge
                    label={trade.action}
                    variant={trade.action === 'BUY' ? 'success' : 'danger'}
                    size="sm"
                  />
                </div>
              </div>
            ))}
            <Link href="/trading">
              <Button variant="ghost" className="w-full">
                View Trading →
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
