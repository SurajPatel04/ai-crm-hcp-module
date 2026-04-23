import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { signupUser } from './authSlice';

const SignUp = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state) => state.auth);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const isMismatch = formData.confirmPassword.length > 0 && formData.password !== formData.confirmPassword;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isMismatch) return;

    const resultAction = await dispatch(signupUser({
      full_name: formData.full_name,
      email: formData.email,
      password: formData.password,
    }));

    if (signupUser.fulfilled.match(resultAction)) {
      navigate('/login', { replace: true });
    }
  };

  return (
    <div className="login-container">
      <div className="card login-card" style={{ maxWidth: '450px' }}>
        <h2 style={{ marginBottom: '0.5rem', textAlign: 'center', fontSize: '1.5rem' }}>
          Create account
        </h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '2rem' }}>
          Join the HCP CRM platform
        </p>

        {error && (
          <div style={{
            color: 'var(--error)',
            backgroundColor: '#FEF2F2',
            border: '1px solid #FECACA',
            borderRadius: '6px',
            padding: '0.75rem 1rem',
            marginBottom: '1.25rem',
            fontSize: '0.875rem',
            fontWeight: 500,
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="full_name">Full Name</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              placeholder="John Doe"
              autoComplete="name"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="you@example.com"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="••••••••"
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label
              className="form-label"
              htmlFor="confirmPassword"
              style={{ color: isMismatch ? 'var(--error)' : '' }}
            >
              Re-type Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              placeholder="••••••••"
              autoComplete="new-password"
              style={{
                borderColor: isMismatch ? 'var(--error)' : 'var(--border-color)',
                backgroundColor: isMismatch ? '#FEF2F2' : 'var(--card-bg)',
              }}
            />
            {isMismatch && (
              <p style={{ color: 'var(--error)', fontSize: '0.75rem', marginTop: '0.35rem', fontWeight: 500 }}>
                Passwords do not match
              </p>
            )}
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', marginTop: '0.5rem' }}
            disabled={loading || isMismatch}
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>

          <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ fontWeight: 600, color: 'var(--primary)' }}>Sign In</Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SignUp;
