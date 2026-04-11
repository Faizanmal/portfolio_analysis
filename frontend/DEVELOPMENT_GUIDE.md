# Frontend Development Guide

## Architecture Overview

The frontend is built on a component-driven architecture with clear separation of concerns.

```
┌─────────────────────────────────────────┐
│         Pages (src/app/*/page.tsx)       │ User-facing features
├─────────────────────────────────────────┤
│  Components (src/components/)            │ Reusable UI components
├─────────────────────────────────────────┤
│  State Management (lib/store.ts)         │ Global application state
├─────────────────────────────────────────┤
│  API Client (lib/api.ts)                 │ Backend communication
├─────────────────────────────────────────┤
│  Utilities (lib/utils.ts)                │ Helpers and formatters
└─────────────────────────────────────────┘
```

## Component Patterns

### 1. Page Component Pattern

All pages follow this structure:

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useAppStore } from '@/lib/store';
import { api } from '@/lib/api';
import { Card, Stat, Button } from '@/components/common';

export default function MyPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const { addAlert } = useAppStore();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await api.getPortfolio();
        setData(result);
      } catch (error) {
        addAlert({
          type: 'danger',
          title: 'Error',
          message: 'Failed to load data'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [addAlert]);

  if (loading) return <div>Loading...</div>;
  if (!data) return <div>No data</div>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">My Page</h1>
      
      <Card title="Summary">
        <Stat label="Total" value={data.total} />
      </Card>
    </div>
  );
}
```

### 2. Form Component Pattern

```typescript
import { useState } from 'react';
import { Input, Select, Button } from '@/components/common';

interface FormData {
  symbol: string;
  quantity: number;
}

export default function TradeForm() {
  const [formData, setFormData] = useState<FormData>({
    symbol: '',
    quantity: 0
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'quantity' ? parseInt(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    const newErrors: Record<string, string> = {};
    if (!formData.symbol) newErrors.symbol = 'Symbol required';
    if (formData.quantity <= 0) newErrors.quantity = 'Quantity must be > 0';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Submit
    try {
      await api.executeTrade({
        symbol: formData.symbol,
        action: 'BUY',
        quantity: formData.quantity,
        order_type: 'market'
      });
      
      // Success handling
      setFormData({ symbol: '', quantity: 0 });
    } catch (error) {
      setErrors({ submit: error.message });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Symbol"
        name="symbol"
        placeholder="AAPL"
        value={formData.symbol}
        onChange={handleChange}
        error={errors.symbol}
      />
      
      <Input
        label="Quantity"
        type="number"
        name="quantity"
        value={formData.quantity}
        onChange={handleChange}
        error={errors.quantity}
      />
      
      <Button type="submit" variant="primary">
        Execute Trade
      </Button>
    </form>
  );
}
```

### 3. List/Table Component Pattern

```typescript
import { Table } from '@/components/common';

interface Item {
  id: string;
  symbol: string;
  price: number;
}

interface ListProps {
  items: Item[];
  onEdit?: (item: Item) => void;
}

export default function ItemList({ items, onEdit }: ListProps) {
  return (
    <Table
      columns={[
        { key: 'symbol', label: 'Symbol' },
        { key: 'price', label: 'Price', render: (v) => `$${v.toFixed(2)}` },
        {
          key: 'actions',
          label: 'Actions',
          render: (_, item) => (
            <button onClick={() => onEdit?.(item)} className="text-blue-500">
              Edit
            </button>
          )
        }
      ]}
      data={items}
    />
  );
}
```

## State Management Patterns

### 1. Using the Store

```typescript
import { useAppStore } from '@/lib/store';

export default function Component() {
  // Get specific state
  const { portfolio, alerts, addAlert, removeAlert } = useAppStore();

  // Add alert
  const handleAction = () => {
    addAlert({
      type: 'success',
      title: 'Success',
      message: 'Operation completed'
    });
  };

  return (
    <div>
      <p>Portfolio Value: ${portfolio.totalValue}</p>
      <button onClick={handleAction}>Action</button>
    </div>
  );
}
```

### 2. Subscribing to Store Changes

```typescript
import { useEffect } from 'react';
import { useAppStore } from '@/lib/store';

export default function Component() {
  useEffect(() => {
    // Subscribe to store changes
    const unsubscribe = useAppStore.subscribe(
      (state) => state.portfolio,
      (portfolio) => {
        console.log('Portfolio updated:', portfolio);
      }
    );

    return unsubscribe;
  }, []);

  return <div>Component</div>;
}
```

## API Integration Patterns

### 1. Simple Data Fetching

```typescript
useEffect(() => {
  const fetchData = async () => {
    try {
      const data = await api.getPortfolio();
      setData(data);
    } catch (error) {
      addAlert({
        type: 'danger',
        message: 'Failed to load'
      });
    }
  };

  fetchData();
}, [addAlert]);
```

### 2. Polling Updates

```typescript
useEffect(() => {
  const interval = setInterval(async () => {
    try {
      const data = await api.getPortfolio();
      setData(data);
    } catch (error) {
      console.error('Polling failed:', error);
    }
  }, 5000); // Poll every 5 seconds

  return () => clearInterval(interval);
}, []);
```

### 3. Refetch Pattern

```typescript
const [data, setData] = useState(null);
const [loading, setLoading] = useState(false);

const refetch = async () => {
  try {
    setLoading(true);
    const result = await api.getPortfolio();
    setData(result);
  } catch (error) {
    addAlert({ type: 'danger', message: error.message });
  } finally {
    setLoading(false);
  }
};

useEffect(() => {
  refetch();
}, []);

return (
  <div>
    {data && <div>{JSON.stringify(data)}</div>}
    <button onClick={refetch} disabled={loading}>
      {loading ? 'Loading...' : 'Refresh'}
    </button>
  </div>
);
```

## Styling Patterns

### 1. Tailwind Classes

```typescript
// Responsive design
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// Flexbox layouts
<div className="flex justify-between items-center">

// Spacing
<div className="p-4 m-2 gap-4">

// Colors
<div className="bg-blue-500 text-white hover:bg-blue-600">

// Responsive text
<h1 className="text-lg md:text-2xl lg:text-4xl">
```

### 2. Conditional Styling

```typescript
import { clsx } from 'clsx';

interface CardProps {
  variant?: 'default' | 'success' | 'danger';
}

export default function Card({ variant = 'default' }: CardProps) {
  return (
    <div
      className={clsx(
        'p-4 rounded-lg',
        {
          'bg-blue-50': variant === 'default',
          'bg-green-50': variant === 'success',
          'bg-red-50': variant === 'danger'
        }
      )}
    >
      Content
    </div>
  );
}
```

### 3. Dynamic Classes

```typescript
const getRiskColor = (level: string) => {
  const colors: Record<string, string> = {
    low: 'text-green-500',
    medium: 'text-yellow-500',
    high: 'text-red-500'
  };
  return colors[level] || 'text-gray-500';
};

<span className={getRiskColor(riskLevel)}>{riskLevel}</span>
```

## Utility Function Patterns

### 1. Formatting

```typescript
import { formatCurrency, formatPercent, formatDate } from '@/lib/utils';

// Currency
console.log(formatCurrency(1000000)); // $1,000,000.00

// Percentage
console.log(formatPercent(0.123)); // 12.30%

// Date
console.log(formatDate(new Date())); // Feb 15, 2024
```

### 2. Calculations

```typescript
import { calculatePnL, calculateSharpeRatio } from '@/lib/utils';

const pnl = calculatePnL(100000, 110000); // 10%
const sharpe = calculateSharpeRatio(returns, riskFreeRate); // 1.25
```

### 3. Debounce & Throttle

```typescript
import { debounce, throttle } from '@/lib/utils';

// Debounce - wait for user to stop typing
const debouncedSearch = debounce(async (query) => {
  const results = await api.search(query);
}, 300);

// Throttle - limit update frequency
const throttledResize = throttle(() => {
  updateLayout();
}, 100);

window.addEventListener('resize', throttledResize);
```

## Error Handling Patterns

### 1. Try-Catch with User Feedback

```typescript
try {
  const result = await api.getPortfolio();
  setData(result);
} catch (error) {
  if (error.response?.status === 401) {
    // Redirect to login
  } else if (error.response?.status === 404) {
    setError('Data not found');
  } else if (error.message === 'Network Error') {
    addAlert({ type: 'danger', message: 'Connection failed' });
  } else {
    addAlert({ type: 'danger', message: error.message });
  }
}
```

### 2. Error Boundary

Create `src/components/ErrorBoundary.tsx`:

```typescript
import React, { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-50 rounded-lg">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 3. Toast Notifications

```typescript
import { addAlert } from '@/lib/store';

// Success
addAlert({ type: 'success', title: 'Success', message: 'Done!' });

// Warning
addAlert({ type: 'warning', title: 'Warning', message: 'Be careful' });

// Error
addAlert({ type: 'danger', title: 'Error', message: 'Something failed' });

// Info
addAlert({ type: 'info', title: 'Info', message: 'FYI' });
```

## Modal/Dialog Patterns

```typescript
'use client';

import { useState } from 'react';
import { Button, Input } from '@/components/common';

export default function ModalExample() {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '' });

  const handleSubmit = () => {
    console.log('Submitted:', formData);
    setIsOpen(false);
  };

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Open Modal</Button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg w-96">
            <h2 className="text-2xl font-bold mb-4">Edit Item</h2>
            
            <Input
              label="Name"
              value={formData.name}
              onChange={(e) => setFormData({ name: e.target.value })}
            />
            
            <div className="flex gap-2 mt-6">
              <Button onClick={handleSubmit} variant="primary">
                Save
              </Button>
              <Button onClick={() => setIsOpen(false)} variant="secondary">
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
```

## Chart Patterns

### Using Recharts

```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface DataPoint {
  date: string;
  value: number;
}

interface ChartProps {
  data: DataPoint[];
}

export default function Chart({ data }: ChartProps) {
  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="value" stroke="#3b82f6" />
    </LineChart>
  );
}
```

## Testing Patterns

### Component Testing

```typescript
import { render, screen } from '@testing-library/react';
import Component from './Component';

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('handles clicks', () => {
    const handleClick = jest.fn();
    render(<Component onClick={handleClick} />);
    screen.getByRole('button').click();
    expect(handleClick).toHaveBeenCalled();
  });
});
```

### API Testing

```typescript
import { api } from '@/lib/api';

describe('API Client', () => {
  it('fetches portfolio', async () => {
    const portfolio = await api.getPortfolio();
    expect(portfolio.totalValue).toBeGreaterThan(0);
  });

  it('handles errors', async () => {
    expect(() => api.getPortfolio()).rejects.toThrow();
  });
});
```

## Performance Optimization

### 1. Memoization

```typescript
import { memo, useMemo } from 'react';

// Memoize component
const ExpensiveComponent = memo(({ data }) => {
  return <div>{data}</div>;
});

// Memoize value
const memoizedData = useMemo(() => {
  return expensiveCalculation(data);
}, [data]);
```

### 2. Code Splitting

```typescript
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <div>Loading chart...</div>
});

export default function Page() {
  return <HeavyChart />;
}
```

### 3. Image Optimization

```typescript
import Image from 'next/image';

<Image
  src="/chart.png"
  alt="Chart"
  width={600}
  height={300}
  priority={false}
/>
```

## Best Practices Checklist

- ✅ Always use 'use client' in interactive components
- ✅ Handle loading and error states
- ✅ Use TypeScript for type safety
- ✅ Add proper error boundaries
- ✅ Show user feedback with alerts
- ✅ Validate form inputs
- ✅ Use responsive design
- ✅ Optimize for performance
- ✅ Test critical paths
- ✅ Document complex logic

---

**Last Updated:** February 2024
