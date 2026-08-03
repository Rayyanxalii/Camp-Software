# ERR-EMR Backend Quick Start Guide

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
uv sync
```

### 2. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your PostgreSQL connection string
# Example:
# DATABASE_URL=postgresql://user:password@localhost:5432/err_emr_db
```

### 3. Ensure PostgreSQL is Running
```bash
# On macOS with Homebrew
brew services start postgresql

# On Linux
sudo systemctl start postgresql

# On Windows or using Docker
docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
```

### 4. Run the Application
```bash
# Development with hot reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (no reload)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Testing an Endpoint

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "AdminPassword123"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "AdminPassword123"
  }'
```

### 3. Use the Token
```bash
# Get current user
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

# Create a patient
curl -X POST "http://localhost:8000/api/v1/patients" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "national_id": "12345678",
    "phone": "5551234567"
  }'
```

## Project Structure

### Models (Database Layer)
- `app/models/patient.py` - Patient demographics
- `app/models/user.py` - User authentication and RBAC
- `app/models/visit.py` - Medical visits and dental records
- `app/models/stock.py` - Inventory management

### Schemas (Validation Layer)
- `app/schemas/auth.py` - Authentication schemas
- `app/schemas/patient.py` - Patient request/response models
- `app/schemas/visit.py` - Visit data validation
- `app/schemas/stock.py` - Inventory schemas
- `app/schemas/analytics.py` - Analytics models
- `app/schemas/uploads.py` - File upload schemas

### Routers (API Endpoints)
- `app/routers/auth.py` - Authentication endpoints
- `app/routers/patients.py` - Patient CRUD operations
- `app/routers/visits.py` - General visit management
- `app/routers/dental_visits.py` - Dental visit management
- `app/routers/stock.py` - Inventory management
- `app/routers/lookup.py` - Reference data and search
- `app/routers/analytics.py` - Reporting and analytics
- `app/routers/uploads.py` - File management

### Core Configuration
- `app/main.py` - FastAPI app setup
- `app/config.py` - Environment configuration
- `app/database.py` - SQLAlchemy setup
- `app/security.py` - Password and JWT utilities
- `app/dependencies.py` - Authentication middleware

## Database Schema

The application uses 8 tables:

1. **patients** - Patient demographics
2. **users** - User accounts
3. **roles** - Role definitions
4. **permissions** - Permission definitions
5. **user_role** - User-role association (many-to-many)
6. **role_permission** - Role-permission association (many-to-many)
7. **visits** - Medical visit records
8. **dental_visits** - Dental visit records
9. **stock** - Inventory items
10. **stock_transactions** - Inventory movement history

## API Endpoints Overview

### Authentication (5 endpoints)
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- GET /api/v1/auth/me
- POST /api/v1/auth/register
- POST /api/v1/auth/refresh

### Patients (6 endpoints)
- GET /api/v1/patients
- GET /api/v1/patients/search
- GET /api/v1/patients/{id}
- POST /api/v1/patients
- PUT /api/v1/patients/{id}
- DELETE /api/v1/patients/{id}

### Visits (5 endpoints)
- GET /api/v1/visits
- GET /api/v1/visits/{id}
- POST /api/v1/visits
- PUT /api/v1/visits/{id}
- DELETE /api/v1/visits/{id}

### Dental Visits (5 endpoints)
- GET /api/v1/dental-visits
- GET /api/v1/dental-visits/{id}
- POST /api/v1/dental-visits
- PUT /api/v1/dental-visits/{id}
- DELETE /api/v1/dental-visits/{id}

### Stock (8 endpoints)
- GET /api/v1/stock
- GET /api/v1/stock/low-stock
- GET /api/v1/stock/{id}
- POST /api/v1/stock
- PUT /api/v1/stock/{id}
- POST /api/v1/stock/import
- POST /api/v1/stock/deduct
- DELETE /api/v1/stock/{id}

### Lookup (4 endpoints)
- GET /api/v1/lookup/icd-diagnosis
- GET /api/v1/lookup/icd-symptoms
- GET /api/v1/lookup/recent-diagnoses
- GET /api/v1/lookup/common-procedures

### Analytics (6 endpoints)
- GET /api/v1/analytics/summary
- GET /api/v1/analytics/visits-by-doctor
- GET /api/v1/analytics/gender-age-distribution
- GET /api/v1/analytics/revenue-metrics
- GET /api/v1/analytics/common-diagnoses
- GET /api/v1/analytics/stock-utilization

### Uploads (4 endpoints)
- POST /api/v1/uploads/images
- GET /api/v1/uploads/images/{filename}
- GET /api/v1/uploads/images
- DELETE /api/v1/uploads/images/{filename}

### System (2 endpoints)
- GET / - Health check
- GET /health - Load balancer check

**Total: 49 API endpoints**

## Troubleshooting

### Database Connection Error
```
psycopg2.OperationalError: connection to server at "localhost" failed
```
**Solution**: Ensure PostgreSQL is running and DATABASE_URL in .env is correct

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**: Change port: `uvicorn app.main:app --port 8001`

### Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Run `uv sync` to install dependencies

## Development Tips

### Code Formatting
```bash
uv run black app/
```

### Linting
```bash
uv run ruff check app/
```

### Type Checking
```bash
uv run mypy app/
```

### Running Tests
```bash
uv run pytest tests/ -v
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| DEBUG | No | false | Enable debug mode |
| ENVIRONMENT | No | development | Environment name |
| APP_NAME | No | ERR-EMR Backend | Application name |
| SECRET_KEY | Yes | - | JWT secret key (change in production) |
| ALGORITHM | No | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | 30 | Token expiration time |
| CORS_ORIGINS | No | ["http://localhost:3000"] | Allowed CORS origins |
| UPLOAD_DIR | No | uploads | Upload directory path |
| MAX_UPLOAD_SIZE | No | 10485760 | Max file size in bytes |

## Next Steps

1. **Database Migrations**: Set up Alembic for schema versioning
2. **Testing**: Write unit and integration tests
3. **Services Layer**: Extract business logic into services
4. **Documentation**: Generate API documentation
5. **Deployment**: Docker setup and CI/CD pipeline
6. **Monitoring**: Add logging and monitoring capabilities

---

For detailed implementation information, see `IMPLEMENTATION_SUMMARY.md`
