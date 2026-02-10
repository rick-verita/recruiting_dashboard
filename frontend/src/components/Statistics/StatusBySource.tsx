import { Paper, Typography, Box, Skeleton } from '@mui/material';
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
      <Typography variant="h6" gutterBottom>
        Status Distribution by Source
      </Typography>
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
    </Paper>
  );
}
