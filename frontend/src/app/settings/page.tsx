'use client';

import React, { useState } from 'react';
import { Card, Button, Input, Select, Badge } from '@/components/common';
import { Save, Settings as SettingsIcon } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    email: 'user@example.com',
    theme: 'dark',
    notificationsEmail: true,
    notificationsPush: true,
    notificationsTrades: true,
    notificationsAlerts: true,
    autoTrading: true,
    riskLimit: '2',
    positionLimit: '10',
    rebalanceFrequency: 'weekly',
    timeZone: 'EST',
    twoFactorAuth: true,
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-2">Manage your account and platform preferences</p>
      </div>

      {/* Account Settings */}
      <Card title="Account Settings" subtitle="Manage your account information">
        <div className="space-y-4">
          <Input
            label="Email Address"
            value={settings.email}
            onChange={(e) => setSettings({ ...settings, email: e.target.value })}
            type="email"
          />
          <Select
            label="Time Zone"
            options={[
              { value: 'EST', label: 'Eastern Standard Time' },
              { value: 'CST', label: 'Central Standard Time' },
              { value: 'MST', label: 'Mountain Standard Time' },
              { value: 'PST', label: 'Pacific Standard Time' },
            ]}
            value={settings.timeZone}
            onChange={(e) => setSettings({ ...settings, timeZone: e.target.value })}
          />
          <Button variant="primary" className="w-full">
            Change Password
          </Button>
        </div>
      </Card>

      {/* Notification Settings */}
      <Card title="Notification Settings" subtitle="Control how you receive updates">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="font-semibold text-white">Email Notifications</p>
              <p className="text-sm text-gray-400">Receive updates via email</p>
            </div>
            <input
              type="checkbox"
              checked={settings.notificationsEmail}
              onChange={(e) =>
                setSettings({ ...settings, notificationsEmail: e.target.checked })
              }
              className="w-5 h-5"
            />
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="font-semibold text-white">Trade Notifications</p>
              <p className="text-sm text-gray-400">Alert when trades are executed</p>
            </div>
            <input
              type="checkbox"
              checked={settings.notificationsTrades}
              onChange={(e) =>
                setSettings({ ...settings, notificationsTrades: e.target.checked })
              }
              className="w-5 h-5"
            />
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="font-semibold text-white">Risk Alerts</p>
              <p className="text-sm text-gray-400">Alert on portfolio risk events</p>
            </div>
            <input
              type="checkbox"
              checked={settings.notificationsAlerts}
              onChange={(e) =>
                setSettings({ ...settings, notificationsAlerts: e.target.checked })
              }
              className="w-5 h-5"
            />
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="font-semibold text-white">Push Notifications</p>
              <p className="text-sm text-gray-400">Push notifications on mobile</p>
            </div>
            <input
              type="checkbox"
              checked={settings.notificationsPush}
              onChange={(e) =>
                setSettings({ ...settings, notificationsPush: e.target.checked })
              }
              className="w-5 h-5"
            />
          </div>
        </div>
      </Card>

      {/* Trading Settings */}
      <Card title="Trading & Risk Settings" subtitle="Control trading parameters">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="font-semibold text-white">Autonomous Trading</p>
              <p className="text-sm text-gray-400">Allow agents to execute trades automatically</p>
            </div>
            <input
              type="checkbox"
              checked={settings.autoTrading}
              onChange={(e) =>
                setSettings({ ...settings, autoTrading: e.target.checked })
              }
              className="w-5 h-5"
            />
          </div>

          <Input
            label="Daily VaR Limit (%)"
            type="number"
            value={settings.riskLimit}
            onChange={(e) => setSettings({ ...settings, riskLimit: e.target.value })}
          />

          <Input
            label="Maximum Position Size (%)"
            type="number"
            value={settings.positionLimit}
            onChange={(e) => setSettings({ ...settings, positionLimit: e.target.value })}
          />

          <Select
            label="Rebalancing Frequency"
            options={[
              { value: 'daily', label: 'Daily' },
              { value: 'weekly', label: 'Weekly' },
              { value: 'monthly', label: 'Monthly' },
              { value: 'quarterly', label: 'Quarterly' },
              { value: 'manual', label: 'Manual Only' },
            ]}
            value={settings.rebalanceFrequency}
            onChange={(e) =>
              setSettings({ ...settings, rebalanceFrequency: e.target.value })
            }
          />
        </div>
      </Card>

      {/* Security Settings */}
      <Card title="Security Settings" subtitle="Manage your security preferences">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="font-semibold text-white">Two-Factor Authentication</p>
              <p className="text-sm text-gray-400">
                {settings.twoFactorAuth ? 'Enabled' : 'Disabled'}
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.twoFactorAuth}
              onChange={(e) =>
                setSettings({ ...settings, twoFactorAuth: e.target.checked })
              }
              className="w-5 h-5"
            />
          </div>

          <Button variant="secondary" className="w-full">
            Manage API Keys
          </Button>

          <Button variant="secondary" className="w-full">
            View Login History
          </Button>
        </div>
      </Card>

      {/* Integration Settings */}
      <Card title="Integrations" subtitle="Connect external services">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { name: 'Interactive Brokers', connected: true },
            { name: 'Bloomberg Terminal', connected: false },
            { name: 'Trading View', connected: true },
            { name: 'Email Service', connected: true },
          ].map((integration, idx) => (
            <div key={idx} className="p-4 bg-gray-700 rounded-lg border border-gray-600">
              <div className="flex items-center justify-between">
                <p className="font-semibold text-white">{integration.name}</p>
                <Badge
                  label={integration.connected ? 'Connected' : 'Disconnected'}
                  variant={integration.connected ? 'success' : 'default'}
                  size="sm"
                />
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="w-full mt-3"
              >
                {integration.connected ? 'Disconnect' : 'Connect'}
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* API Documentation */}
      <Card title="API Documentation" subtitle="Integrate with external systems">
        <div className="space-y-3">
          <p className="text-gray-300">
            Access the API documentation to build custom integrations:
          </p>
          <Button variant="primary" className="w-full">
            View API Documentation
          </Button>
          <Button variant="secondary" className="w-full">
            Generate API Key
          </Button>
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex gap-3 sticky bottom-6">
        <Button variant="primary" size="lg" onClick={handleSave} className="flex-1">
          <Save size={20} className="mr-2" />
          Save Changes
        </Button>
        {saved && (
          <div className="fixed bottom-6 right-6 bg-green-500 text-white px-4 py-2 rounded-lg">
            ✓ Settings saved successfully
          </div>
        )}
      </div>
    </div>
  );
}
