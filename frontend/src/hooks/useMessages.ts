import { useMutation, useQuery, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import {
  fetchMessages,
  updateMessage,
  bulkUpdateMessageStatus,
} from '../api/messages';
import {
  MessageFilters,
  MessageUpdate,
  MessageBulkStatusUpdate,
} from '../types';

export function useMessages(filters: MessageFilters) {
  return useQuery({
    queryKey: ['messages', filters],
    queryFn: () => fetchMessages(filters),
    staleTime: 30000,
    placeholderData: keepPreviousData,
  });
}

export function useUpdateMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, update }: { id: number; update: MessageUpdate }) =>
      updateMessage(id, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages'] });
    },
  });
}

export function useBulkUpdateMessageStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (update: MessageBulkStatusUpdate) =>
      bulkUpdateMessageStatus(update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages'] });
    },
  });
}
