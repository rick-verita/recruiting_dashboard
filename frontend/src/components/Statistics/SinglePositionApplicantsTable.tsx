import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Link,
  Skeleton,
} from '@mui/material';
import { MultiPositionApplicantsResponse } from '../../types';

interface MultiPositionApplicantsTableProps {
  data: MultiPositionApplicantsResponse | undefined;
  isLoading: boolean;
}

export default function MultiPositionApplicantsTable({
  data,
  isLoading,
}: MultiPositionApplicantsTableProps) {
  if (isLoading) {
    return (
      <Box sx={{ mt: 4 }}>
        <Skeleton variant="text" width={320} height={32} sx={{ mb: 1 }} />
        <Skeleton variant="rectangular" height={320} />
      </Box>
    );
  }

  if (!data) return null;

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        Applicants who applied to multiple positions
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Total: {data.total}
      </Typography>
      <TableContainer
        component={Paper}
        sx={{ maxHeight: 320, width: '100%' }}
      >
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Position(s)</TableCell>
              <TableCell>Link</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.items.map((row, idx) => (
              <TableRow key={idx}>
                <TableCell>{row.applicant_name}</TableCell>
                <TableCell>{row.position_titles}</TableCell>
                <TableCell>
                  {row.application_link ? (
                    <Link
                      href={row.application_link}
                      target="_blank"
                      rel="noopener"
                    >
                      View
                    </Link>
                  ) : (
                    '—'
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
