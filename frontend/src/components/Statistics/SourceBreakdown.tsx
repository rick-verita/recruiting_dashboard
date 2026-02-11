import { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Skeleton,
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
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { SourceBreakdown as SourceBreakdownType, SOURCE_OPTIONS } from '../../types';

interface SourceBreakdownProps {
  data: SourceBreakdownType[] | undefined;
  isLoading: boolean;
}

const COLORS = [
  '#1976d2',
  '#dc004e',
  '#9c27b0',
  '#ff9800',
  '#4caf50',
  '#00bcd4',
  '#795548',
  '#607d8b',
  '#e91e63',
  '#3f51b5',
];

export default function SourceBreakdown({ data, isLoading }: SourceBreakdownProps) {
  const [viewAs, setViewAs] = useState<'graph' | 'table'>('graph');

  if (isLoading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Skeleton variant="rectangular" height={300} />
      </Paper>
    );
  }

  const chartData = data?.map((item) => {
    const option = SOURCE_OPTIONS.find((o) => o.value === item.source);
    return {
      ...item,
      name: option?.label || item.source,
    };
  });

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Applications by Source</Typography>
        <Button
          size="small"
          startIcon={viewAs === 'graph' ? <TableChartIcon /> : <BarChartIcon />}
          onClick={() => setViewAs(viewAs === 'graph' ? 'table' : 'graph')}
        >
          {viewAs === 'graph' ? 'View as table' : 'View as graph'}
        </Button>
      </Box>
      {viewAs === 'table' ? (
        <TableContainer sx={{ maxHeight: 300 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Source</TableCell>
                <TableCell align="right">Count</TableCell>
                <TableCell align="right">%</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(chartData ?? []).map((row) => (
                <TableRow key={row.source}>
                  <TableCell>{row.name ?? row.source}</TableCell>
                  <TableCell align="right">{row.count.toLocaleString()}</TableCell>
                  <TableCell align="right">{row.percentage}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
      <Box sx={{ width: '100%', height: 300, overflow: 'visible' }}>
        <ResponsiveContainer>
          <PieChart margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
            <Pie
              data={chartData}
              dataKey="count"
              nameKey="name"
              cx="38%"
              cy="50%"
              outerRadius={80}
            >
              {chartData?.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number, name: string) => [
                `${value} applications`,
                name,
              ]}
            />
            <Legend
              layout="vertical"
              align="right"
              verticalAlign="middle"
              wrapperStyle={{ paddingLeft: 32, paddingRight: 8 }}
              style={{ gap: 12 }}
              formatter={(value, entry) => (
                <span style={{ whiteSpace: 'nowrap' }}>
                  {value}: {entry?.payload?.percentage ?? 0}%
                </span>
              )}
              iconType="circle"
              iconSize={10}
            />
          </PieChart>
        </ResponsiveContainer>
      </Box>
      )}
    </Paper>
  );
}
