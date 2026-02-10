import { Select, MenuItem, SelectChangeEvent } from '@mui/material';
import { ApplicationStatus, STATUS_OPTIONS } from '../../types';

interface StatusSelectProps {
  value: ApplicationStatus;
  onChange: (value: ApplicationStatus) => void;
  disabled?: boolean;
}

export default function StatusSelect({ value, onChange, disabled }: StatusSelectProps) {
  const handleChange = (event: SelectChangeEvent<ApplicationStatus>) => {
    onChange(event.target.value as ApplicationStatus);
  };

  const currentOption = STATUS_OPTIONS.find((opt) => opt.value === value);

  return (
    <Select
      value={value}
      onChange={handleChange}
      disabled={disabled}
      size="small"
      sx={{
        minWidth: 120,
        '& .MuiSelect-select': {
          py: 0.5,
          backgroundColor: currentOption?.color,
          color: 'white',
          borderRadius: 1,
        },
      }}
    >
      {STATUS_OPTIONS.map((option) => (
        <MenuItem
          key={option.value}
          value={option.value}
          sx={{
            backgroundColor: option.color,
            color: 'white',
            '&:hover': {
              backgroundColor: option.color,
              opacity: 0.9,
            },
            '&.Mui-selected': {
              backgroundColor: option.color,
            },
          }}
        >
          {option.label}
        </MenuItem>
      ))}
    </Select>
  );
}
