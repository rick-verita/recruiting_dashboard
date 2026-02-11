import { useMutation, useQuery, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { fetchApplications, updateApplication, bulkUpdateStatus } from '../api/applications';
import { ApplicationFilters, ApplicationUpdate, BulkStatusUpdate } from '../types';

export function useApplications(filters: ApplicationFilters) {
  return useQuery({
    queryKey: ['applications', filters],
    queryFn: () => fetchApplications(filters),
    staleTime: 30000,
    placeholderData: keepPreviousData,
  });
}

export function useUpdateApplication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, update }: { id: number; update: ApplicationUpdate }) =>
      updateApplication(id, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
    },
  });
}

export function useBulkUpdateStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (update: BulkStatusUpdate) => bulkUpdateStatus(update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
    },
  });
}
