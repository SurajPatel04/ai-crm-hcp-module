import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import interactionReducer from '../features/interactions/interactionSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    interactions: interactionReducer,
  },
});