export type ApplicationStatus = 'new' | 'reviewed' | 'contacted' | 'rejected' | 'hired';

export type JobBoard =
  | 'ziprecruiter'
  | 'handshake'
  | 'wellfound'
  | 'indeed'
  | 'linkedin'
  | 'welcome_to_the_jungle'
  | 'greenhouse'
  | 'lever'
  | 'other'
  | 'unknown';

export interface Position {
  id: number;
  title: string;
}

export interface Applicant {
  id: number;
  first_name: string;
  last_name: string;
}

export interface Application {
  id: number;
  applicant: Applicant;
  applicant_name: string;
  positions: Position[];
  position_titles: string;
  source: JobBoard;
  status: ApplicationStatus;
  comments: string | null;
  application_link: string | null;
  application_time: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationListResponse {
  items: Application[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApplicationUpdate {
  status?: ApplicationStatus;
  comments?: string;
}

export interface BulkStatusUpdate {
  ids: number[];
  status: ApplicationStatus;
}

export interface SummaryStats {
  total_applications: number;
  total_applicants: number;
  status_counts: Record<string, number>;
  source_counts: Record<string, number>;
}

export interface DailyCount {
  date: string;
  count: number;
}

export interface DailyCountBySource {
  date: string;
  counts: Record<string, number>;
}

export interface SourceBreakdown {
  source: string;
  count: number;
  percentage: number;
}

export interface StatusBySource {
  source: string;
  status_counts: Record<string, number>;
}

export interface PositionListItem {
  id: number;
  title: string;
  is_active: boolean;
}

export interface ApplicationFilters {
  page: number;
  page_size: number;
  sort_by: string;
  sort_order: 'asc' | 'desc';
  search?: string;
  status?: string[];
  source?: string[];
  date_from?: string;
  date_to?: string;
}

export const STATUS_OPTIONS: { value: ApplicationStatus; label: string; color: string }[] = [
  { value: 'new', label: 'New', color: '#2196f3' },
  { value: 'reviewed', label: 'Reviewed', color: '#ff9800' },
  { value: 'contacted', label: 'Contacted', color: '#9c27b0' },
  { value: 'rejected', label: 'Rejected', color: '#f44336' },
  { value: 'hired', label: 'Hired', color: '#4caf50' },
];

export const SOURCE_OPTIONS: { value: JobBoard; label: string }[] = [
  { value: 'ziprecruiter', label: 'ZipRecruiter' },
  { value: 'handshake', label: 'Handshake' },
  { value: 'wellfound', label: 'Wellfound' },
  { value: 'indeed', label: 'Indeed' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'welcome_to_the_jungle', label: 'Welcome to the Jungle' },
  { value: 'greenhouse', label: 'Greenhouse' },
  { value: 'lever', label: 'Lever' },
  { value: 'other', label: 'Other' },
  { value: 'unknown', label: 'Unknown' },
];
