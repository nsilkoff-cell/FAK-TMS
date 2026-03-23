# Local Development Setup

## Prerequisites

Ensure you have installed:
- **Docker** & **Docker Compose** – [Install](https://docs.docker.com/get-docker/)
- **Git** – [Install](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- **Python 3.9+** – [Install](https://www.python.org/downloads/)
- **Node.js 16+** – [Install](https://nodejs.org/)

## Quick Start (Docker Compose)

The easiest way to get the full stack running locally:
```bash
# Clone the repository
git clone https://github.com/nsilkoff-cell/FAK-TMS.git
cd FAK-TMS

# Start all services (backend, database, frontend)
docker-compose up

# Wait for services to be ready (~30 seconds)
# You'll see logs indicating each service is running
```

**Services will be available at:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Database**: postgres://localhost:5432/faktms

## Manual Setup (Without Docker)

### 1. Set Up PostgreSQL Database
```bash
# macOS (Homebrew)
brew install postgresql
brew services start postgresql

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
createdb faktms
```

### 2. Set Up Backend
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://localhost/faktms"
export DEBUG=true

# Run migrations (once we have them)
# python -m alembic upgrade head

# Start backend server
python -m uvicorn app.main:app --reload

# Backend will run on http://localhost:8000
```

### 3. Set Up Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will run on http://localhost:3000
```

## Environment Variables

Create a `.env` file in the project root:
```
# Backend
DATABASE_URL=postgresql://localhost/faktms
DEBUG=true
API_PORT=8000

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Integrations (add once you have API keys)
HIGHWAY_API_KEY=your_key_here
TEAMS_BOT_TOKEN=your_token_here
FRONT_API_KEY=your_key_here
FAK_API_URL=your_fak_url_here
```

## Development Workflow

### Making Backend Changes
```bash
cd backend
source venv/bin/activate

# Make your changes to Python files
# Uvicorn with --reload will automatically restart the server

# Run tests (once we have them)
pytest
```

### Making Frontend Changes
```bash
cd frontend

# Make your changes to React files
# Vite will hot-reload automatically in the browser
```

### Database Migrations
```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Debugging

### Backend Logs

If running with Docker:
```bash
docker-compose logs backend --follow
```

If running manually:
```bash
# Check terminal where you ran `uvicorn`
```

### Frontend Logs
```bash
# Check browser console (F12 or Cmd+Option+I)
# Check terminal where you ran `npm run dev`
```

### Database Connection Issues
```bash
# Test connection to PostgreSQL
psql postgresql://localhost/faktms

# If it fails, check:
# 1. Is PostgreSQL running? (systemctl status postgresql)
# 2. Does database exist? (psql -l)
# 3. Are credentials correct in .env?
```

## Stopping the Stack

### Docker Compose
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

### Manual Setup
```bash
# Kill the backend process (Ctrl+C in the terminal)
# Kill the frontend process (Ctrl+C in the terminal)
# Stop PostgreSQL: brew services stop postgresql (macOS)
```

## Troubleshooting

### "postgres: command not found"
- Install PostgreSQL: `brew install postgresql` (macOS) or `sudo apt-get install postgresql` (Linux)

### "ModuleNotFoundError: No module named 'fastapi'"
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### "Cannot connect to database"
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env is correct
- Verify database exists: `psql -l | grep faktms`

### Frontend shows "Cannot reach API"
- Check backend is running on http://localhost:8000
- Verify REACT_APP_API_URL in .env matches backend URL
- Check browser console (F12) for CORS errors

### Port already in use
```bash
# Find process using port 8000 (backend)
lsof -i :8000
# Kill it: kill -9 <PID>

# Find process using port 3000 (frontend)
lsof -i :3000
# Kill it: kill -9 <PID>
```

## Next Steps

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
2. Read [MODULES.md](MODULES.md) for detailed module descriptions
3. Check out [API_SPEC.md](API_SPEC.md) for API endpoints
4. Start coding! Begin with backend models and API routes.

---

**Need help?** Open an issue on GitHub or check the [docs](/) folder.