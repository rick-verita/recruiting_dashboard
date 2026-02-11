import { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Skeleton,
  ToggleButton,
  ToggleButtonGroup,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import TableChartIcon from '@mui/icons-material/TableChart';
import BarChartIcon from '@mui/icons-material/BarChart';
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

type ViewAs = 'graph' | 'table';

export default function DailyChart({ data, dataBySource, isLoading }: DailyChartProps) {
  const [viewMode, setViewMode] = useState<'total' | 'by-source'>('total');
  const [viewAs, setViewAs] = useState<ViewAs>('graph');

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

  // Table: most recent date at top (descending)
  const tableDataTotal = (chartDataTotal ?? []).slice().sort((a, b) => b.date.localeCompare(a.date));
  const tableDataBySource = (chartDataBySource ?? []).slice().sort((a, b) => b.date.localeCompare(a.date));
  const sourceColumns = Array.from(activeSources);

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1 }}>
        <Typography variant="h6">Daily Applications (Last 30 Days)</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={handleViewModeChange}
            size="small"
          >
            <ToggleButton value="total">Total</ToggleButton>
            <ToggleButton value="by-source">By Source</ToggleButton>
          </ToggleButtonGroup>
          <Button
            size="small"
            startIcon={viewAs === 'graph' ? <TableChartIcon /> : <BarChartIcon />}
            onClick={() => setViewAs(viewAs === 'graph' ? 'table' : 'graph')}
          >
            {viewAs === 'graph' ? 'View as table' : 'View as graph'}
          </Button>
        </Box>
      </Box>
      {viewAs === 'table' ? (
        <TableContainer sx={{ maxHeight: 300 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                {viewMode === 'total' ? (
                  <TableCell align="right">Count</TableCell>
                ) : (
                  sourceColumns.map((src) => {
                    const opt = SOURCE_OPTIONS.find((o) => o.value === src);
                    return (
                      <TableCell key={src} align="right">
                        {opt?.label ?? src}
                      </TableCell>
                    );
                  })
                )}
              </TableRow>
            </TableHead>
            <TableBody>
              {(viewMode === 'total' ? tableDataTotal : tableDataBySource).map((row: { date: string; dateLabel: string; count?: number; [k: string]: unknown }) => (
                <TableRow key={row.date}>
                  <TableCell>{row.dateLabel ?? row.date}</TableCell>
                  {viewMode === 'total' ? (
                    <TableCell align="right">{(row.count ?? 0).toLocaleString()}</TableCell>
                  ) : (
                    sourceColumns.map((src) => (
                      <TableCell key={src} align="right">
                        {((row[src] as number) ?? 0).toLocaleString()}
                      </TableCell>
                    ))
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
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
      )}
    </Paper>
  );
}
