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
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { StatusBySource as StatusBySourceType, SOURCE_OPTIONS, STATUS_OPTIONS } from '../../types';

interface StatusBySourceProps {
  data: StatusBySourceType[] | undefined;
  isLoading: boolean;
}

export default function StatusBySource({ data, isLoading }: StatusBySourceProps) {
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
      name: option?.label || item.source,
      ...item.status_counts,
    };
  });

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Status Distribution by Source</Typography>
        <Button
          size="small"
          startIcon={viewAs === 'graph' ? <TableChartIcon /> : <BarChartIcon />}
          onClick={() => setViewAs(viewAs === 'graph' ? 'table' : 'graph')}
        >
          {viewAs === 'graph' ? 'View as table' : 'View as graph'}
        </Button>
      </Box>
      {viewAs === 'table' ? (
        <TableContainer sx={{ maxHeight: 400 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Source</TableCell>
                {STATUS_OPTIONS.map((s) => (
                  <TableCell key={s.value} align="right">
                    {s.label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {(data ?? []).map((row) => {
                const option = SOURCE_OPTIONS.find((o) => o.value === row.source);
                return (
                  <TableRow key={row.source}>
                    <TableCell>{option?.label ?? row.source}</TableCell>
                    {STATUS_OPTIONS.map((s) => (
                      <TableCell key={s.value} align="right">
                        {(row.status_counts[s.value] ?? 0).toLocaleString()}
                      </TableCell>
                    ))}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
      <Box sx={{ width: '100%', height: 400 }}>
        <ResponsiveContainer>
          <BarChart data={chartData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" allowDecimals={false} />
            <YAxis dataKey="name" type="category" width={150} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            {STATUS_OPTIONS.map((status) => (
              <Bar
                key={status.value}
                dataKey={status.value}
                name={status.label}
                fill={status.color}
                stackId="a"
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </Box>
      )}
    </Paper>
  );
}
