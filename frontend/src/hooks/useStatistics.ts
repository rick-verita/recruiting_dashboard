import { useQuery } from '@tanstack/react-query';
import {
  fetchSummaryStats,
  fetchDailyCounts,
  fetchDailyCountsBySource,
  fetchSourceBreakdown,
  fetchStatusBySource,
  fetchPositionBreakdown,
  fetchAggregatedPositionBreakdown,
  fetchMultiPositionApplicants,
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

export function usePositionBreakdown() {
  return useQuery({
    queryKey: ['statistics', 'by-position'],
    queryFn: fetchPositionBreakdown,
    staleTime: 60000,
  });
}

export function useAggregatedPositionBreakdown() {
  return useQuery({
    queryKey: ['statistics', 'by-position-aggregated'],
    queryFn: fetchAggregatedPositionBreakdown,
    staleTime: 60000,
  });
}

export function useMultiPositionApplicants() {
  return useQuery({
    queryKey: ['statistics', 'multi-position-applicants'],
    queryFn: fetchMultiPositionApplicants,
    staleTime: 60000,
  });
}
