import { useState } from 'react';
import { Paper, Typography, Box, Skeleton, ToggleButton, ToggleButtonGroup } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { DailyCount, DailyCountBySource, SOURCE_OPTIONS } from '../../types';

// Colors for each source
const SOURCE_COLORS: Record<string, string> = {
  ziprecruiter: '#1976d2',
  handshake: '#9c27b0',
  wellfound: '#ff9800',
  indeed: '#4caf50',
  linkedin: '#0077b5',
  welcome_to_the_jungle: '#e91e63',
  greenhouse: '#00bcd4',
  lever: '#795548',
  other: '#607d8b',
  unknown: '#9e9e9e',
};

interface DailyChartProps {
  data: DailyCount[] | undefined;
  dataBySource: DailyCountBySource[] | undefined;
  isLoading: boolean;
}

export default function DailyChart({ data, dataBySource, isLoading }: DailyChartProps) {
  const [viewMode, setViewMode] = useState<'total' | 'by-source'>('total');

  if (isLoading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Skeleton variant="rectangular" height={300} />
      </Paper>
    );
  }

  const handleViewModeChange = (
    _: React.MouseEvent<HTMLElement>,
    newMode: 'total' | 'by-source' | null
  ) => {
    if (newMode !== null) {
      setViewMode(newMode);
    }
  };

  // Get all sources that have data
  const activeSources = new Set<string>();
  dataBySource?.forEach((item) => {
    Object.keys(item.counts).forEach((source) => {
      if (item.counts[source] > 0) {
        activeSources.add(source);
      }
    });
  });

  // Transform data for the by-source view
  const chartDataBySource = dataBySource?.map((item) => ({
    date: item.date,
    dateLabel: format(parseISO(item.date), 'MMM d'),
    ...item.counts,
  }));

  const chartDataTotal = data?.map((item) => ({
    ...item,
    dateLabel: format(parseISO(item.date), 'MMM d'),
  }));

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Daily Applications (Last 30 Days)</Typography>
        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={handleViewModeChange}
          size="small"
        >
          <ToggleButton value="total">Total</ToggleButton>
          <ToggleButton value="by-source">By Source</ToggleButton>
        </ToggleButtonGroup>
      </Box>
      <Box sx={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          {viewMode === 'total' ? (
            <LineChart data={chartDataTotal}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="dateLabel"
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis allowDecimals={false} />
              <Tooltip
                labelFormatter={(_, payload) => {
                  if (payload && payload[0]) {
                    return format(parseISO(payload[0].payload.date), 'MMMM d, yyyy');
                  }
                  return '';
                }}
              />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#1976d2"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          ) : (
            <LineChart data={chartDataBySource}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="dateLabel"
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis allowDecimals={false} />
              <Tooltip
                labelFormatter={(_, payload) => {
                  if (payload && payload[0]) {
                    return format(parseISO(payload[0].payload.date), 'MMMM d, yyyy');
                  }
                  return '';
                }}
              />
              <Legend />
              {Array.from(activeSources).map((source) => {
                const sourceOption = SOURCE_OPTIONS.find((o) => o.value === source);
                return (
                  <Line
                    key={source}
                    type="monotone"
                    dataKey={source}
                    name={sourceOption?.label || source}
                    stroke={SOURCE_COLORS[source] || '#999'}
                    strokeWidth={2}
                    dot={{ r: 2 }}
                    activeDot={{ r: 4 }}
                  />
                );
              })}
            </LineChart>
          )}
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}
