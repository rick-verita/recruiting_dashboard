import { Grid, Paper, Typography, Box, Skeleton } from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import AssignmentIcon from '@mui/icons-material/Assignment';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import { SummaryStats } from '../../types';

interface SummaryCardsProps {
  data: SummaryStats | undefined;
  isLoading: boolean;
}

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

function StatCard({ title, value, icon, color }: StatCardProps) {
  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box
          sx={{
            backgroundColor: color,
            borderRadius: 2,
            p: 1.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
          <Typography variant="h4">{value.toLocaleString()}</Typography>
        </Box>
      </Box>
    </Paper>
  );
}

export default function SummaryCards({ data, isLoading }: SummaryCardsProps) {
  if (isLoading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Skeleton variant="rectangular" height={100} />
          </Grid>
        ))}
      </Grid>
    );
  }

  if (!data) return null;

  const newCount = data.status_counts['new'] || 0;
  const hiredCount = data.status_counts['hired'] || 0;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Total Applications"
          value={data.total_applications}
          icon={<AssignmentIcon sx={{ color: 'white', fontSize: 28 }} />}
          color="#1976d2"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Total Applicants"
          value={data.total_applicants}
          icon={<PeopleIcon sx={{ color: 'white', fontSize: 28 }} />}
          color="#9c27b0"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="New Applications"
          value={newCount}
          icon={<HourglassEmptyIcon sx={{ color: 'white', fontSize: 28 }} />}
          color="#2196f3"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Hired"
          value={hiredCount}
          icon={<CheckCircleIcon sx={{ color: 'white', fontSize: 28 }} />}
          color="#4caf50"
        />
      </Grid>
    </Grid>
  );
}
