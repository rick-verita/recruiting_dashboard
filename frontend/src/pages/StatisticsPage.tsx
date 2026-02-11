import { Box, Typography, Grid } from '@mui/material';
import SummaryCards from '../components/Statistics/SummaryCards';
import DailyChart from '../components/Statistics/DailyChart';
import SourceBreakdown from '../components/Statistics/SourceBreakdown';
import StatusBySource from '../components/Statistics/StatusBySource';
import ApplicationsByPosition from '../components/Statistics/ApplicationsByPosition';
import MultiPositionApplicantsTable from '../components/Statistics/SinglePositionApplicantsTable';
import {
  useSummaryStats,
  useDailyCounts,
  useDailyCountsBySource,
  useSourceBreakdown,
  useStatusBySource,
  usePositionBreakdown,
  useAggregatedPositionBreakdown,
  useMultiPositionApplicants,
} from '../hooks/useStatistics';

export default function StatisticsPage() {
  const summaryQuery = useSummaryStats();
  const dailyQuery = useDailyCounts(30);
  const dailyBySourceQuery = useDailyCountsBySource(30);
  const sourceQuery = useSourceBreakdown();
  const statusBySourceQuery = useStatusBySource();
  const positionBreakdownQuery = usePositionBreakdown();
  const aggregatedPositionBreakdownQuery = useAggregatedPositionBreakdown();
  const multiPositionQuery = useMultiPositionApplicants();

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Statistics
      </Typography>

      <Box sx={{ mb: 4 }}>
        <SummaryCards data={summaryQuery.data} isLoading={summaryQuery.isLoading} />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <DailyChart
            data={dailyQuery.data}
            dataBySource={dailyBySourceQuery.data}
            isLoading={dailyQuery.isLoading || dailyBySourceQuery.isLoading}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <SourceBreakdown data={sourceQuery.data} isLoading={sourceQuery.isLoading} />
        </Grid>
        <Grid item xs={12} md={6}>
          <StatusBySource
            data={statusBySourceQuery.data}
            isLoading={statusBySourceQuery.isLoading}
          />
        </Grid>
        <Grid item xs={12}>
          <ApplicationsByPosition
            data={positionBreakdownQuery.data}
            aggregatedData={aggregatedPositionBreakdownQuery.data}
            isLoading={positionBreakdownQuery.isLoading}
            isAggregatedLoading={aggregatedPositionBreakdownQuery.isLoading}
          />
        </Grid>
        <Grid item xs={12}>
          <MultiPositionApplicantsTable
            data={multiPositionQuery.data}
            isLoading={multiPositionQuery.isLoading}
          />
        </Grid>
      </Grid>
    </Box>
  );
}
