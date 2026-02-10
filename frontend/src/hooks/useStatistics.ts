import { useQuery } from '@tanstack/react-query';
import {
  fetchSummaryStats,
  fetchDailyCounts,
  fetchDailyCountsBySource,
  fetchSourceBreakdown,
  fetchStatusBySource,
} from '../api/statistics';

export function useSummaryStats() {
  return useQuery({
    queryKey: ['statistics', 'summary'],
    queryFn: fetchSummaryStats,
    staleTime: 60000,
  });
}

export function useDailyCounts(days: number = 30) {
  return useQuery({
    queryKey: ['statistics', 'daily', days],
    queryFn: () => fetchDailyCounts(days),
    staleTime: 60000,
  });
}

export function useDailyCountsBySource(days: number = 30) {
  return useQuery({
    queryKey: ['statistics', 'daily-by-source', days],
    queryFn: () => fetchDailyCountsBySource(days),
    staleTime: 60000,
  });
}

export function useSourceBreakdown() {
  return useQuery({
    queryKey: ['statistics', 'by-source'],
    queryFn: fetchSourceBreakdown,
    staleTime: 60000,
  });
}

export function useStatusBySource() {
  return useQuery({
    queryKey: ['statistics', 'status-by-source'],
    queryFn: fetchStatusBySource,
    staleTime: 60000,
  });
}
