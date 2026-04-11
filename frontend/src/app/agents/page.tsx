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
import { Card, Stat, Button, Badge, Progress } from '@/components/common';
import { Activity, AlertCircle, CheckCircle, Zap } from 'lucide-react';

const agentPerformanceData = [
  { date: '1/1', pm: 85, ra: 78, mr: 82, ta: 88, ca: 75 },
  { date: '1/8', pm: 87, ra: 80, mr: 85, ta: 90, ca: 77 },
  { date: '1/15', pm: 89, ra: 82, mr: 87, ta: 91, ca: 79 },
  { date: '1/22', pm: 86, ra: 81, mr: 84, ta: 89, ca: 81 },
  { date: '1/29', pm: 90, ra: 83, mr: 88, ta: 92, ca: 83 },
  { date: '2/5', pm: 91, ra: 85, mr: 89, ta: 93, ca: 84 },
  { date: '2/12', pm: 92, ra: 86, mr: 90, ta: 94, ca: 86 },
];

const agentActivityData = [
  { date: 'Mon', decisions: 45, trades: 12, alerts: 8 },
  { date: 'Tue', decisions: 52, trades: 15, alerts: 6 },
  { date: 'Wed', decisions: 48, trades: 13, alerts: 9 },
  { date: 'Thu', decisions: 60, trades: 18, alerts: 5 },
  { date: 'Fri', decisions: 55, trades: 16, alerts: 7 },
  { date: 'Mon', decisions: 58, trades: 17, alerts: 4 },
  { date: 'Tue', decisions: 62, trades: 19, alerts: 3 },
];

const agents = [
  {
    name: 'Portfolio Manager Agent',
    status: 'active',
    description: 'Manages portfolio allocation and rebalancing',
    successRate: 0.92,
    decisionsToday: 28,
    tradesExecuted: 12,
    lastActivity: '2 minutes ago',
    keyMetrics: { accuracy: 94, responseTime: '2.3s', trades: 234 },
  },
  {
    name: 'Risk Analyst Agent',
    status: 'active',
    description: 'Real-time risk assessment and monitoring',
    successRate: 0.86,
    decisionsToday: 156,
    tradesExecuted: 8,
    lastActivity: '1 minute ago',
    keyMetrics: { accuracy: 89, responseTime: '1.8s', alerts: 312 },
  },
  {
    name: 'Market Researcher Agent',
    status: 'active',
    description: 'Market analysis and opportunity identification',
    successRate: 0.90,
    decisionsToday: 42,
    tradesExecuted: 6,
    lastActivity: '5 minutes ago',
    keyMetrics: { accuracy: 91, responseTime: '3.2s', insights: 587 },
  },
  {
    name: 'Trading Agent',
    status: 'active',
    description: 'Autonomous trade execution and optimization',
    successRate: 0.94,
    decisionsToday: 89,
    tradesExecuted: 19,
    lastActivity: '30 seconds ago',
    keyMetrics: { accuracy: 96, responseTime: '0.8s', fills: 847 },
  },
  {
    name: 'Compliance Agent',
    status: 'active',
    description: 'Regulatory compliance and audit trail',
    successRate: 0.88,
    decisionsToday: 12,
    tradesExecuted: 0,
    lastActivity: '3 minutes ago',
    keyMetrics: { accuracy: 100, responseTime: '0.5s', violations: 0 },
  },
  {
    name: 'NLP Intelligence Agent',
    status: 'inactive',
    description: 'News analysis and sentiment processing',
    successRate: 0.85,
    decisionsToday: 0,
    tradesExecuted: 0,
    lastActivity: '1 day ago',
    keyMetrics: { accuracy: 87, responseTime: '2.1s', articles: 1245 },
  },
];

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const activeAgents = agents.filter(a => a.status === 'active').length;
  const totalDecisions = agents.reduce((sum, a) => sum + a.decisionsToday, 0);
  const totalTrades = agents.reduce((sum, a) => sum + a.tradesExecuted, 0);
  const avgSuccessRate = (agents.reduce((sum, a) => sum + a.successRate, 0) / agents.length) * 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Agent Management</h1>
        <p className="text-gray-400 mt-2">Monitor and manage AI agent performance</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat
          label="Active Agents"
          value={`${activeAgents}/6`}
          icon="🤖"
        />
        <Stat
          label="Total Decisions Today"
          value={totalDecisions}
          icon="💭"
        />
        <Stat
          label="Trades Executed"
          value={totalTrades}
          icon="📈"
        />
        <Stat
          label="Avg Success Rate"
          value={`${avgSuccessRate.toFixed(1)}%`}
          icon="✅"
        />
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agent Accuracy Trend */}
        <Card title="Agent Accuracy Trend" subtitle="Last 7 days performance">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={agentPerformanceData}>
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
                <Line type="monotone" dataKey="pm" stroke="#3b82f6" name="Portfolio Manager" />
                <Line type="monotone" dataKey="ra" stroke="#10b981" name="Risk Analyst" />
                <Line type="monotone" dataKey="mr" stroke="#f59e0b" name="Market Researcher" />
                <Line type="monotone" dataKey="ta" stroke="#8b5cf6" name="Trading Agent" />
                <Line type="monotone" dataKey="ca" stroke="#06b6d4" name="Compliance Agent" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Daily Activity */}
        <Card title="Daily Activity" subtitle="This week">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={agentActivityData}>
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
                <Bar dataKey="decisions" fill="#3b82f6" name="Decisions" />
                <Bar dataKey="trades" fill="#10b981" name="Trades" />
                <Bar dataKey="alerts" fill="#ef4444" name="Alerts" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Agents Details */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-4">Active Agents</h2>
        <div className="space-y-4">
          {agents.map((agent, idx) => (
            <Card
              key={idx}
              noPadding
              className="cursor-pointer hover:border-blue-500 transition-colors"
              onClick={() =>
                setExpandedAgent(expandedAgent === agent.name ? null : agent.name)
              }
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">🤖</div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">
                          {agent.name}
                        </h3>
                        <p className="text-sm text-gray-400 mt-1">
                          {agent.description}
                        </p>
                      </div>
                    </div>
                  </div>
                  <Badge
                    label={agent.status}
                    variant={agent.status === 'active' ? 'success' : 'default'}
                  />
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-700">
                  <div>
                    <p className="text-xs text-gray-400">Success Rate</p>
                    <p className="text-lg font-semibold text-green-400">
                      {(agent.successRate * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Decisions Today</p>
                    <p className="text-lg font-semibold text-blue-400">
                      {agent.decisionsToday}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Trades Executed</p>
                    <p className="text-lg font-semibold text-green-400">
                      {agent.tradesExecuted}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Last Activity</p>
                    <p className="text-lg font-semibold text-gray-300">
                      {agent.lastActivity}
                    </p>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedAgent === agent.name && (
                  <div className="mt-6 pt-6 border-t border-gray-700 space-y-4">
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-gray-400 mb-2">Accuracy</p>
                        <Progress
                          value={agent.keyMetrics.accuracy}
                          max={100}
                          color="blue"
                        />
                        <p className="text-xs text-gray-400 mt-2">
                          {agent.keyMetrics.accuracy}%
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-400 mb-2">Response Time</p>
                        <div className="bg-gray-700 rounded-lg p-2 text-center">
                          <p className="text-sm font-semibold text-white">
                            {agent.keyMetrics.responseTime}
                          </p>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-gray-400 mb-2">Key Metric</p>
                        <div className="bg-gray-700 rounded-lg p-2 text-center">
                          <p className="text-sm font-semibold text-white">
                            {Object.values(agent.keyMetrics)[2]}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <Button variant="primary" size="sm">
                        View Logs
                      </Button>
                      <Button variant="secondary" size="sm">
                        Pause Agent
                      </Button>
                      <Button variant="ghost" size="sm">
                        Configuration
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Agent Controls */}
      <Card title="Agent Controls" subtitle="Manage all agents">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button variant="primary" className="w-full">
            Start All Agents
          </Button>
          <Button variant="secondary" className="w-full">
            Pause All Agents
          </Button>
          <Button variant="danger" className="w-full">
            Emergency Stop
          </Button>
        </div>
      </Card>
    </div>
  );
}
