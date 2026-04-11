'use client';

import React, { useState } from 'react';
import { Card, Button, Badge, Input } from '@/components/common';
import { Trash2, Filter, Search } from 'lucide-react';

const allAlerts = [
  { id: 1, type: 'warning', title: 'High Volatility Detected', message: 'Market volatility increased 15% in last hour', time: '2 minutes ago', read: false },
  { id: 2, type: 'success', title: 'Trade Executed', message: 'Successfully executed BUY order: 100 AAPL @ $150.25', time: '5 minutes ago', read: false },
  { id: 3, type: 'info', title: 'Portfolio Rebalanced', message: 'Portfolio has been rebalanced to target allocation', time: '1 hour ago', read: false },
  { id: 4, type: 'warning', title: 'Risk Alert', message: 'Portfolio VaR has exceeded threshold by 2%', time: '2 hours ago', read: true },
  { id: 5, type: 'danger', title: 'Kill Switch Triggered', message: 'Volatility spike detected: Kill switch activated for position protection', time: '3 hours ago', read: true },
  { id: 6, type: 'success', title: 'Agent Decision', message: 'Portfolio Manager recommended rebalancing action', time: '4 hours ago', read: true },
  { id: 7, type: 'info', title: 'Market Update', message: 'Fed announces new interest rate decision', time: '5 hours ago', read: true },
  { id: 8, type: 'warning', title: 'Correlation Breach', message: 'Detected unusual correlation between assets', time: '6 hours ago', read: true },
];

export default function AlertsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string | null>(null);
  const [alerts, setAlerts] = useState(allAlerts);

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSearch = alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.message.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType ? alert.type === filterType : true;
    return matchesSearch && matchesType;
  });

  const handleDelete = (id: number) => {
    setAlerts(alerts.filter((a) => a.id !== id));
  };

  const handleMarkAsRead = (id: number) => {
    setAlerts(
      alerts.map((a) => (a.id === id ? { ...a, read: true } : a))
    );
  };

  const unreadCount = alerts.filter((a) => !a.read).length;

  const getAlertStyles = (type: string) => {
    switch (type) {
      case 'success':
        return 'border-l-4 border-green-500 bg-green-500 bg-opacity-10';
      case 'warning':
        return 'border-l-4 border-yellow-500 bg-yellow-500 bg-opacity-10';
      case 'danger':
        return 'border-l-4 border-red-500 bg-red-500 bg-opacity-10';
      case 'info':
        return 'border-l-4 border-blue-500 bg-blue-500 bg-opacity-10';
      default:
        return 'border-l-4 border-gray-500 bg-gray-500 bg-opacity-10';
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-400';
      case 'warning':
        return 'text-yellow-400';
      case 'danger':
        return 'text-red-400';
      case 'info':
        return 'text-blue-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Alerts</h1>
          <p className="text-gray-400 mt-2">
            {unreadCount} unread alerts • {alerts.length} total
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={() => setAlerts(alerts.map((a) => ({ ...a, read: true })))}
        >
          Mark All as Read
        </Button>
      </div>

      {/* Search and Filter */}
      <Card>
        <div className="flex gap-4 flex-col md:flex-row">
          <div className="flex-1">
            <Input
              placeholder="Search alerts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              icon={<Search size={20} />}
            />
          </div>
          <div className="flex gap-2 flex-wrap md:flex-nowrap">
            <button
              onClick={() => setFilterType(null)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filterType === null
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              All
            </button>
            {['success', 'warning', 'danger', 'info'].map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-4 py-2 rounded-lg transition-colors capitalize ${
                  filterType === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts.length > 0 ? (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg flex items-start justify-between ${getAlertStyles(
                alert.type
              )} ${!alert.read ? 'border border-opacity-100' : 'opacity-75'}`}
            >
              <div className="flex-1 flex items-start gap-4">
                <div className={`text-2xl mt-1 ${getAlertColor(alert.type)}`}>
                  {alert.type === 'success' && '✓'}
                  {alert.type === 'warning' && '⚠'}
                  {alert.type === 'danger' && '✕'}
                  {alert.type === 'info' && 'ℹ'}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className={`font-semibold ${!alert.read ? 'text-white' : 'text-gray-300'}`}>
                      {alert.title}
                    </p>
                    {!alert.read && (
                      <div className="w-2 h-2 bg-blue-400 rounded-full" />
                    )}
                  </div>
                  <p className="text-sm text-gray-400 mt-1">{alert.message}</p>
                  <p className="text-xs text-gray-500 mt-2">{alert.time}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {!alert.read && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleMarkAsRead(alert.id)}
                  >
                    Mark as read
                  </Button>
                )}
                <button
                  onClick={() => handleDelete(alert.id)}
                  className="p-2 hover:bg-red-500 hover:bg-opacity-20 rounded transition-colors"
                >
                  <Trash2 size={18} className="text-red-400" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="p-8 text-center">
            <p className="text-gray-400">No alerts found</p>
          </div>
        )}
      </div>

      {/* Alert Statistics */}
      <Card title="Alert Statistics" subtitle="Summary of alerts by type">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-green-500 bg-opacity-10 rounded-lg border border-green-500">
            <p className="text-red-400 text-sm font-semibold">Success</p>
            <p className="text-2xl font-bold text-white mt-2">
              {alerts.filter((a) => a.type === 'success').length}
            </p>
          </div>
          <div className="p-4 bg-yellow-500 bg-opacity-10 rounded-lg border border-yellow-500">
            <p className="text-yellow-400 text-sm font-semibold">Warnings</p>
            <p className="text-2xl font-bold text-white mt-2">
              {alerts.filter((a) => a.type === 'warning').length}
            </p>
          </div>
          <div className="p-4 bg-red-500 bg-opacity-10 rounded-lg border border-red-500">
            <p className="text-red-400 text-sm font-semibold">Danger</p>
            <p className="text-2xl font-bold text-white mt-2">
              {alerts.filter((a) => a.type === 'danger').length}
            </p>
          </div>
          <div className="p-4 bg-blue-500 bg-opacity-10 rounded-lg border border-blue-500">
            <p className="text-blue-400 text-sm font-semibold">Info</p>
            <p className="text-2xl font-bold text-white mt-2">
              {alerts.filter((a) => a.type === 'info').length}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
