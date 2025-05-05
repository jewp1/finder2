import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Chip,
  Button,
  Grid,
  Divider,
} from '@mui/material';
import axios from 'axios';

const ProjectDetail = () => {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProject();
  }, [id]);

  const fetchProject = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/v1/projects/${id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setProject(response.data);
    } catch (err) {
      setError('Failed to fetch project details');
    }
  };

  const handleLike = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `http://localhost:8000/api/v1/likes/project/${id}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      fetchProject();
    } catch (err) {
      setError('Failed to like project');
    }
  };

  if (!project) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography color="error">{error || 'Loading...'}</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h4" gutterBottom>
              {project.title}
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Chip
                label={`Status: ${project.status}`}
                color={project.status === 'open' ? 'success' : 'default'}
                sx={{ mr: 1 }}
              />
              <Chip
                label={`Budget: ${project.budget}`}
                color="primary"
                sx={{ mr: 1 }}
              />
              <Chip label={`Duration: ${project.duration}`} color="primary" />
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Description
            </Typography>
            <Typography paragraph>{project.description}</Typography>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Requirements
            </Typography>
            <Box sx={{ mb: 2 }}>
              {project.requirements &&
                JSON.parse(project.requirements).map((req, index) => (
                  <Chip
                    key={index}
                    label={req}
                    sx={{ mr: 1, mb: 1 }}
                    variant="outlined"
                  />
                ))}
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Project Owner
            </Typography>
            <Typography>
              {project.owner?.full_name || 'Anonymous'}
            </Typography>
            {project.owner?.bio && (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {project.owner.bio}
              </Typography>
            )}
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                color="secondary"
                onClick={handleLike}
                sx={{ mr: 2 }}
              >
                Like Project
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default ProjectDetail; 