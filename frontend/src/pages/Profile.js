import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Chip,
  Avatar,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    bio: '',
    skills: '',
    experience: '',
  });

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(response.data.user);
      setFormData({
        full_name: response.data.user.full_name || '',
        bio: response.data.user.bio || '',
        skills: response.data.user.skills || '',
        experience: response.data.user.experience || '',
      });
    } catch (err) {
      setError('Failed to fetch user data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        'http://localhost:8000/api/v1/users/me',
        formData,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setEditMode(false);
      fetchUserData();
    } catch (err) {
      setError('Failed to update profile');
    }
  };

  const renderSkills = (skills) => {
    if (!skills) return null;
    try {
      const skillsArray = typeof skills === 'string' ? JSON.parse(skills) : skills;
      return skillsArray.map((skill, index) => (
        <Chip
          key={index}
          label={skill}
          sx={{ mr: 1, mb: 1 }}
          variant="outlined"
        />
      ));
    } catch (e) {
      return <Typography variant="body2">{skills}</Typography>;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Profile
      </Typography>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" mb={3}>
            <Avatar
              sx={{ width: 100, height: 100 }}
              alt={user?.full_name}
            >
              {user?.full_name?.[0] || user?.username?.[0]}
            </Avatar>
          </Box>

          {editMode ? (
            <form onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Full Name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleInputChange}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Bio"
                    name="bio"
                    value={formData.bio}
                    onChange={handleInputChange}
                    multiline
                    rows={4}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Skills (comma-separated)"
                    name="skills"
                    value={formData.skills}
                    onChange={handleInputChange}
                    helperText="Enter your skills separated by commas"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Experience"
                    name="experience"
                    value={formData.experience}
                    onChange={handleInputChange}
                    multiline
                    rows={4}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Box display="flex" gap={2}>
                    <Button
                      variant="contained"
                      color="primary"
                      type="submit"
                    >
                      Save Changes
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => setEditMode(false)}
                    >
                      Cancel
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </form>
          ) : (
            <>
              <Typography variant="h5" align="center" gutterBottom>
                {user?.full_name}
              </Typography>
              <Typography variant="subtitle1" align="center" color="textSecondary" gutterBottom>
                @{user?.username}
              </Typography>
              {user?.bio && (
                <Typography variant="body1" paragraph>
                  {user.bio}
                </Typography>
              )}
              {user?.skills && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Skills
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    {renderSkills(user.skills)}
                  </Box>
                </>
              )}
              {user?.experience && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Experience
                  </Typography>
                  <Typography variant="body2" paragraph>
                    {user.experience}
                  </Typography>
                </>
              )}
              <Box display="flex" justifyContent="center" mt={2}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => setEditMode(true)}
                >
                  Edit Profile
                </Button>
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default Profile; 