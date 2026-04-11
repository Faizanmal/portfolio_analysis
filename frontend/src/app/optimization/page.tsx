'use client';

import React, { useState } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
} from 'recharts';
import { Card, Stat, Button, Input, Select, Progress } from '@/components/common';
import { Zap } from 'lucide-react';

const efficientFrontier = [
  { risk: 5, return: 4.2 },
  { risk: 6, return: 5.1 },
  { risk: 7, return: 6.3 },
  { risk: 8, return: 7.5 },
  { risk: 9, return: 8.2 },
  { risk: 10, return: 8.8 },
  { risk: 11, return: 9.1 },
  { risk: 12, return: 9.3 },
];

const currentPortfolio = [{ risk: 8.5, return: 7.8 }];

const optimizationOptions = [
  { name: 'Sharpe Optimization', sharpe: 1.45, return: 7.8, risk: 8.5 },
  { name: 'Min Volatility', sharpe: 0.95, return: 4.2, risk: 5.0 },
  { name: 'Max Return', sharpe: 1.15, return: 9.3, risk: 12.0 },
  { name: 'Risk Parity', sharpe: 1.38, return: 7.2, risk: 8.0 },
];

const backtestResults = [
  { scenario: 'Bull Market', return: 15.2, maxDD: -3.2, sharpe: 2.1 },
  { scenario: 'Bear Market', return: -5.8, maxDD: -18.5, sharpe: -0.3 },
  { scenario: 'Sideways', return: 2.1, maxDD: -2.1, sharpe: 0.8 },
  { scenario: 'High Vol', return: 8.5, maxDD: -8.2, sharpe: 1.2 },
];

export default function OptimizationPage() {
  const [selectedStrategy, setSelectedStrategy] = useState('sharpe');
  const [targetReturn, setTargetReturn] = useState('8');
  const [maxRisk, setMaxRisk] = useState('10');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Portfolio Optimization</h1>
        <p className="text-gray-400 mt-2">Advanced portfolio rebalancing and optimization strategies</p>
      </div>

      {/* Current Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Stat label="Current Sharpe Ratio" value="1.45" icon="📊" />
        <Stat label="Expected Return" value="7.8%" icon="📈" />
        <Stat label="Portfolio Risk" value="8.5%" icon="⚠️" />
      </div>

      {/* Efficient Frontier */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Efficient Frontier" subtitle="Risk vs Return analysis">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="risk" stroke="#9ca3af" name="Risk %" />
                <YAxis stroke="#9ca3af" name="Return %" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                  cursor={{ strokeDasharray: '3 3' }}
                />
                <Scatter name="Efficient Frontier" data={efficientFrontier} fill="#3b82f6" />
                <Scatter name="Current Portfolio" data={currentPortfolio} fill="#10b981" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Optimization Options */}
        <Card title="Optimization Strategies" subtitle="Available rebalancing options">
          <div className="space-y-3">
            {optimizationOptions.map((option, idx) => (
              <div
                key={idx}
                className="p-4 bg-gray-700 rounded-lg border border-gray-600 hover:border-blue-500 transition-colors cursor-pointer"
                onClick={() => setSelectedStrategy(option.name)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-semibold text-white">{option.name}</p>
                    <div className="flex gap-4 mt-2 text-xs text-gray-400">
                      <span>Sharpe: {option.sharpe}</span>
                      <span>Return: {option.return}%</span>
                      <span>Risk: {option.risk}%</span>
                    </div>
                  </div>
                  <input
                    type="radio"
                    name="strategy"
                    checked={selectedStrategy === option.name}
                    onChange={() => setSelectedStrategy(option.name)}
                    className="mt-1"
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Optimization Controls */}
      <Card title="Optimization Parameters" subtitle="Customize optimization constraints">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <Input
            label="Target Annual Return"
            value={targetReturn}
            onChange={(e) => setTargetReturn(e.target.value)}
            placeholder="8.0"
            type="number"
          />
          <Input
            label="Maximum Portfolio Risk"
            value={maxRisk}
            onChange={(e) => setMaxRisk(e.target.value)}
            placeholder="10.0"
            type="number"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Button variant="primary">
            <Zap size={20} className="mr-2" /> Run Optimization
          </Button>
          <Button variant="secondary">View Current Allocation</Button>
        </div>
      </Card>

      {/* Backtest Results */}
      <Card title="Backtest Performance" subtitle="Strategy performance under different scenarios">
        <div className="space-y-3">
          {backtestResults.map((result, idx) => (
            <div key={idx} className="p-4 bg-gray-700 rounded-lg border border-gray-600">
              <div className="flex items-center justify-between mb-3">
                <p className="font-semibold text-white">{result.scenario}</p>
                <span className={result.return > 0 ? 'text-green-400' : 'text-red-400'}>
                  {result.return > 0 ? '+' : ''}{result.return}%
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-gray-400">Max Drawdown</p>
                  <p className={`font-semibold ${result.maxDD < -10 ? 'text-red-400' : 'text-yellow-400'}`}>
                    {result.maxDD}%
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">Sharpe Ratio</p>
                  <p className="font-semibold text-blue-400">{result.sharpe}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Recommended Changes */}
      <Card title="Recommended Rebalancing" subtitle="Changes to optimize your portfolio">
        <div className="space-y-3">
          <div className="p-4 bg-green-500 bg-opacity-10 rounded-lg border border-green-500">
            <p className="text-sm text-gray-400 mb-2">Increase Position</p>
            <p className="font-semibold text-green-400">Technology: +5%</p>
            <p className="text-xs text-gray-400 mt-1">Increase allocation to capitalize on growth</p>
          </div>
          <div className="p-4 bg-yellow-500 bg-opacity-10 rounded-lg border border-yellow-500">
            <p className="text-sm text-gray-400 mb-2">Rebalance</p>
            <p className="font-semibold text-yellow-400">Finance: -3%</p>
            <p className="text-xs text-gray-400 mt-1">Reduce concentration risk</p>
          </div>
          <div className="p-4 bg-blue-500 bg-opacity-10 rounded-lg border border-blue-500">
            <p className="text-sm text-gray-400 mb-2">Add Diversification</p>
            <p className="font-semibold text-blue-400">Healthcare: +2%</p>
            <p className="text-xs text-gray-400 mt-1">Improve sector diversification</p>
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <Button variant="primary" className="flex-1">
            Apply Recommendations
          </Button>
          <Button variant="secondary" className="flex-1">
            Save as Template
          </Button>
        </div>
      </Card>
    </div>
  );
}
