const API_URL = process.env.REACT_APP_API_URL || 'http://89.169.150.10:8000';

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: `${API_URL}/api/v1/auth/login`,
        REGISTER: `${API_URL}/api/v1/auth/register`,
        ME: `${API_URL}/api/v1/auth/me`,
    },
    USERS: {
        ME: `${API_URL}/api/v1/users/me`,
    },
    PROJECTS: {
        LIST: `${API_URL}/api/v1/projects`,
        SEARCH: `${API_URL}/api/v1/projects/search`,
        DETAIL: (id) => `${API_URL}/api/v1/projects/${id}`,
    },
    LIKES: {
        PROJECT: (id) => `${API_URL}/api/v1/likes/project/${id}`,
        USER: (id) => `${API_URL}/api/v1/likes/user/${id}`,
    },
    MATCHES: {
        LIST: `${API_URL}/api/v1/matches`,
        POTENTIAL: `${API_URL}/api/v1/matches/potential`,
    },
};

export default API_ENDPOINTS; 