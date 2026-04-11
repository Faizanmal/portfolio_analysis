import { create } from 'zustand';

export interface Alert {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
}

export interface PortfolioState {
  totalValue: number;
  cash: number;
  dailyReturn: number;
  ytdReturn: number;
  positions: any[];
  loading: boolean;
  error: string | null;
}

export interface RiskState {
  var95: number;
  var99: number;
  cvar95: number;
  maxDrawdown: number;
  sharpeRatio: number;
  loading: boolean;
}

export interface AgentState {
  agents: any[];
  loading: boolean;
  activeAlerts: number;
}

interface AppStore {
  // Alerts
  alerts: Alert[];
  addAlert: (alert: Omit<Alert, 'id' | 'timestamp'>) => void;
  removeAlert: (id: string) => void;
  clearAlerts: () => void;

  // Portfolio
  portfolio: PortfolioState;
  setPortfolio: (portfolio: Partial<PortfolioState>) => void;
  
  // Risk
  risk: RiskState;
  setRisk: (risk: Partial<RiskState>) => void;

  // Agents
  agents: AgentState;
  setAgents: (agents: Partial<AgentState>) => void;

  // UI State
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useAppStore = create<AppStore>((set) => ({
  // Alerts
  alerts: [],
  addAlert: (alert) =>
    set((state) => ({
      alerts: [
        ...state.alerts,
        {
          ...alert,
          id: Date.now().toString(),
          timestamp: new Date(),
        },
      ],
    })),
  removeAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.filter((alert) => alert.id !== id),
    })),
  clearAlerts: () => set({ alerts: [] }),

  // Portfolio
  portfolio: {
    totalValue: 0,
    cash: 0,
    dailyReturn: 0,
    ytdReturn: 0,
    positions: [],
    loading: false,
    error: null,
  },
  setPortfolio: (portfolio) =>
    set((state) => ({
      portfolio: { ...state.portfolio, ...portfolio },
    })),

  // Risk
  risk: {
    var95: 0,
    var99: 0,
    cvar95: 0,
    maxDrawdown: 0,
    sharpeRatio: 0,
    loading: false,
  },
  setRisk: (risk) =>
    set((state) => ({
      risk: { ...state.risk, ...risk },
    })),

  // Agents
  agents: {
    agents: [],
    loading: false,
    activeAlerts: 0,
  },
  setAgents: (agents) =>
    set((state) => ({
      agents: { ...state.agents, ...agents },
    })),

  // UI State
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  theme: 'dark',
  setTheme: (theme) => set({ theme }),
}));
