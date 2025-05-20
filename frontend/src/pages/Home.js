import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import API_ENDPOINTS from '../config';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Avatar,
  TextField,
  CircularProgress
} from '@mui/material';

const Home = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchUserData = async () => {
      try {
        const response = await axios.get(API_ENDPOINTS.AUTH.ME, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        setUser(response.data.user);
      } catch (err) {
        setError('Failed to fetch user data');
        if (err.response?.status === 401) {
          localStorage.removeItem('token');
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Grid container spacing={3}>
          {/* Profile Section */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" flexDirection="column" alignItems="center">
                  <Avatar
                    sx={{ width: 100, height: 100, mb: 2 }}
                    alt={user?.username}
                    src={`https://ui-avatars.com/api/?name=${user?.username}&background=random`}
                  />
                  <Typography variant="h5" gutterBottom>
                    {user?.full_name || user?.username}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    @{user?.username}
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {user?.bio || 'No bio provided'}
                  </Typography>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={handleLogout}
                    sx={{ mt: 2 }}
                  >
                    Logout
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Main Content */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Skills
                </Typography>
                <Typography variant="body1" paragraph>
                  {user?.skills || 'No skills listed'}
                </Typography>

                <Typography variant="h6" gutterBottom>
                  Experience
                </Typography>
                <Typography variant="body1">
                  {user?.experience || 'No experience listed'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Home;

