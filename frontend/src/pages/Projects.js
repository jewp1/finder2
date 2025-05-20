import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  TextField,
  Box,
  Chip,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import axios from 'axios';
import API_ENDPOINTS from '../config';

const Projects = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [newProject, setNewProject] = useState({
    title: '',
    description: '',
    requirements: '',
    budget: '',
    duration: '',
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(API_ENDPOINTS.PROJECTS.LIST, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProjects(response.data || []);
    } catch (err) {
      setError('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_ENDPOINTS.PROJECTS.SEARCH}?q=${searchQuery}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setProjects(response.data || []);
    } catch (err) {
      setError('Failed to search projects');
    }
  };

  const handleLike = async (projectId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        API_ENDPOINTS.LIKES.PROJECT(projectId),
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      fetchProjects();
    } catch (err) {
      setError('Failed to like project');
    }
  };

  const handleCreateProject = async () => {
    try {
      const token = localStorage.getItem('token');
      const projectData = {
        ...newProject,
        requirements: newProject.requirements
          ? newProject.requirements.split(',').map(r => r.trim()).filter(r => r)
          : [],
      };
      
      await axios.post(
        API_ENDPOINTS.PROJECTS.LIST,
        projectData,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setOpenDialog(false);
      setNewProject({
        title: '',
        description: '',
        requirements: '',
        budget: '',
        duration: '',
      });
      fetchProjects();
    } catch (err) {
      setError('Failed to create project');
      console.error('Error creating project:', err.response?.data || err);
    }
  };

  const renderRequirements = (requirements) => {
    if (!requirements) return null;
    try {
      const requirementsArray = typeof requirements === 'string' ? JSON.parse(requirements) : requirements;
      return requirementsArray.map((req, index) => (
        <Chip
          key={index}
          label={req}
          sx={{ mr: 1, mb: 1 }}
          variant="outlined"
        />
      ));
    } catch (e) {
      return <Typography variant="body2">{requirements}</Typography>;
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4">
          Projects
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create Project
        </Button>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={8}>
            <TextField
              fullWidth
              label="Search Projects"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </Box>

      {projects.length === 0 ? (
        <Typography variant="body1" align="center">
          No projects found
        </Typography>
      ) : (
        <Grid container spacing={3}>
          {projects.map((project) => (
            <Grid item xs={12} sm={6} md={4} key={project.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {project.title}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="textSecondary"
                    sx={{
                      mb: 2,
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}
                  >
                    {project.description}
                  </Typography>
                  <Box sx={{ mb: 1 }}>
                    <Chip
                      label={`Budget: ${project.budget}`}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Chip
                      label={`Duration: ${project.duration}`}
                      size="small"
                    />
                  </Box>
                  {project.requirements && (
                    <Box sx={{ mt: 1 }}>
                      {renderRequirements(project.requirements)}
                    </Box>
                  )}
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    color="primary"
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    View Details
                  </Button>
                  <Button
                    size="small"
                    color="secondary"
                    onClick={() => handleLike(project.id)}
                  >
                    Like
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Project</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Title"
              value={newProject.title}
              onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description"
              value={newProject.description}
              onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
              multiline
              rows={4}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Requirements (comma-separated)"
              value={newProject.requirements}
              onChange={(e) => setNewProject({ ...newProject, requirements: e.target.value })}
              helperText="Enter requirements separated by commas"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Budget"
              value={newProject.budget}
              onChange={(e) => setNewProject({ ...newProject, budget: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Duration"
              value={newProject.duration}
              onChange={(e) => setNewProject({ ...newProject, duration: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateProject} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Projects; 