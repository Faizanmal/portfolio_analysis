'use client';

import React from 'react';
import { Menu, X, Bell, Settings, LogOut, Sun, Moon } from 'lucide-react';
import Link from 'next/link';
import { useAppStore } from '@/lib/store';
import clsx from 'clsx';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { sidebarOpen, setSidebarOpen, alerts, theme, setTheme } = useAppStore();
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
    <div className={clsx(
      "flex h-screen w-full overflow-hidden transition-colors duration-300",
      theme === 'dark' ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'
    )}>
      {/* Sidebar */}
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-40 w-64 sm:w-72 overflow-y-auto transform transition-transform duration-300 border-r',
          theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className={clsx(
          "p-6 border-b",
          theme === 'dark' ? 'border-gray-700' : 'border-gray-200'
        )}>
          <h1 className="text-2xl font-bold bg-linear-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            Portfolio AI
          </h1>
        </div>

        <nav className="mt-8 space-y-2 px-3">
          {navigationItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                theme === 'dark'
                  ? 'text-gray-300 hover:text-white hover:bg-gray-700'
                  : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
              )}
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
          className="fixed inset-0 bg-black bg-opacity-50 z-30 sm:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className={clsx(
        "flex-1 flex flex-col min-w-0 w-full overflow-hidden transition-all duration-300",
        // On desktop: account for sidebar when open
        sidebarOpen ? 'sm:ml-72' : 'sm:ml-0'
      )}>
        {/* Header */}
        <header className={clsx(
          "border-b sticky top-0 z-20 shrink-0",
          theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
        )}>
          <div className="flex items-center justify-between px-4 sm:px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className={clsx(
                  "p-2 rounded-lg transition-colors",
                  theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                )}
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
              {/* Theme Toggle */}
              <button
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className={clsx(
                  "p-2 rounded-lg transition-colors",
                  theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                )}
                title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              >
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setNotificationsOpen(!notificationsOpen)}
                  className={clsx(
                    "p-2 rounded-lg transition-colors relative",
                    theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                  )}
                >
                  <Bell size={20} />
                  {alerts.length > 0 && (
                    <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {alerts.length}
                    </span>
                  )}
                </button>

                {notificationsOpen && (
                  <div className={clsx(
                    "absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] border rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto",
                    theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
                  )}>
                    <div className={clsx(
                      "p-4 border-b",
                      theme === 'dark' ? 'border-gray-700' : 'border-gray-200'
                    )}>
                      <h3 className="font-semibold">Recent Alerts</h3>
                    </div>
                    <div className="space-y-2">
                      {alerts.slice(0, 5).map((alert) => (
                        <div
                          key={alert.id}
                          className={clsx(
                            "p-3 border-l-4 border-blue-500",
                            theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'
                          )}
                        >
                          <p className="font-medium text-sm">{alert.title}</p>
                          <p className={clsx(
                            "text-xs mt-1",
                            theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
                          )}>
                            {alert.message}
                          </p>
                        </div>
                      ))}
                      {alerts.length === 0 && (
                        <div className={clsx(
                          "p-4 text-center text-sm",
                          theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                        )}>
                          No recent alerts
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Settings */}
              <button className={clsx(
                "p-2 rounded-lg transition-colors hidden sm:block",
                theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
              )}>
                <Settings size={20} />
              </button>

              {/* Logout */}
              <button className={clsx(
                "p-2 rounded-lg transition-colors hidden sm:block",
                theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
              )}>
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
