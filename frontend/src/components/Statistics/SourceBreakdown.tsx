import { Paper, Typography, Box, Skeleton } from '@mui/material';
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
      <Typography variant="h6" gutterBottom>
        Applications by Source
      </Typography>
      <Box sx={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="count"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ name, percentage }) => `${name}: ${percentage}%`}
              labelLine
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
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}
