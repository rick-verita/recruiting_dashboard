import { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
  SelectChangeEvent,
  Button,
} from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
import { ApplicationFilters, STATUS_OPTIONS, SOURCE_OPTIONS } from '../../types';

interface FilterToolbarProps {
  filters: ApplicationFilters;
  onFiltersChange: (filters: Partial<ApplicationFilters>) => void;
}

export default function FilterToolbar({ filters, onFiltersChange }: FilterToolbarProps) {
  const [searchInput, setSearchInput] = useState(filters.search || '');

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== filters.search) {
        onFiltersChange({ search: searchInput || undefined, page: 1 });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const handleStatusChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    onFiltersChange({
      status: typeof value === 'string' ? value.split(',') : value,
      page: 1,
    });
  };

  const handleSourceChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    onFiltersChange({
      source: typeof value === 'string' ? value.split(',') : value,
      page: 1,
    });
  };

  const handleClearFilters = () => {
    setSearchInput('');
    onFiltersChange({
      search: undefined,
      status: undefined,
      source: undefined,
      date_from: undefined,
      date_to: undefined,
      page: 1,
    });
  };

  const hasActiveFilters =
    filters.search ||
    (filters.status && filters.status.length > 0) ||
    (filters.source && filters.source.length > 0) ||
    filters.date_from ||
    filters.date_to;

  return (
    <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap', alignItems: 'center' }}>
      <TextField
        label="Search"
        variant="outlined"
        size="small"
        value={searchInput}
        onChange={(e) => setSearchInput(e.target.value)}
        placeholder="Search by name or position..."
        sx={{ minWidth: 250 }}
      />

      <FormControl size="small" sx={{ minWidth: 200 }}>
        <InputLabel>Status</InputLabel>
        <Select
          multiple
          value={filters.status || []}
          onChange={handleStatusChange}
          input={<OutlinedInput label="Status" />}
          renderValue={(selected) => (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {selected.map((value) => {
                const option = STATUS_OPTIONS.find((o) => o.value === value);
                return (
                  <Chip
                    key={value}
                    label={option?.label || value}
                    size="small"
                    sx={{ backgroundColor: option?.color, color: 'white' }}
                  />
                );
              })}
            </Box>
          )}
        >
          {STATUS_OPTIONS.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl size="small" sx={{ minWidth: 200 }}>
        <InputLabel>Source</InputLabel>
        <Select
          multiple
          value={filters.source || []}
          onChange={handleSourceChange}
          input={<OutlinedInput label="Source" />}
          renderValue={(selected) => (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {selected.map((value) => {
                const option = SOURCE_OPTIONS.find((o) => o.value === value);
                return <Chip key={value} label={option?.label || value} size="small" />;
              })}
            </Box>
          )}
        >
          {SOURCE_OPTIONS.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <TextField
        label="From Date"
        type="date"
        size="small"
        value={filters.date_from || ''}
        onChange={(e) => onFiltersChange({ date_from: e.target.value || undefined, page: 1 })}
        InputLabelProps={{ shrink: true }}
      />

      <TextField
        label="To Date"
        type="date"
        size="small"
        value={filters.date_to || ''}
        onChange={(e) => onFiltersChange({ date_to: e.target.value || undefined, page: 1 })}
        InputLabelProps={{ shrink: true }}
      />

      {hasActiveFilters && (
        <Button
          variant="outlined"
          size="small"
          startIcon={<ClearIcon />}
          onClick={handleClearFilters}
        >
          Clear Filters
        </Button>
      )}
    </Box>
  );
}
