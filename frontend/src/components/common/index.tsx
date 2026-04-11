import React from 'react';
import clsx from 'clsx';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  className,
  noPadding = false,
  ...props
}) => {
  return (
    <div
      className={clsx(
        'bg-gray-800 border border-gray-700 rounded-lg',
        noPadding ? '' : 'p-6',
        className
      )}
      {...props}
    >
      {title && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
        </div>
      )}
      {children}
    </div>
  );
};

interface StatProps {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  className?: string;
}

export const Stat: React.FC<StatProps> = ({
  label,
  value,
  change,
  changeLabel,
  icon,
  className,
}) => {
  const isPositive = change ? change > 0 : false;

  return (
    <div className={clsx('p-4 bg-gray-800 rounded-lg border border-gray-700', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-400 font-medium">{label}</p>
          <p className="text-2xl font-bold text-white mt-2">{value}</p>
          {change !== undefined && (
            <div className={clsx('text-sm font-semibold mt-2 flex items-center gap-1')}>
              <span
                className={clsx(
                  isPositive ? 'text-green-400' : 'text-red-400'
                )}
              >
                {isPositive ? '↑' : '↓'} {Math.abs(change).toFixed(2)}%
              </span>
              {changeLabel && (
                <span className="text-gray-400">({changeLabel})</span>
              )}
            </div>
          )}
        </div>
        {icon && (
          <div className="text-blue-400 text-2xl opacity-50">{icon}</div>
        )}
      </div>
    </div>
  );
};

interface TableProps {
  columns: Array<{
    key: string;
    label: string;
    render?: (value: any, row: any) => React.ReactNode;
  }>;
  data: any[];
  className?: string;
}

export const Table: React.FC<TableProps> = ({ columns, data, className }) => {
  return (
    <div className={clsx('overflow-x-auto w-full', className)}>
      <table className="w-full min-w-full">
        <thead>
          <tr className="border-b border-gray-700">
            {columns.map((column) => (
              <th
                key={column.key}
                className="px-3 sm:px-6 py-3 text-left text-xs sm:text-sm font-semibold text-gray-400 uppercase tracking-wider whitespace-nowrap"
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr
              key={idx}
              className="border-b border-gray-700 hover:bg-gray-700 transition-colors"
            >
              {columns.map((column) => (
                <td key={column.key} className="px-3 sm:px-6 py-4 text-xs sm:text-sm text-white">
                  {column.render
                    ? column.render(row[column.key], row)
                    : row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

interface BadgeProps {
  label: string | number;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  variant = 'default',
  size = 'md',
}) => {
  const baseClasses =
    'inline-flex items-center rounded-full font-semibold';
  const variants = {
    default: 'bg-gray-700 text-gray-200',
    success: 'bg-green-500 bg-opacity-20 text-green-400',
    warning: 'bg-yellow-500 bg-opacity-20 text-yellow-400',
    danger: 'bg-red-500 bg-opacity-20 text-red-400',
    info: 'bg-blue-500 bg-opacity-20 text-blue-400',
  };
  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size]
      )}
    >
      {label}
    </span>
  );
};

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const Button: React.FC<ButtonProps & { children: React.ReactNode }> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  children,
  className,
  disabled,
  ...props
}) => {
  const baseClasses =
    'inline-flex items-center justify-center font-semibold transition-colors rounded-lg';
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-600',
    secondary: 'bg-gray-700 hover:bg-gray-600 text-white disabled:bg-gray-700',
    danger: 'bg-red-600 hover:bg-red-700 text-white disabled:bg-gray-600',
    ghost: 'bg-transparent hover:bg-gray-700 text-white disabled:text-gray-600',
  };
  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size],
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};

interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  icon,
  className,
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        <input
          className={clsx(
            'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            icon && 'pl-10',
            error && 'border-red-500',
            className
          )}
          {...props}
        />
        {icon && (
          <div className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-gray-400">
            {icon}
          </div>
        )}
      </div>
      {error && (
        <p className="text-red-400 text-sm mt-1">{error}</p>
      )}
    </div>
  );
};

interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: Array<{ value: string | number; label: string }>;
  error?: string;
}

export const Select: React.FC<SelectProps> = ({
  label,
  options,
  error,
  className,
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label}
        </label>
      )}
      <select
        className={clsx(
          'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
          error && 'border-red-500',
          className
        )}
        {...props}
      >
        <option value="">Select an option</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-red-400 text-sm mt-1">{error}</p>
      )}
    </div>
  );
};

interface ProgressProps {
  value: number;
  max?: number;
  label?: string;
  color?: 'blue' | 'green' | 'yellow' | 'red';
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  label,
  color = 'blue',
}) => {
  const percentage = (value / max) * 100;
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  };

  return (
    <div>
      {label && (
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium text-gray-300">{label}</span>
          <span className="text-sm text-gray-400">{percentage.toFixed(0)}%</span>
        </div>
      )}
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className={clsx('h-2 rounded-full transition-all duration-300', colorClasses[color])}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
