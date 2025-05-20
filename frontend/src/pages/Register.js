import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Link,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import axios from 'axios';
import API_ENDPOINTS from '../config';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    bio: '',
    skills: '',
    experience: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log('Sending registration data:', formData);
      const response = await axios.post(API_ENDPOINTS.AUTH.REGISTER, formData);
      console.log('Registration response:', response.data);
      localStorage.setItem('token', response.data.access_token);
      navigate('/');
    } catch (err) {
      console.error('Registration error:', err.response?.data);
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          // Handle validation errors
          const errorMessages = err.response.data.detail.map(error => {
            const field = error.loc[error.loc.length - 1];
            return `${field}: ${error.msg}`;
          });
          setError(errorMessages.join('\n'));
        } else {
          // Handle other errors
          setError(err.response.data.detail);
        }
      } else {
        setError('An error occurred during registration');
      }
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Register
          </Typography>
          {error && (
            <Typography color="error" align="center" gutterBottom>
              {error}
            </Typography>
          )}
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Full Name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Bio"
              name="bio"
              multiline
              rows={4}
              value={formData.bio}
              onChange={handleChange}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Skills (comma-separated)"
              name="skills"
              value={formData.skills}
              onChange={handleChange}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Experience"
              name="experience"
              multiline
              rows={4}
              value={formData.experience}
              onChange={handleChange}
              margin="normal"
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              sx={{ mt: 3 }}
            >
              Register
            </Button>
          </form>
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Link component={RouterLink} to="/login">
              Already have an account? Login
            </Link>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register; 