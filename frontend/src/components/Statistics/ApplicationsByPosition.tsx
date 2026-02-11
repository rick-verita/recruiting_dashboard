import { useState } from 'react';
import {
  Paper,
  Typography,
  Skeleton,
  Box,
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
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { PositionBreakdown } from '../../types';

const BAR_COLORS = [
  '#1976d2',
  '#9c27b0',
  '#00897b',
  '#ff9800',
  '#00bcd4',
  '#795548',
  '#607d8b',
  '#e91e63',
];

function wrapTickLabel(text: string, maxCharsPerLine: number = 36): string[] {
  if (text.length <= maxCharsPerLine) return [text];
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let current = '';
  for (const w of words) {
    if (current.length + 1 + w.length <= maxCharsPerLine) {
      current = current ? `${current} ${w}` : w;
    } else {
      if (current) lines.push(current);
      current = w.length > maxCharsPerLine ? w.slice(0, maxCharsPerLine) : w;
    }
  }
  if (current) lines.push(current);
  return lines.slice(0, 2);
}

interface ApplicationsByPositionProps {
  data: PositionBreakdown[] | undefined;
  aggregatedData: PositionBreakdown[] | undefined;
  isLoading: boolean;
  isAggregatedLoading: boolean;
}

export default function ApplicationsByPosition({
  data,
  aggregatedData,
  isLoading,
  isAggregatedLoading,
}: ApplicationsByPositionProps) {
  const [viewMode, setViewMode] = useState<'count' | 'percent'>('count');
  const [viewAs, setViewAs] = useState<'graph' | 'table'>('graph');
  const [viewAggregate, setViewAggregate] = useState(false);

  const effectiveData = viewAggregate ? aggregatedData : data;
  const effectiveLoading = viewAggregate ? isAggregatedLoading : isLoading;

  if (effectiveLoading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Skeleton variant="rectangular" height={300} />
      </Paper>
    );
  }

  if (!effectiveData || effectiveData.length === 0) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Applications by Position
        </Typography>
        <Typography color="text.secondary">No position data yet.</Typography>
      </Paper>
    );
  }

  const chartData = effectiveData.map((row) => ({
    ...row,
    name: row.position_title,
    value: viewMode === 'percent' ? row.percentage : row.count,
  }));

  const handleViewModeChange = (
    _: React.MouseEvent<HTMLElement>,
    newMode: 'count' | 'percent' | null
  ) => {
    if (newMode !== null) {
      setViewMode(newMode);
    }
  };

  const barHeight = 28;
  const barCategoryGap = 12;
  const chartHeight = effectiveData.length * (barHeight + barCategoryGap) + 40;

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1 }}>
        <Typography variant="h6">Applications by Position</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={handleViewModeChange}
            size="small"
          >
            <ToggleButton value="count">Count</ToggleButton>
            <ToggleButton value="percent">Percent</ToggleButton>
          </ToggleButtonGroup>
          <Button
            size="small"
            variant={viewAggregate ? 'contained' : 'outlined'}
            onClick={() => setViewAggregate(!viewAggregate)}
          >
            {viewAggregate ? 'View separated' : 'View as aggregate'}
          </Button>
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
        <TableContainer sx={{ maxHeight: Math.max(280, chartHeight) }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Position</TableCell>
                <TableCell align="right">Count</TableCell>
                <TableCell align="right">%</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {effectiveData.map((row) => (
                <TableRow key={row.position_title}>
                  <TableCell>{row.position_title}</TableCell>
                  <TableCell align="right">{row.count.toLocaleString()}</TableCell>
                  <TableCell align="right">{row.percentage}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
      <Box sx={{ width: '100%', height: Math.max(280, chartHeight) }}>
        <ResponsiveContainer>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 8, right: 24, left: 4, bottom: 8 }}
            barCategoryGap={barCategoryGap}
            barGap={8}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis
              type="number"
              tickFormatter={
                viewMode === 'percent' ? (v) => `${v}%` : (v) => v.toLocaleString()
              }
              domain={viewMode === 'percent' ? [0, 100] : undefined}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={240}
              interval={0}
              tick={(props) => {
                const { x, y, payload } = props;
                const label = payload?.name ?? payload?.value ?? String(payload ?? '');
                const lines = wrapTickLabel(label);
                const lineHeight = 14;
                const totalHeight = lines.length * lineHeight;
                const startY = -totalHeight / 2 + lineHeight / 2;
                return (
                  <g transform={`translate(${x},${y})`}>
                    {lines.map((line, i) => (
                      <text
                        key={i}
                        textAnchor="end"
                        x={0}
                        y={startY + i * lineHeight}
                        dy={4}
                        fontSize={12}
                        fill="#666"
                      >
                        {line}
                      </text>
                    ))}
                  </g>
                );
              }}
            />
            <Tooltip
              formatter={(value: number) => [
                viewMode === 'percent' ? `${value}%` : value.toLocaleString(),
                viewMode === 'percent' ? 'Share' : 'Count',
              ]}
              labelFormatter={(label) => label}
            />
            <Bar
              dataKey="value"
              name={viewMode === 'percent' ? 'Share' : 'Count'}
              radius={[0, 4, 4, 0]}
              barSize={barHeight - 4}
            >
              {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
      )}
    </Paper>
  );
}
