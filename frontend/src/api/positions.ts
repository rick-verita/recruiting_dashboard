import client from './client';
import { PositionListItem } from '../types';

export async function fetchPositions(activeOnly: boolean = false): Promise<PositionListItem[]> {
  const response = await client.get<PositionListItem[]>(
    `/positions?active_only=${activeOnly}`
  );
  return response.data;
}
