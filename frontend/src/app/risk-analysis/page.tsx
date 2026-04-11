'use client';

import React, { useState } from 'react';
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
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, Stat, Button, Badge, Progress } from '@/components/common';
import { AlertTriangle, TrendingDown, Lock } from 'lucide-react';

const varData = [
  { date: '1/1', var95: 0.75, var99: 1.2, cvar95: 0.95 },
  { date: '1/8', var95: 0.82, var99: 1.31, cvar95: 1.05 },
  { date: '1/15', var95: 0.78, var99: 1.25, cvar95: 0.98 },
  { date: '1/22', var95: 0.85, var99: 1.35, cvar95: 1.08 },
  { date: '1/29', var95: 0.9, var99: 1.42, cvar95: 1.15 },
  { date: '2/5', var95: 0.88, var99: 1.40, cvar95: 1.12 },
  { date: '2/12', var95: 0.92, var99: 1.45, cvar95: 1.18 },
];

const drawdownData = [
  { date: '1/1', value: 0 },
  { date: '1/5', value: -1.2 },
  { date: '1/10', value: -0.5 },
  { date: '1/15', value: 1.3 },
  { date: '1/20', value: 0.8 },
  { date: '1/25', value: -2.1 },
  { date: '2/1', value: -2.5 },
  { date: '2/5', value: -1.8 },
  { date: '2/12', value: -5.2 },
];

const stressTestScenarios = [
  { name: '2008 Crisis', impact: '-45%', probability: 'Low', color: 'danger' },
  { name: 'COVID-19', impact: '-35%', probability: 'Medium', color: 'warning' },
  { name: 'Tech Crash', impact: '-28%', probability: 'Medium', color: 'warning' },
  { name: 'Rate Hike', impact: '-12%', probability: 'High', color: 'info' },
  { name: 'Market Rally', impact: '+25%', probability: 'Medium', color: 'success' },
];

const correlationMatrix = [
  { asset: 'AAPL', market: 0.92, sector: 0.85, bonds: -0.15 },
  { asset: 'MSFT', market: 0.88, sector: 0.80, bonds: -0.12 },
  { asset: 'JPM', market: 0.95, sector: 0.90, bonds: -0.25 },
  { asset: 'JNJ', market: 0.78, sector: 0.82, bonds: -0.08 },
];

const killSwitches = [
  { name: 'Portfolio VaR', status: 'Active', threshold: '2%', current: '0.85%', triggered: false },
  { name: 'Position Size', status: 'Active', threshold: '10%', current: '8.5%', triggered: false },
  { name: 'Volatility Spike', status: 'Active', threshold: '50%', current: '12.3%', triggered: false },
  { name: 'Liquidity Breach', status: 'Active', threshold: '30%', current: '5%', triggered: false },
  { name: 'Correlation Break', status: 'Active', threshold: '0.3', current: '0.15', triggered: false },
];

export default function RiskAnalysisPage() {
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Risk Analysis</h1>
        <p className="text-gray-400 mt-2">Comprehensive portfolio risk monitoring and assessment</p>
      </div>

      {/* Key Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat
          label="Value at Risk (95%)"
          value="0.85%"
          icon="⚠️"
        />
        <Stat
          label="Conditional VaR (95%)"
          value="1.15%"
          icon="⚠️"
        />
        <Stat
          label="Max Drawdown"
          value="-5.2%"
          icon="📉"
        />
        <Stat
          label="Sharpe Ratio"
          value="1.45"
          icon="📊"
        />
      </div>

      {/* VaR Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Value at Risk Trend" subtitle="Last 30 days">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={varData}>
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
                <Line type="monotone" dataKey="var95" stroke="#3b82f6" name="VaR 95%" />
                <Line type="monotone" dataKey="var99" stroke="#ef4444" name="VaR 99%" />
                <Line type="monotone" dataKey="cvar95" stroke="#f59e0b" name="CVaR 95%" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Maximum Drawdown" subtitle="Peak-to-trough decline">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={drawdownData}>
                <defs>
                  <linearGradient id="colorDD" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
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
                  stroke="#ef4444"
                  fill="url(#colorDD)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Risk Management Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stress Tests */}
        <Card title="Stress Test Scenarios" subtitle="Portfolio impact analysis">
          <div className="space-y-3">
            {stressTestScenarios.map((scenario, idx) => (
              <div
                key={idx}
                className="p-4 bg-gray-700 rounded-lg border border-gray-600 hover:border-blue-500 transition-colors cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="font-semibold text-white">{scenario.name}</p>
                    <div className="flex gap-2 mt-2">
                      <Badge
                        label={scenario.impact}
                        variant={scenario.color as any}
                        size="sm"
                      />
                      <Badge
                        label={`Prob: ${scenario.probability}`}
                        variant="default"
                        size="sm"
                      />
                    </div>
                  </div>
                  <button className="text-blue-400 hover:text-blue-300 font-semibold">
                    View Details →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Kill Switches */}
        <Card title="Risk Kill Switches" subtitle="Automated circuit breakers">
          <div className="space-y-3">
            {killSwitches.map((ks, idx) => (
              <div key={idx} className="p-3 bg-gray-700 rounded-lg border border-gray-600">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-white text-sm">{ks.name}</p>
                    <div className="flex gap-2 mt-1">
                      <span className="text-xs text-gray-400">Threshold: {ks.threshold}</span>
                      <span className="text-xs text-gray-400">Current: {ks.current}</span>
                    </div>
                  </div>
                  <Lock size={16} className="text-green-400" />
                </div>
                <Progress
                  value={parseFloat(ks.current)}
                  max={parseFloat(ks.threshold)}
                  color={ks.triggered ? 'red' : 'blue'}
                />
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Correlation Analysis */}
      <Card title="Correlation Matrix" subtitle="Asset correlation analysis">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="px-4 py-3 text-left text-gray-400 font-semibold">Asset</th>
                <th className="px-4 py-3 text-center text-gray-400 font-semibold">Market</th>
                <th className="px-4 py-3 text-center text-gray-400 font-semibold">Sector</th>
                <th className="px-4 py-3 text-center text-gray-400 font-semibold">Bonds</th>
              </tr>
            </thead>
            <tbody>
              {correlationMatrix.map((row, idx) => (
                <tr key={idx} className="border-b border-gray-600 hover:bg-gray-700">
                  <td className="px-4 py-3 text-white font-semibold">{row.asset}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-green-400">{row.market.toFixed(2)}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-green-400">{row.sector.toFixed(2)}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-red-400">{row.bonds.toFixed(2)}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Risk Actions */}
      <div className="flex gap-3">
        <Button variant="primary">Generate Risk Report</Button>
        <Button variant="secondary">Run Backtest</Button>
        <Button variant="danger">Emergency Stop Protocol</Button>
      </div>
    </div>
  );
}
