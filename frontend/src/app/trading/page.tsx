'use client';

import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, Stat, Button, Table, Badge, Input, Select } from '@/components/common';
import { DollarSign, TrendingUp, TrendingDown, Send } from 'lucide-react';

const tradeHistoryData = [
  { date: '1/1', buys: 5, sells: 3, totalVolume: 250000 },
  { date: '1/5', buys: 8, sells: 4, totalVolume: 320000 },
  { date: '1/10', buys: 6, sells: 5, totalVolume: 280000 },
  { date: '1/15', buys: 9, sells: 6, totalVolume: 380000 },
  { date: '1/20', buys: 7, sells: 4, totalVolume: 300000 },
  { date: '1/25', buys: 10, sells: 7, totalVolume: 420000 },
  { date: '2/1', buys: 8, sells: 5, totalVolume: 350000 },
];

const tradeHistory = [
  { id: 1, orderType: 'BUY', symbol: 'AAPL', shares: 100, price: 150.25, total: 15025, status: 'Executed', time: '2/12 2:45 PM', agent: 'Portfolio Manager' },
  { id: 2, orderType: 'SELL', symbol: 'MSFT', shares: 50, price: 380.50, total: 19025, status: 'Executed', time: '2/12 1:30 PM', agent: 'Risk Analyst' },
  { id: 3, orderType: 'BUY', symbol: 'GOOGL', shares: 20, price: 140.75, total: 2815, status: 'Executed', time: '2/12 11:20 AM', agent: 'Market Researcher' },
  { id: 4, orderType: 'BUY', symbol: 'TSLA', shares: 30, price: 240.30, total: 7209, status: 'Pending', time: '2/12 9:15 AM', agent: 'Trading Agent' },
  { id: 5, orderType: 'SELL', symbol: 'AMZN', shares: 40, price: 175.60, total: 7024, status: 'Executed', time: '2/11 3:50 PM', agent: 'Portfolio Manager' },
];

const recommendedTrades = [
  { symbol: 'NVDA', action: 'BUY', reason: 'Oversold', confidence: 0.85, targetPrice: 825.50 },
  { symbol: 'META', action: 'SELL', reason: 'Overbought', confidence: 0.78, targetPrice: 500.00 },
  { symbol: 'ADBE', action: 'BUY', reason: 'Undervalued', confidence: 0.92, targetPrice: 650.00 },
];

export default function TradingPage() {
  const [selectedOrder, setSelectedOrder] = useState<number | null>(null);
  const [showExecuteForm, setShowExecuteForm] = useState(false);
  const [formData, setFormData] = useState({
    symbol: '',
    action: 'BUY',
    quantity: '',
    orderType: 'MARKET',
    price: '',
  });

  const totalExecuted = tradeHistory.filter(t => t.status === 'Executed').length;
  const totalPending = tradeHistory.filter(t => t.status === 'Pending').length;
  const totalVolume = tradeHistory.reduce((sum, t) => sum + t.total, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Trading Management</h1>
          <p className="text-gray-400 mt-2">Execute and monitor trades across your portfolio</p>
        </div>
        <Button variant="primary" onClick={() => setShowExecuteForm(true)}>
          <Send size={20} className="mr-2" /> Execute Trade
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat
          label="Total Executed"
          value={totalExecuted}
          icon="✅"
        />
        <Stat
          label="Pending Orders"
          value={totalPending}
          icon="⏳"
        />
        <Stat
          label="Total Volume"
          value={`$${(totalVolume / 1000).toFixed(1)}K`}
          icon="💱"
        />
        <Stat
          label="Success Rate"
          value="98.5%"
          icon="📊"
        />
      </div>

      {/* Trading Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Buy/Sell Volume */}
        <Card title="Trading Volume" subtitle="Last 30 days">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tradeHistoryData}>
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
                <Legend />
                <Bar dataKey="buys" fill="#10b981" name="Buy Orders" />
                <Bar dataKey="sells" fill="#ef4444" name="Sell Orders" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Trade Performance */}
        <Card title="Trade Performance" subtitle="PnL by execution">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={tradeHistoryData}>
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
                <Line
                  type="monotone"
                  dataKey="totalVolume"
                  stroke="#3b82f6"
                  name="Volume"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* AI Recommended Trades */}
      <Card title="AI Recommended Trades" subtitle="Based on market analysis">
        <div className="space-y-3">
          {recommendedTrades.map((trade, idx) => (
            <div
              key={idx}
              className="p-4 bg-gray-700 rounded-lg border border-gray-600 flex items-center justify-between hover:border-blue-500 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <div>
                    <p className="font-semibold text-white">{trade.symbol}</p>
                    <p className="text-xs text-gray-400 mt-1">{trade.reason}</p>
                  </div>
                  <Badge
                    label={trade.action}
                    variant={trade.action === 'BUY' ? 'success' : 'danger'}
                  />
                </div>
              </div>
              <div className="text-right mr-4">
                <p className="text-sm text-gray-400">Target Price</p>
                <p className="font-semibold text-white">${trade.targetPrice.toFixed(2)}</p>
                <p className="text-xs text-gray-400">Confidence: {(trade.confidence * 100).toFixed(0)}%</p>
              </div>
              <Button variant="primary" size="sm">
                Execute
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Trade History */}
      <Card title="Trade History" subtitle="Recent executions">
        <Table
          columns={[
            {
              key: 'orderType',
              label: 'Type',
              render: (value) => (
                <Badge
                  label={value}
                  variant={value === 'BUY' ? 'success' : 'danger'}
                />
              ),
            },
            { key: 'symbol', label: 'Symbol' },
            {
              key: 'shares',
              label: 'Shares',
              render: (value) => value.toLocaleString(),
            },
            {
              key: 'price',
              label: 'Price',
              render: (value) => `$${value.toFixed(2)}`,
            },
            {
              key: 'total',
              label: 'Total',
              render: (value) => `$${(value / 1000).toFixed(2)}K`,
            },
            { key: 'agent', label: 'Agent' },
            {
              key: 'status',
              label: 'Status',
              render: (value) => (
                <Badge
                  label={value}
                  variant={value === 'Executed' ? 'success' : 'info'}
                />
              ),
            },
            { key: 'time', label: 'Time' },
          ]}
          data={tradeHistory}
        />
      </Card>

      {/* Execute Trade Modal */}
      {showExecuteForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold">Execute Trade</h3>
              <button
                onClick={() => setShowExecuteForm(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <form className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Symbol"
                  placeholder="e.g., AAPL"
                  value={formData.symbol}
                  onChange={(e) =>
                    setFormData({ ...formData, symbol: e.target.value })
                  }
                />
                <Select
                  label="Action"
                  options={[
                    { value: 'BUY', label: 'Buy' },
                    { value: 'SELL', label: 'Sell' },
                  ]}
                  value={formData.action}
                  onChange={(e) =>
                    setFormData({ ...formData, action: e.target.value })
                  }
                />
              </div>

              <Input
                label="Quantity"
                placeholder="0"
                type="number"
                value={formData.quantity}
                onChange={(e) =>
                  setFormData({ ...formData, quantity: e.target.value })
                }
              />

              <Select
                label="Order Type"
                options={[
                  { value: 'MARKET', label: 'Market' },
                  { value: 'LIMIT', label: 'Limit' },
                ]}
                value={formData.orderType}
                onChange={(e) =>
                  setFormData({ ...formData, orderType: e.target.value })
                }
              />

              {formData.orderType === 'LIMIT' && (
                <Input
                  label="Limit Price"
                  placeholder="$0.00"
                  type="number"
                  value={formData.price}
                  onChange={(e) =>
                    setFormData({ ...formData, price: e.target.value })
                  }
                />
              )}

              <div className="pt-4 flex gap-3">
                <Button
                  variant="secondary"
                  className="flex-1"
                  onClick={() => setShowExecuteForm(false)}
                >
                  Cancel
                </Button>
                <Button variant="primary" className="flex-1">
                  Execute Trade
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
