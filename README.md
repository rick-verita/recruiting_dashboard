# Internal Recruiting Dashboard

An internal tool for monitoring and managing job applications. The system monitors a Gmail inbox for incoming applications, parses them using AI, and provides a dashboard for reviewing candidates.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Frontend**: React with Vite
- **Database**: PostgreSQL 16
- **AI**: OpenAI GPT-4 for email parsing
- **Email**: Gmail API integration

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Gmail API credentials
- OpenAI API key

## Setup

1. Clone the repository

2. Copy the environment file and configure it:
   ```bash
   cp .env.example .env
   ```

3. Configure the following in `.env`:
   - `DATABASE_URL` - PostgreSQL connection string
   - `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN` - Gmail API credentials
   - `OPENAI_API_KEY` - OpenAI API key

4. Start the services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

## Development

### Backend

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run the API server
uvicorn src.email_parser.api:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Services

| Service  | Port | Description           |
|----------|------|-----------------------|
| API      | 8000 | FastAPI backend       |
| Frontend | 8585 | React dashboard       |
| Postgres | 5433 | Database (mapped)     |

## License

Internal use only.
