import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Login — backend sets httpOnly cookies, returns { success, message }
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/signin', credentials);
      return response.data; // { success: true, message: "Login successful" }
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

// Get current user profile
export const fetchUser = createAsyncThunk(
  'auth/fetchUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/auth/me');
      return response.data.data; // Extracts the user object from the response data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user');
    }
  }
);

// Sign Up — creates the account
export const signupUser = createAsyncThunk(
  'auth/signupUser',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/signup', userData);
      return response.data; // { success: true, message: "Account Created Successfully!" }
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Signup failed');
    }
  }
);

// Logout — calls backend to revoke refresh token & clear cookies
export const logoutUser = createAsyncThunk(
  'auth/logoutUser',
  async (_, { rejectWithValue }) => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Even if it fails, clear local state
    }
  }
);

// Persist auth state in sessionStorage so page refresh doesn't log out the user
const isAuthFromStorage = sessionStorage.getItem('isAuthenticated') === 'true';

const initialState = {
  isAuthenticated: isAuthFromStorage,
  user: null, // Holds user profile details
  loading: false,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Direct logout action for immediate local-only logout
    clearAuth: (state) => {
      state.isAuthenticated = false;
      sessionStorage.removeItem('isAuthenticated');
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state) => {
        state.loading = false;
        state.isAuthenticated = true;
        sessionStorage.setItem('isAuthenticated', 'true');
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Signup
    builder
      .addCase(signupUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(signupUser.fulfilled, (state) => {
        state.loading = false;
        // Don't auto-login — redirect to login page
      })
      .addCase(signupUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Logout
    builder
      .addCase(logoutUser.fulfilled, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        sessionStorage.removeItem('isAuthenticated');
      });

    // Fetch User
    builder
      .addCase(fetchUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true; // ensure they're authenticated if fetch succeeds
        sessionStorage.setItem('isAuthenticated', 'true');
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.loading = false;
        // Optionally handle logout on fetch user failure (e.g. invalid token)
      });
  },
});

export const { clearAuth } = authSlice.actions;
export default authSlice.reducer;
