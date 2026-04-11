'use client';

import React, { useState } from 'react';
import {
  PieChart,
  Pie,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Card, Stat, Button, Table, Badge, Input } from '@/components/common';
import { formatCurrency, formatPercent } from '@/lib/utils';
import { Plus, Trash2, Edit2, TrendingUp, TrendingDown } from 'lucide-react';

const sectorAllocation = [
  { name: 'Technology', value: 35, color: '#3b82f6' },
  { name: 'Finance', value: 25, color: '#10b981' },
  { name: 'Healthcare', value: 20, color: '#f59e0b' },
  { name: 'Energy', value: 12, color: '#ef4444' },
  { name: 'Consumer', value: 8, color: '#8b5cf6' },
];

const positions = [
  { symbol: 'AAPL', name: 'Apple Inc.', shares: 150, buyPrice: 120.50, currentPrice: 150.25, sector: 'Technology' },
  { symbol: 'MSFT', name: 'Microsoft Corp.', shares: 100, buyPrice: 300.00, currentPrice: 380.50, sector: 'Technology' },
  { symbol: 'JPM', name: 'JPMorgan Chase', shares: 80, buyPrice: 130.00, currentPrice: 165.30, sector: 'Finance' },
  { symbol: 'JNJ', name: 'Johnson & Johnson', shares: 120, buyPrice: 155.00, currentPrice: 158.75, sector: 'Healthcare' },
  { symbol: 'XOM', name: 'ExxonMobil', shares: 60, buyPrice: 95.00, currentPrice: 110.20, sector: 'Energy' },
];

export default function PortfolioPage() {
  const [showAddPosition, setShowAddPosition] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);

  const totalValue = positions.reduce((sum, pos) => sum + pos.shares * pos.currentPrice, 0);
  const totalCost = positions.reduce((sum, pos) => sum + pos.shares * pos.buyPrice, 0);
  const totalGainLoss = totalValue - totalCost;
  const totalGainLossPercent = (totalGainLoss / totalCost) * 100;

  const portfolioMetrics = [
    { label: 'Portfolio Value', value: formatCurrency(totalValue), icon: '💼' },
    { label: 'Total Cost Basis', value: formatCurrency(totalCost), icon: '💰' },
    { label: 'Total Gain/Loss', value: formatCurrency(totalGainLoss), icon: totalGainLoss > 0 ? '📈' : '📉' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Portfolio Management</h1>
          <p className="text-gray-400 mt-2">Manage your investment positions and allocation</p>
        </div>
        <Button variant="primary" onClick={() => setShowAddPosition(true)}>
          <Plus size={20} className="mr-2" /> Add Position
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {portfolioMetrics.map((metric, idx) => (
          <Stat
            key={idx}
            label={metric.label}
            value={metric.value}
            icon={metric.icon}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sector Allocation */}
        <Card title="Sector Allocation" subtitle="Current portfolio distribution">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sectorAllocation}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sectorAllocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Rebalance Recommendations */}
        <Card title="Rebalance Recommendations" subtitle="Optimize your portfolio">
          <div className="space-y-3">
            <div className="p-3 bg-blue-500 bg-opacity-20 rounded-lg border border-blue-500">
              <p className="text-sm text-blue-200 font-semibold">Increase Energy</p>
              <p className="text-xs text-blue-100 mt-1">Current: 12% → Target: 15%</p>
            </div>
            <div className="p-3 bg-yellow-500 bg-opacity-20 rounded-lg border border-yellow-500">
              <p className="text-sm text-yellow-200 font-semibold">Reduce Consumer</p>
              <p className="text-xs text-yellow-100 mt-1">Current: 8% → Target: 5%</p>
            </div>
            <div className="p-3 bg-green-500 bg-opacity-20 rounded-lg border border-green-500">
              <p className="text-sm text-green-200 font-semibold">Technology OK</p>
              <p className="text-xs text-green-100 mt-1">Current: 35% → Target: 35%</p>
            </div>
            <Button variant="primary" className="w-full mt-4">
              Apply Rebalance
            </Button>
          </div>
        </Card>

        {/* Performance Summary */}
        <Card title="Performance Summary" subtitle="Last 30 days">
          <div className="space-y-4">
            <div className="p-3 bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Total Return</span>
                <span className="text-lg font-semibold text-green-400">
                  +{totalGainLossPercent.toFixed(2)}%
                </span>
              </div>
            </div>
            <div className="p-3 bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Best Performer</span>
                <span className="text-lg font-semibold text-white">MSFT</span>
              </div>
              <p className="text-xs text-green-400 mt-1">+26.8%</p>
            </div>
            <div className="p-3 bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Worst Performer</span>
                <span className="text-lg font-semibold text-white">XOM</span>
              </div>
              <p className="text-xs text-orange-400 mt-1">+16.0%</p>
            </div>
            <div className="p-3 bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Volatility</span>
                <span className="text-lg font-semibold text-yellow-400">12.3%</span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Positions Table */}
      <Card title="Holdings" subtitle="Current portfolio positions">
        <Table
          columns={[
            { key: 'symbol', label: 'Symbol' },
            { key: 'name', label: 'Company' },
            { key: 'sector', label: 'Sector' },
            {
              key: 'shares',
              label: 'Shares',
              render: (value) => value.toLocaleString(),
            },
            {
              key: 'buyPrice',
              label: 'Buy Price',
              render: (value) => formatCurrency(value),
            },
            {
              key: 'currentPrice',
              label: 'Current Price',
              render: (value) => formatCurrency(value),
            },
            {
              key: 'positionValue',
              label: 'Position Value',
              render: (_value, row) => formatCurrency(row.currentPrice * row.shares),
            },
            {
              key: 'gainLoss',
              label: 'Gain/Loss',
              render: (_value, row) => {
                const gainLoss = (row.currentPrice - row.buyPrice) * row.shares;
                const gainLossPercent = ((row.currentPrice - row.buyPrice) / row.buyPrice) * 100;
                return (
                  <div className={gainLoss > 0 ? 'text-green-400' : 'text-red-400'}>
                    {gainLoss > 0 ? '+' : ''}{formatCurrency(gainLoss)}
                    <span className="text-xs ml-2">({gainLossPercent > 0 ? '+' : ''}{gainLossPercent.toFixed(2)}%)</span>
                  </div>
                );
              },
            },
            {
              key: 'actions',
              label: 'Actions',
              render: () => (
                <div className="flex gap-2">
                  <button className="p-1 hover:bg-gray-700 rounded transition-colors">
                    <Edit2 size={16} className="text-blue-400" />
                  </button>
                  <button className="p-1 hover:bg-gray-700 rounded transition-colors">
                    <Trash2 size={16} className="text-red-400" />
                  </button>
                </div>
              ),
            },
          ]}
          data={positions}
        />
      </Card>

      {/* Add Position Modal */}
      {showAddPosition && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold">Add New Position</h3>
              <button
                onClick={() => setShowAddPosition(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <div className="space-y-4">
              <Input label="Symbol" placeholder="e.g., AAPL" />
              <Input label="Number of Shares" placeholder="0" type="number" />
              <Input label="Purchase Price" placeholder="$0.00" type="number" />
              <Input label="Current Price" placeholder="$0.00" type="number" />
              <div className="flex gap-3 pt-4">
                <Button variant="secondary" className="flex-1" onClick={() => setShowAddPosition(false)}>
                  Cancel
                </Button>
                <Button variant="primary" className="flex-1">
                  Add Position
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
