import { Grid, Paper, Typography, Box, Skeleton } from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import AssignmentIcon from '@mui/icons-material/Assignment';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RateReviewIcon from '@mui/icons-material/RateReview';
import ContactPhoneIcon from '@mui/icons-material/ContactPhone';
import CancelIcon from '@mui/icons-material/Cancel';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
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
  suffix?: string;
}

function StatCard({ title, value, icon, color, suffix = '' }: StatCardProps) {
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
          <Typography variant="h4">
            {typeof value === 'number' && value % 1 !== 0
              ? value.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
              : value.toLocaleString()}
            {suffix}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
}

export default function SummaryCards({ data, isLoading }: SummaryCardsProps) {
  if (isLoading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3, 4, 5, 6, 7].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Skeleton variant="rectangular" height={100} />
          </Grid>
        ))}
      </Grid>
    );
  }

  if (!data) return null;

  const hiredCount = data.status_counts['hired'] || 0;
  const reviewRate = data.review_rate ?? 0;
  const contactRate = data.contact_rate ?? 0;
  const rejectedRate = data.rejected_rate ?? 0;
  const hireRate = data.hire_rate ?? 0;

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
          title="Unique Applicants"
          value={data.total_applicants}
          icon={<PeopleIcon sx={{ color: 'white', fontSize: 28 }} />}
          color="#9c27b0"
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
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Review Rate"
          value={reviewRate}
          suffix="%"
          icon={<RateReviewIcon sx={{ color: 'white', fontSize: 28 }} />}
          color="#5c6bc0"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Contact Rate"
          value={contactRate}
          suffix="%"
          icon={<ContactPhoneIcon sx={{ color: 'white', fontSize: 28 }} />}
          color="#26a69a"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Rejected Rate"
          value={rejectedRate}
          suffix="%"
          icon={<CancelIcon sx={{ color: 'white', fontSize: 28 }} />}
          color="#ef5350"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Hire Rate"
          value={hireRate}
          suffix="%"
          icon={<TrendingUpIcon sx={{ color: 'white', fontSize: 28 }} />}
          color="#00897b"
        />
      </Grid>
    </Grid>
  );
}
