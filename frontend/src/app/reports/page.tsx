'use client';

import React, { useState } from 'react';
import { Card, Button, Badge, Select, Input } from '@/components/common';
import { Download, Calendar, Filter } from 'lucide-react';

const reports = [
  {
    id: 1,
    name: 'Monthly Performance Report',
    type: 'Performance',
    generated: '2024-02-12',
    format: 'PDF',
    size: '2.4 MB',
    status: 'ready',
  },
  {
    id: 2,
    name: 'Risk Analysis - February',
    type: 'Risk',
    generated: '2024-02-11',
    format: 'PDF',
    size: '1.8 MB',
    status: 'ready',
  },
  {
    id: 3,
    name: 'Portfolio Allocation Review',
    type: 'Portfolio',
    generated: '2024-02-10',
    format: 'PDF',
    size: '3.1 MB',
    status: 'ready',
  },
  {
    id: 4,
    name: 'Trading Activity Summary',
    type: 'Trading',
    generated: '2024-02-09',
    format: 'Excel',
    size: '1.2 MB',
    status: 'ready',
  },
  {
    id: 5,
    name: 'Compliance Report',
    type: 'Compliance',
    generated: '2024-02-08',
    format: 'PDF',
    size: '2.7 MB',
    status: 'ready',
  },
  {
    id: 6,
    name: 'Agent Performance Analysis',
    type: 'Performance',
    generated: '2024-02-07',
    format: 'PDF',
    size: '1.5 MB',
    status: 'ready',
  },
];

const reportTemplates = [
  { id: 1, name: 'Daily Summary', description: 'Daily portfolio performance and activity' },
  { id: 2, name: 'Weekly Review', description: 'Weekly portfolio analysis and recommendations' },
  { id: 3, name: 'Monthly Statement', description: 'Comprehensive monthly report with all metrics' },
  { id: 4, name: 'Quarterly Analysis', description: 'Detailed quarterly performance and risk analysis' },
  { id: 5, name: 'Annual Report', description: 'Complete annual review and audit trail' },
  { id: 6, name: 'Custom Report', description: 'Create a custom report with selected metrics' },
];

export default function ReportsPage() {
  const [reportType, setReportType] = useState('monthly');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-02-12');
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Reports</h1>
        <p className="text-gray-400 mt-2">Generate and download portfolio and performance reports</p>
      </div>

      {/* Report Generator */}
      <Card title="Generate Report" subtitle="Create a new custom report">
        <div className="space-y-4">
          <Select
            label="Report Type"
            options={[
              { value: 'daily', label: 'Daily Summary' },
              { value: 'weekly', label: 'Weekly Review' },
              { value: 'monthly', label: 'Monthly Statement' },
              { value: 'quarterly', label: 'Quarterly Analysis' },
              { value: 'annual', label: 'Annual Report' },
            ]}
            value={reportType}
            onChange={(e) => setReportType(e.target.value)}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Start Date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
            <Input
              label="End Date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>

          <div>
            <p className="text-sm text-gray-400 mb-3">Report Components</p>
            <div className="space-y-2">
              {['Portfolio Summary', 'Performance Analysis', 'Risk Metrics', 'Trading Activity', 'Agent Performance', 'Recommendations'].map(
                (component) => (
                  <div key={component} className="flex items-center gap-3">
                    <input type="checkbox" defaultChecked className="w-4 h-4" />
                    <label className="text-gray-300 cursor-pointer">{component}</label>
                  </div>
                )
              )}
            </div>
          </div>

          <div className="flex gap-3">
            <Button variant="primary" className="flex-1">
              <Download size={20} className="mr-2" />
              Generate Report
            </Button>
            <Button variant="secondary" className="flex-1">
              Schedule Report
            </Button>
          </div>
        </div>
      </Card>

      {/* Recent Reports */}
      <Card title="Recent Reports" subtitle="Previously generated reports">
        <div className="space-y-3">
          {reports.map((report) => (
            <div
              key={report.id}
              className="p-4 bg-gray-700 rounded-lg border border-gray-600 flex items-center justify-between hover:border-blue-500 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <div>
                    <p className="font-semibold text-white">{report.name}</p>
                    <div className="flex gap-3 mt-2 text-xs text-gray-400">
                      <span>{report.generated}</span>
                      <span>•</span>
                      <span>{report.format}</span>
                      <span>•</span>
                      <span>{report.size}</span>
                    </div>
                  </div>
                  <Badge label={report.type} variant="info" size="sm" />
                </div>
              </div>
              <Button variant="primary" size="sm">
                <Download size={16} className="mr-2" />
                Download
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Report Templates */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-4">Quick Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reportTemplates.map((template) => (
            <Card
              key={template.id}
              className="cursor-pointer hover:border-blue-500 transition-colors"
              onClick={() => setSelectedTemplate(template.id)}
            >
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  {template.name}
                </h3>
                <p className="text-sm text-gray-400 mb-4">{template.description}</p>
                <Button variant="primary" className="w-full">
                  Use Template
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Scheduled Reports */}
      <Card title="Scheduled Reports" subtitle="Automatically generated reports">
        <div className="space-y-3">
          <div className="p-4 bg-gray-700 rounded-lg border border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-white">Daily Market Summary</p>
                <p className="text-sm text-gray-400 mt-1">Sent daily at 5:00 PM EST</p>
              </div>
              <Badge label="Active" variant="success" size="sm" />
            </div>
          </div>
          <div className="p-4 bg-gray-700 rounded-lg border border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-white">Weekly Performance Report</p>
                <p className="text-sm text-gray-400 mt-1">Sent every Monday at 9:00 AM EST</p>
              </div>
              <Badge label="Active" variant="success" size="sm" />
            </div>
          </div>
          <div className="p-4 bg-gray-700 rounded-lg border border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-white">Monthly Statement</p>
                <p className="text-sm text-gray-400 mt-1">Sent on the 1st of each month at 8:00 AM EST</p>
              </div>
              <Badge label="Active" variant="success" size="sm" />
            </div>
          </div>
        </div>
      </Card>

      {/* Report Settings */}
      <Card title="Report Settings" subtitle="Customize report preferences">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="font-semibold text-white">Include Charts</p>
              <p className="text-sm text-gray-400">Add visualizations to all reports</p>
            </div>
            <input type="checkbox" defaultChecked className="w-5 h-5" />
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="font-semibold text-white">Include Recommendations</p>
              <p className="text-sm text-gray-400">Add AI recommendations to reports</p>
            </div>
            <input type="checkbox" defaultChecked className="w-5 h-5" />
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div>
              <p className="font-semibold text-white">Detailed Analysis</p>
              <p className="text-sm text-gray-400">Include deep dive analysis sections</p>
            </div>
            <input type="checkbox" defaultChecked className="w-5 h-5" />
          </div>
        </div>
      </Card>
    </div>
  );
}
