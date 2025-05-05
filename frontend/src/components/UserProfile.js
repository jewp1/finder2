import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  Avatar,
} from '@mui/material';
import { ThumbUp, ThumbDown } from '@mui/icons-material';

const UserProfile = ({ user, onLike, onDislike, isLiked, isDisliked }) => {
  return (
    <Card sx={{ maxWidth: 600, mx: 'auto', my: 2 }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar
            sx={{ width: 80, height: 80, mr: 2 }}
            alt={user.username}
            src={`https://ui-avatars.com/api/?name=${user.username}&background=random`}
          />
          <Box>
            <Typography variant="h5" gutterBottom>
              {user.full_name}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              @{user.username}
            </Typography>
          </Box>
        </Box>

        <Typography variant="body1" paragraph>
          {user.bio || 'No bio provided'}
        </Typography>

        {user.skills && (
          <Box mb={2}>
            <Typography variant="subtitle1" gutterBottom>
              Skills:
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {user.skills.split(',').map((skill, index) => (
                <Chip
                  key={index}
                  label={skill.trim()}
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}

        {user.experience && (
          <Box mb={2}>
            <Typography variant="subtitle1" gutterBottom>
              Experience:
            </Typography>
            <Typography variant="body2">
              {user.experience}
            </Typography>
          </Box>
        )}

        <Box display="flex" justifyContent="center" gap={2} mt={2}>
          <Button
            variant={isLiked ? "contained" : "outlined"}
            color="primary"
            startIcon={<ThumbUp />}
            onClick={() => onLike(user.id)}
            disabled={isLiked || isDisliked}
          >
            Like
          </Button>
          <Button
            variant={isDisliked ? "contained" : "outlined"}
            color="error"
            startIcon={<ThumbDown />}
            onClick={() => onDislike(user.id)}
            disabled={isLiked || isDisliked}
          >
            Dislike
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default UserProfile; 