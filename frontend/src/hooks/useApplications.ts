import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchApplications, updateApplication, bulkUpdateStatus } from '../api/applications';
import { ApplicationFilters, ApplicationUpdate, BulkStatusUpdate } from '../types';

export function useApplications(filters: ApplicationFilters) {
  return useQuery({
    queryKey: ['applications', filters],
    queryFn: () => fetchApplications(filters),
    staleTime: 30000,
  });
}

export function useUpdateApplication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, update }: { id: number; update: ApplicationUpdate }) =>
      updateApplication(id, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });
}

export function useBulkUpdateStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (update: BulkStatusUpdate) => bulkUpdateStatus(update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });
}
