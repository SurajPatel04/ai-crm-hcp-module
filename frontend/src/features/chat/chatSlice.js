import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    messages: [],
    isTyping: false,
};

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        // Add user or AI message
        addMessage: (state, action) => {
            state.messages.push(action.payload);
        },

        setTyping: (state, action) => {
            state.isTyping = action.payload;
        },

        clearChat: (state) => {
            state.messages = [];
        },
    },
});

export const {
    addMessage,
    setTyping,
    clearChat,
} = chatSlice.actions;

export default chatSlice.reducer;