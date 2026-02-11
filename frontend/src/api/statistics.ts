import client from './client';
import {
  DailyCount,
  DailyCountBySource,
  MultiPositionApplicantsResponse,
  PositionBreakdown,
  SourceBreakdown,
  StatusBySource,
  SummaryStats,
} from '../types';

export async function fetchSummaryStats(): Promise<SummaryStats> {
  const response = await client.get<SummaryStats>('/statistics/summary');
  return response.data;
}

export async function fetchDailyCounts(days: number = 30): Promise<DailyCount[]> {
  const response = await client.get<DailyCount[]>(`/statistics/daily?days=${days}`);
  return response.data;
}

export async function fetchDailyCountsBySource(days: number = 30): Promise<DailyCountBySource[]> {
  const response = await client.get<DailyCountBySource[]>(`/statistics/daily-by-source?days=${days}`);
  return response.data;
}

export async function fetchSourceBreakdown(): Promise<SourceBreakdown[]> {
  const response = await client.get<SourceBreakdown[]>('/statistics/by-source');
  return response.data;
}

export async function fetchStatusBySource(): Promise<StatusBySource[]> {
  const response = await client.get<StatusBySource[]>('/statistics/status-by-source');
  return response.data;
}

export async function fetchPositionBreakdown(): Promise<PositionBreakdown[]> {
  const response = await client.get<PositionBreakdown[]>('/statistics/by-position');
  return response.data;
}

export async function fetchAggregatedPositionBreakdown(): Promise<PositionBreakdown[]> {
  const response = await client.get<PositionBreakdown[]>(
    '/statistics/by-position-aggregated'
  );
  return response.data;
}

export async function fetchMultiPositionApplicants(): Promise<MultiPositionApplicantsResponse> {
  const response = await client.get<MultiPositionApplicantsResponse>(
    '/statistics/multi-position-applicants'
  );
  return response.data;
}
