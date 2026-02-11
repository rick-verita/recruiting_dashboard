import { useState, useCallback } from 'react';
import {
  DataGrid,
  GridColDef,
  GridPaginationModel,
  GridSortModel,
  GridRenderCellParams,
  GridRowSelectionModel,
} from '@mui/x-data-grid';
import {
  Box,
  Paper,
  Typography,
  Link,
  TextField,
  IconButton,
  Menu,
  MenuItem,
  Button,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { format } from 'date-fns';
import {
  Message,
  MessageFilters,
  ApplicationStatus,
  STATUS_OPTIONS,
  SOURCE_OPTIONS,
} from '../../types';
import {
  useMessages,
  useUpdateMessage,
  useBulkUpdateMessageStatus,
} from '../../hooks/useMessages';
import StatusSelect from '../ApplicationsTable/StatusSelect';
import FilterToolbar from './FilterToolbar';

export default function MessagesTable() {
  const [filters, setFilters] = useState<MessageFilters>({
    page: 1,
    page_size: 25,
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  const [editingCommentId, setEditingCommentId] = useState<number | null>(null);
  const [editingCommentValue, setEditingCommentValue] = useState('');
  const [selectedRows, setSelectedRows] = useState<GridRowSelectionModel>([]);
  const [bulkMenuAnchor, setBulkMenuAnchor] = useState<null | HTMLElement>(null);

  const { data, isLoading, error } = useMessages(filters);
  const updateMutation = useUpdateMessage();
  const bulkUpdateMutation = useBulkUpdateMessageStatus();

  const handleFiltersChange = useCallback((newFilters: Partial<MessageFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  }, []);

  const handlePaginationChange = useCallback((model: GridPaginationModel) => {
    setFilters((prev) => ({
      ...prev,
      page: model.page + 1,
      page_size: model.pageSize,
    }));
  }, []);

  const handleSortChange = useCallback((model: GridSortModel) => {
    if (model.length > 0) {
      setFilters((prev) => ({
        ...prev,
        sort_by: model[0].field,
        sort_order: model[0].sort || 'desc',
      }));
    }
  }, []);

  const handleStatusChange = useCallback(
    (id: number, status: ApplicationStatus) => {
      updateMutation.mutate({ id, update: { status } });
    },
    [updateMutation]
  );

  const handleCommentEdit = useCallback((id: number, currentComment: string | null) => {
    setEditingCommentId(id);
    setEditingCommentValue(currentComment || '');
  }, []);

  const handleCommentSave = useCallback(
    (id: number) => {
      updateMutation.mutate(
        { id, update: { comments: editingCommentValue } },
        {
          onSuccess: () => {
            setEditingCommentId(null);
            setEditingCommentValue('');
          },
        }
      );
    },
    [updateMutation, editingCommentValue]
  );

  const handleCommentCancel = useCallback(() => {
    setEditingCommentId(null);
    setEditingCommentValue('');
  }, []);

  const handleBulkStatusChange = useCallback(
    (status: ApplicationStatus) => {
      bulkUpdateMutation.mutate({
        ids: selectedRows as number[],
        status,
      });
      setBulkMenuAnchor(null);
      setSelectedRows([]);
    },
    [bulkUpdateMutation, selectedRows]
  );

  const columns: GridColDef<Message>[] = [
    {
      field: 'applicant_name',
      headerName: 'Applicant',
      flex: 1,
      minWidth: 150,
    },
    {
      field: 'position_titles',
      headerName: 'Position(s)',
      flex: 1.5,
      minWidth: 200,
    },
    {
      field: 'source',
      headerName: 'Source',
      width: 150,
      valueGetter: (params) => {
        const option = SOURCE_OPTIONS.find((o) => o.value === params.row.source);
        return option?.label || params.row.source;
      },
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 150,
      renderCell: (params: GridRenderCellParams<Message>) => (
        <StatusSelect
          value={params.row.status}
          onChange={(status) => handleStatusChange(params.row.id, status)}
          disabled={updateMutation.isPending}
        />
      ),
    },
    {
      field: 'comments',
      headerName: 'Comments',
      flex: 2,
      minWidth: 250,
      renderCell: (params: GridRenderCellParams<Message>) => {
        const isEditing = editingCommentId === params.row.id;

        if (isEditing) {
          return (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
              <TextField
                size="small"
                value={editingCommentValue}
                onChange={(e) => setEditingCommentValue(e.target.value)}
                fullWidth
                autoFocus
                multiline
                maxRows={3}
              />
              <IconButton
                size="small"
                color="primary"
                onClick={() => handleCommentSave(params.row.id)}
              >
                <CheckIcon />
              </IconButton>
              <IconButton size="small" onClick={handleCommentCancel}>
                <CloseIcon />
              </IconButton>
            </Box>
          );
        }

        return (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              width: '100%',
              cursor: 'pointer',
            }}
            onClick={() => handleCommentEdit(params.row.id, params.row.comments)}
          >
            <Typography
              variant="body2"
              sx={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                flex: 1,
                color: params.row.comments ? 'inherit' : 'text.disabled',
              }}
            >
              {params.row.comments || 'Click to add comment...'}
            </Typography>
            <IconButton size="small" sx={{ opacity: 0.5 }}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Box>
        );
      },
    },
    {
      field: 'email',
      headerName: 'Contact',
      width: 180,
      renderCell: (params: GridRenderCellParams<Message>) => {
        const row = params.row;
        if (row.email) {
          return (
            <Link href={`mailto:${row.email}`}>
              {row.email}
            </Link>
          );
        }
        if (row.message_link) {
          return (
            <Link href={row.message_link} target="_blank" rel="noopener">
              View message
            </Link>
          );
        }
        return null;
      },
    },
    {
      field: 'received_at',
      headerName: 'Date',
      width: 120,
      valueGetter: (params) =>
        params.row.received_at
          ? format(new Date(params.row.received_at), 'MMM d, yyyy')
          : '',
    },
  ];

  if (error) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="error">
          Error loading messages: {String(error)}
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">Messages</Typography>
        {selectedRows.length > 0 && (
          <Box>
            <Button
              variant="contained"
              endIcon={<MoreVertIcon />}
              onClick={(e) => setBulkMenuAnchor(e.currentTarget)}
            >
              Bulk Actions ({selectedRows.length})
            </Button>
            <Menu
              anchorEl={bulkMenuAnchor}
              open={Boolean(bulkMenuAnchor)}
              onClose={() => setBulkMenuAnchor(null)}
            >
              {STATUS_OPTIONS.map((option) => (
                <MenuItem
                  key={option.value}
                  onClick={() => handleBulkStatusChange(option.value)}
                >
                  Set to {option.label}
                </MenuItem>
              ))}
            </Menu>
          </Box>
        )}
      </Box>

      <FilterToolbar filters={filters} onFiltersChange={handleFiltersChange} />

      <Paper sx={{ height: 'calc(100vh - 280px)', width: '100%' }}>
        <DataGrid
          rows={data?.items || []}
          columns={columns}
          loading={isLoading}
          rowCount={data?.total || 0}
          pageSizeOptions={[10, 25, 50, 100]}
          paginationModel={{
            page: filters.page - 1,
            pageSize: filters.page_size,
          }}
          paginationMode="server"
          sortingMode="server"
          onPaginationModelChange={handlePaginationChange}
          onSortModelChange={handleSortChange}
          checkboxSelection
          rowSelectionModel={selectedRows}
          onRowSelectionModelChange={setSelectedRows}
          disableRowSelectionOnClick
          getRowHeight={() => 'auto'}
          sx={{
            '& .MuiDataGrid-cell': {
              py: 1,
            },
          }}
        />
      </Paper>
    </Box>
  );
}
