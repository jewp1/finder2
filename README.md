# Project Finder

A client-server platform for matching specialists with projects using semantic search and mutual likes.

## Project Structure

```
proj-finder/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   ├── tests/        # Backend tests
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/         # Source code
│   ├── public/      # Static files
│   └── package.json
└── docker/          # Docker configuration
```

## Technologies

### Backend
- FastAPI (Python)
- SQLAlchemy
- Pydantic
- PostgreSQL
- Redis
- Celery
- Sentence Transformers

### Frontend
- React
- Material-UI
- Axios
- React Router

## Setup Instructions

### Backend Setup
1. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup
1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm start
```

## Development

- Backend API documentation will be available at `http://localhost:8000/docs`
- Frontend development server will run at `http://localhost:3000`

## License

MIT 