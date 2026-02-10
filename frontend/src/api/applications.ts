import client from './client';
import {
  Application,
  ApplicationFilters,
  ApplicationListResponse,
  ApplicationUpdate,
  BulkStatusUpdate,
} from '../types';

export async function fetchApplications(
  filters: ApplicationFilters
): Promise<ApplicationListResponse> {
  const params = new URLSearchParams();
  params.set('page', filters.page.toString());
  params.set('page_size', filters.page_size.toString());
  params.set('sort_by', filters.sort_by);
  params.set('sort_order', filters.sort_order);

  if (filters.search) {
    params.set('search', filters.search);
  }
  if (filters.status && filters.status.length > 0) {
    filters.status.forEach((s) => params.append('status', s));
  }
  if (filters.source && filters.source.length > 0) {
    filters.source.forEach((s) => params.append('source', s));
  }
  if (filters.date_from) {
    params.set('date_from', filters.date_from);
  }
  if (filters.date_to) {
    params.set('date_to', filters.date_to);
  }

  const response = await client.get<ApplicationListResponse>(`/applications?${params.toString()}`);
  return response.data;
}

export async function updateApplication(
  id: number,
  update: ApplicationUpdate
): Promise<Application> {
  const response = await client.patch<Application>(`/applications/${id}`, update);
  return response.data;
}

export async function bulkUpdateStatus(update: BulkStatusUpdate): Promise<{ updated: number }> {
  const response = await client.patch<{ updated: number }>('/applications/bulk/status', update);
  return response.data;
}
