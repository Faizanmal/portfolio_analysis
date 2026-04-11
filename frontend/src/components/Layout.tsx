'use client';

import React from 'react';
import { Menu, X, Bell, Settings, LogOut } from 'lucide-react';
import Link from 'next/link';
import { useAppStore } from '@/lib/store';
import clsx from 'clsx';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { sidebarOpen, setSidebarOpen, alerts } = useAppStore();
  const [notificationsOpen, setNotificationsOpen] = React.useState(false);

  const navigationItems = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'Portfolio', href: '/portfolio', icon: '💼' },
    { name: 'Risk Analysis', href: '/risk-analysis', icon: '⚠️' },
    { name: 'Market Intelligence', href: '/market-intelligence', icon: '📈' },
    { name: 'Trading', href: '/trading', icon: '📉' },
    { name: 'Agents', href: '/agents', icon: '🤖' },
    { name: 'Optimization', href: '/optimization', icon: '✨' },
    { name: 'Alerts', href: '/alerts', icon: '🔔' },
    { name: 'Reports', href: '/reports', icon: '📝' },
    { name: 'Settings', href: '/settings', icon: '⚙️' },
  ];

  return (
    <div className="flex h-screen w-full bg-gray-900 text-white overflow-hidden">
      {/* Sidebar */}
      <div
        className={clsx(
          'fixed top-0 left-0 h-screen bg-gray-800 border-r border-gray-700 transition-transform duration-300 z-40 w-64 sm:w-72',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold bg-linear-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            Portfolio AI
          </h1>
        </div>

        <nav className="mt-8 space-y-2 px-3">
          {navigationItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-700 transition-colors text-gray-300 hover:text-white"
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium">{item.name}</span>
            </Link>
          ))}
        </nav>
      </div>

      {/* Overlay when sidebar is open on mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 w-full overflow-hidden">
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700 sticky top-0 z-20 shrink-0">
          <div className="flex items-center justify-between px-4 sm:px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                {sidebarOpen ? (
                  <X size={24} />
                ) : (
                  <Menu size={24} />
                )}
              </button>
              <h2 className="text-lg sm:text-xl font-semibold truncate">AI Portfolio Management</h2>
            </div>

            <div className="flex items-center gap-2 sm:gap-4">
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setNotificationsOpen(!notificationsOpen)}
                  className="p-2 hover:bg-gray-700 rounded-lg transition-colors relative"
                >
                  <Bell size={20} />
                  {alerts.length > 0 && (
                    <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {alerts.length}
                    </span>
                  )}
                </button>

                {notificationsOpen && (
                  <div className="absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
                    <div className="p-4 border-b border-gray-700">
                      <h3 className="font-semibold">Recent Alerts</h3>
                    </div>
                    <div className="space-y-2">
                      {alerts.slice(0, 5).map((alert) => (
                        <div
                          key={alert.id}
                          className="p-3 border-l-4 border-blue-500 bg-gray-700"
                        >
                          <p className="font-medium text-sm">{alert.title}</p>
                          <p className="text-xs text-gray-400 mt-1">
                            {alert.message}
                          </p>
                        </div>
                      ))}
                      {alerts.length === 0 && (
                        <div className="p-4 text-center text-gray-400 text-sm">
                          No recent alerts
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Settings */}
              <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors hidden sm:block">
                <Settings size={20} />
              </button>

              {/* Logout */}
              <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors hidden sm:block">
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-4 sm:p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
