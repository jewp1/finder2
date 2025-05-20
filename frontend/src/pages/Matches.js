import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Avatar,
  IconButton,
} from '@mui/material';
import { Favorite, Close } from '@mui/icons-material';
import axios from 'axios';
import API_ENDPOINTS from '../config';

const Matches = () => {
  const [potentialMatches, setPotentialMatches] = useState([]);
  const [currentMatch, setCurrentMatch] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPotentialMatches();
    fetchMatches();
  }, []);

  const fetchPotentialMatches = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(API_ENDPOINTS.MATCHES.POTENTIAL, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPotentialMatches(response.data);
      if (response.data.length > 0) {
        setCurrentMatch(response.data[0]);
      }
    } catch (err) {
      setError('Failed to fetch potential matches');
    } finally {
      setLoading(false);
    }
  };

  const fetchMatches = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(API_ENDPOINTS.MATCHES.LIST, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMatches(response.data);
    } catch (err) {
      setError('Failed to fetch matches');
    }
  };

  const handleLike = async () => {
    if (!currentMatch) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        API_ENDPOINTS.LIKES.USER(currentMatch.id),
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      // Remove current match and show next one
      setPotentialMatches(potentialMatches.slice(1));
      if (potentialMatches.length > 1) {
        setCurrentMatch(potentialMatches[1]);
      } else {
        setCurrentMatch(null);
      }
      fetchMatches();
    } catch (err) {
      setError('Failed to like user');
    }
  };

  const handleDislike = () => {
    // Remove current match and show next one
    setPotentialMatches(potentialMatches.slice(1));
    if (potentialMatches.length > 1) {
      setCurrentMatch(potentialMatches[1]);
    } else {
      setCurrentMatch(null);
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

  const renderMatch = (match) => {
    if (match.user) {
      return (
        <Card key={match.id} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Avatar
                sx={{ width: 50, height: 50, mr: 2 }}
                alt={match.user.full_name || match.user.username}
              >
                {(match.user.full_name?.[0] || match.user.username?.[0] || '?').toUpperCase()}
              </Avatar>
              <Box>
                <Typography variant="h6">
                  {match.user.full_name || match.user.username}
                </Typography>
                <Typography variant="subtitle2" color="textSecondary">
                  @{match.user.username}
                </Typography>
              </Box>
            </Box>
            {match.user.bio && (
              <Typography variant="body2" paragraph>
                {match.user.bio}
              </Typography>
            )}
            <Chip
              label={`Status: ${match.status}`}
              color={
                match.status === 'accepted'
                  ? 'success'
                  : match.status === 'rejected'
                  ? 'error'
                  : 'default'
              }
            />
          </CardContent>
        </Card>
      );
    } else if (match.project) {
      return (
        <Card key={match.id} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {match.project.title}
            </Typography>
            <Typography variant="body2" paragraph>
              {match.project.description}
            </Typography>
            {match.project.requirements && (
              <Box sx={{ mb: 2 }}>
                {renderSkills(match.project.requirements)}
              </Box>
            )}
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body2" color="textSecondary">
                Budget: {match.project.budget}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Duration: {match.project.duration}
              </Typography>
            </Box>
            <Chip
              label={`Status: ${match.status}`}
              color={
                match.status === 'accepted'
                  ? 'success'
                  : match.status === 'rejected'
                  ? 'error'
                  : 'default'
              }
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>
      );
    }
    return null;
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
        Find Your Match
      </Typography>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Grid container spacing={3}>
        {/* Potential Matches */}
        <Grid item xs={12} md={6}>
          <Typography variant="h5" gutterBottom>
            Potential Matches
          </Typography>
          {!currentMatch ? (
            <Typography variant="body1" align="center">
              No more potential matches. Check back later!
            </Typography>
          ) : (
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="center" mb={2}>
                  <Avatar
                    sx={{ width: 100, height: 100 }}
                    alt={currentMatch.full_name || currentMatch.username}
                  >
                    {(currentMatch.full_name?.[0] || currentMatch.username?.[0] || '?').toUpperCase()}
                  </Avatar>
                </Box>
                <Typography variant="h5" align="center" gutterBottom>
                  {currentMatch.full_name || currentMatch.username}
                </Typography>
                <Typography variant="subtitle1" align="center" color="textSecondary" gutterBottom>
                  @{currentMatch.username}
                </Typography>
                {currentMatch.bio && (
                  <Typography variant="body1" paragraph>
                    {currentMatch.bio}
                  </Typography>
                )}
                {currentMatch.skills && (
                  <>
                    <Typography variant="h6" gutterBottom>
                      Skills
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      {renderSkills(currentMatch.skills)}
                    </Box>
                  </>
                )}
                {currentMatch.experience && (
                  <>
                    <Typography variant="h6" gutterBottom>
                      Experience
                    </Typography>
                    <Typography variant="body2" paragraph>
                      {currentMatch.experience}
                    </Typography>
                  </>
                )}
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                <IconButton
                  color="error"
                  size="large"
                  onClick={handleDislike}
                  sx={{ mr: 2 }}
                >
                  <Close fontSize="large" />
                </IconButton>
                <IconButton
                  color="primary"
                  size="large"
                  onClick={handleLike}
                >
                  <Favorite fontSize="large" />
                </IconButton>
              </CardActions>
            </Card>
          )}
        </Grid>

        {/* Current Matches */}
        <Grid item xs={12} md={6}>
          <Typography variant="h5" gutterBottom>
            Your Matches
          </Typography>
          {matches.length === 0 ? (
            <Typography variant="body1" align="center">
              No matches yet. Start liking users to get matches!
            </Typography>
          ) : (
            matches.map(renderMatch)
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default Matches; 