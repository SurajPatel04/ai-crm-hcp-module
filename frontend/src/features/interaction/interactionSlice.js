import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    hcp_name: '',
    date: '',
    sentiment: '',
    products: [],
    materials_shared: [],
    notes: '',
    summary: '',
    interaction_id: null,
    loading: false,
    error: null,
};

const interactionSlice = createSlice({
    name: 'interaction',
    initialState,
    reducers: {
        // Fill entire form (used by log_interaction tool)
        setInteractionData: (state, action) => {
            return { ...state, ...action.payload };
        },

        // Update only specific fields (used by edit_interaction tool)
        updateInteractionFields: (state, action) => {
            return { ...state, ...action.payload };
        },

        // Reset form
        resetInteraction: () => initialState,

        setLoading: (state, action) => {
            state.loading = action.payload;
        },

        setError: (state, action) => {
            state.error = action.payload;
        },
    },
});

export const {
    setInteractionData,
    updateInteractionFields,
    resetInteraction,
    setLoading,
    setError,
} = interactionSlice.actions;

export default interactionSlice.reducer;