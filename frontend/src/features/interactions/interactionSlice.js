import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/interactions/');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch interactions');
    }
  }
);

export const fetchInteractionById = createAsyncThunk(
  'interactions/fetchById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.get(`/interactions/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch interaction');
    }
  }
);

export const createInteraction = createAsyncThunk(
  'interactions/create',
  async (interactionData, { rejectWithValue }) => {
    try {
      const response = await api.post('/interactions/', interactionData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create interaction');
    }
  }
);

export const updateInteraction = createAsyncThunk(
  'interactions/update',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/interactions/${id}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update interaction');
    }
  }
);

const initialState = {
  interactions: [],
  current: null,
  loading: false,
  error: null,
  // Added for ChatPanel -> Form communication
  aiExtractedData: null,
};

const interactionSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    setAiExtractedData: (state, action) => {
      state.aiExtractedData = action.payload;
    },
    clearCurrent: (state) => {
      state.current = null;
      state.aiExtractedData = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchInteractions.fulfilled, (state, action) => { state.loading = false; state.interactions = action.payload; })
      .addCase(fetchInteractions.rejected, (state, action) => { state.loading = false; state.error = action.payload; })
      
      .addCase(fetchInteractionById.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchInteractionById.fulfilled, (state, action) => { state.loading = false; state.current = action.payload; })
      .addCase(fetchInteractionById.rejected, (state, action) => { state.loading = false; state.error = action.payload; })

      .addCase(createInteraction.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(createInteraction.fulfilled, (state, action) => { 
        state.loading = false; 
        state.interactions.unshift(action.payload);
        state.aiExtractedData = null;
      })
      .addCase(createInteraction.rejected, (state, action) => { state.loading = false; state.error = action.payload; })

      .addCase(updateInteraction.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.interactions.findIndex(i => i.id === action.payload.id);
        if (index !== -1) {
          state.interactions[index] = action.payload;
        }
      })
      .addCase(updateInteraction.rejected, (state, action) => { state.loading = false; state.error = action.payload; });
  },
});

export const { setAiExtractedData, clearCurrent } = interactionSlice.actions;
export default interactionSlice.reducer;
