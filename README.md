# Conflict Monitor API

A FastAPI-based REST API for monitoring conflicts in different countries, supporting user authentication, conflict data retrieval, and user feedback submission.

## Features

- **JWT-based Authentication**: Secure user registration and login
- **Conflict Data Management**: View and manage conflict data for different countries
- **User Feedback**: Submit feedback on admin1 regions (authentication required)
- **Admin Functions**: Delete conflict data entries (admin only)
- **Background Jobs**: Calculate average risk scores using background tasks
- **Efficient Database Queries**: Optimized with proper indexing to avoid N+1 queries
- **Pagination**: Efficient data retrieval with pagination support

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd conflict-monitor
   ```

2. **Create a virtual environment** (if not already created):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the database and load sample data**:
   ```bash
   python -m app.load_data sample_data.csv
   ```

6. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

7. **Access the API documentation**:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Documentation

### Authentication

All authentication endpoints are prefixed with `/auth`.

#### Register User
- **Endpoint**: `POST /auth/register`
- **Description**: Register a new user
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string (email format)",
    "password": "string (6-11 characters)"
  }
  ```
- **Response**: User object (201 Created)
- **Error Responses**:
  - 400: Username or email already exists, or password validation failed (must be 6-11 characters)
  - 422: Validation error (password length)

#### Login
- **Endpoint**: `POST /auth/login`
- **Description**: Login and receive JWT access token
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```
- **Error Responses**:
  - 401: Incorrect username or password

#### Get Current User
- **Endpoint**: `GET /auth/me`
- **Description**: Get current authenticated user information
- **Headers**: `Authorization: Bearer <token>`
- **Response**: User object
- **Error Responses**:
  - 401: Not authenticated

### Conflict Data

All conflict data endpoints are prefixed with `/conflictdata`.

#### List Conflict Data
- **Endpoint**: `GET /conflictdata`
- **Description**: List conflict data grouped by country with pagination (default 20 countries per page). Each country includes all its admin1 entries.
- **Query Parameters**:
  - `page` (int, optional): Page number (default: 1)
  - `page_size` (int, optional): Number of countries per page (default: 20)
- **Response**:
  ```json
  {
    "items": [
      {
        "country": "Afghanistan",
        "admin1_details": [
          {
            "admin1": "Kabul",
            "score": 7.8,
            "population": 4635000,
            "events": 245
          },
          {
            "admin1": "Kandahar",
            "score": 8.2,
            "population": 1235000,
            "events": 189
          }
        ]
      }
    ],
    "total": 239,
    "page": 1,
    "page_size": 20,
    "total_pages": 12
  }
  ```

#### Get Conflict Data by Country
- **Endpoint**: `GET /conflictdata/{country}`
- **Description**: Get conflict data for specific country/countries. Supports multiple countries (comma-separated)
- **Path Parameters**:
  - `country` (string): Country name(s), comma-separated for multiple countries
- **Response**: Array of country detail objects with admin1 details
  ```json
  [
    {
      "country": "Afghanistan",
      "admin1_details": [
        {
          "admin1": "Kabul",
          "score": 7.8,
          "population": 4635000,
          "events": 245
        }
      ]
    }
  ]
  ```
- **Error Responses**:
  - 404: Country not found

#### Get Average Risk Score
- **Endpoint**: `GET /conflictdata/{country}/riskscore`
- **Description**: Get average risk score for a country (calculated using background job). The score is rounded to 2 decimal places.
- **Path Parameters**:
  - `country` (string): Country name
- **Response**:
  ```json
  {
    "country": "Afghanistan",
    "average_risk_score": 7.63,
    "calculated_at": "2024-01-01T12:00:00"
  }
  ```
- **Note**: The calculation runs in a background executor using asyncio, demonstrating the background job pattern. The result is rounded to 2 decimal places.
- **Error Responses**:
  - 404: Country not found

#### Submit User Feedback
- **Endpoint**: `POST /conflictdata/{admin1}/userfeedback`
- **Description**: Submit feedback about an admin1 region (authentication required)
- **Authentication**: Required (JWT token)
- **Path Parameters**:
  - `admin1` (string): Admin1 region name
- **Request Body**:
  ```json
  {
    "feedback_text": "string (10-500 characters)"
  }
  ```
- **Response**: Feedback object (201 Created)
- **Error Responses**:
  - 401: Not authenticated
  - 404: Admin1 not found
  - 422: Validation error (feedback text length)

#### Delete Conflict Data (Admin Only)
- **Endpoint**: `DELETE /conflictdata`
- **Description**: Delete conflict data entry by country and admin1 (admin only)
- **Authentication**: Required (JWT token, admin user)
- **Request Body**:
  ```json
  {
    "country": "string",
    "admin1": "string"
  }
  ```
- **Response**: 204 No Content
- **Error Responses**:
  - 401: Not authenticated
  - 403: Not enough permissions (not admin)
  - 404: Entry not found

## Example Requests

### Using cURL

#### Register a user:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test1234"
  }'
```

#### Login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test1234"
  }'
```

#### Get conflict data (with pagination):
```bash
curl -X GET "http://localhost:8000/conflictdata?page=1&page_size=20"
```

#### Get conflict data by country:
```bash
curl -X GET "http://localhost:8000/conflictdata/Afghanistan"
```

#### Get multiple countries:
```bash
curl -X GET "http://localhost:8000/conflictdata/Afghanistan,Syria,Iraq"
```

#### Get average risk score:
```bash
curl -X GET "http://localhost:8000/conflictdata/Afghanistan/riskscore"
```

#### Submit feedback (authenticated):
```bash
curl -X POST "http://localhost:8000/conflictdata/Kabul/userfeedback" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "feedback_text": "This is my feedback about the Kabul region. It should be at least 10 characters."
  }'
```

#### Delete conflict data (admin only):
```bash
curl -X DELETE "http://localhost:8000/conflictdata" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -d '{
    "country": "Afghanistan",
    "admin1": "Kabul"
  }'
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "test1234"  # Password must be 6-11 characters
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "testuser",
    "password": "test1234"  # Password must be 6-11 characters
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get conflict data
response = requests.get(f"{BASE_URL}/conflictdata?page=1&page_size=20")
print(response.json())

# Submit feedback
response = requests.post(
    f"{BASE_URL}/conflictdata/Kabul/userfeedback",
    headers=headers,
    json={"feedback_text": "This is my detailed feedback about Kabul region."}
)
print(response.json())
```

## Database Design

### Tables

1. **users**
   - id (Primary Key)
   - username (Unique, Indexed)
   - email (Unique, Indexed)
   - hashed_password
   - is_admin (Boolean)
   - created_at

2. **conflict_data**
   - id (Primary Key)
   - country (Indexed)
   - admin1 (Indexed)
   - population (Float, nullable)
   - events (Integer)
   - score (Float)
   - Indexes: country, admin1, composite (country, admin1)

3. **user_feedback**
   - id (Primary Key)
   - user_id (Foreign Key to users, Indexed)
   - admin1 (Indexed)
   - country
   - feedback_text
   - created_at
   - Indexes: user_id, admin1

### Indexing Strategy

- Single-column indexes on frequently filtered columns (country, admin1, user_id)
- Composite index on (country, admin1) for efficient lookups
- All foreign keys are indexed
- Prevents N+1 query problems through proper query design (using `.filter().in_()` for batch queries)

### Query Optimization

- **N+1 Prevention**: All queries use batch operations (`.filter().in_()`) instead of loops with individual queries
  - `GET /conflictdata`: Fetches all countries' data in a single query using `.filter().in_()`, then groups in memory
  - `GET /conflictdata/{country}`: Uses `.in_()` for multiple countries in one query
  - No relationship lazy loading issues - all data fetched upfront
- **Efficient Pagination**: Uses offset/limit for pagination, with single queries for all data
- **Aggregate Functions**: Uses SQL aggregate functions (`func.avg()`) for calculations
- **Transaction Management**: All write operations use proper transaction handling with rollback on errors
  - Write operations (register, feedback, delete) have try/except blocks with `db.rollback()` on errors
  - Ensures data integrity and prevents partial commits

## Security Features

- **Password Hashing**: Uses bcrypt directly for secure password storage (6-11 character validation)
- **JWT Authentication**: Secure token-based authentication using HTTPBearer for Swagger UI token input
- **SQL Injection Prevention**: Uses SQLAlchemy ORM with parameterized queries (all queries are parameterized automatically)
- **Input Validation**: Pydantic models for request/response validation
- **Admin Protection**: Separate dependency for admin-only endpoints
- **Transaction Safety**: Proper transaction handling with rollback on errors for all write operations

## Design Decisions and Tradeoffs

### Database Choice
- **SQLite**: Chosen for simplicity and ease of deployment. For production, consider PostgreSQL or MySQL for better concurrency and performance.
- **Tradeoff**: SQLite has limitations in high-concurrency scenarios but is perfect for local development and simple deployments.

### Authentication
- **JWT**: Chosen for stateless authentication, allowing easy scalability.
- **Tradeoff**: Tokens cannot be revoked until expiry. For production, consider token blacklisting or refresh tokens.

### Background Jobs
- **Implementation**: Risk score calculation uses `asyncio.run_in_executor()` to run in a background thread, demonstrating the background job pattern.
- **Tradeoff**: For production with heavy workloads, consider Celery with Redis/RabbitMQ for distributed task processing, or FastAPI BackgroundTasks for fire-and-forget operations.

### Pagination
- **Offset-based**: Simple and effective for moderate datasets.
- **Tradeoff**: Cursor-based pagination would be better for very large datasets, but offset-based is simpler to implement and understand.

### API Design
- **RESTful**: Follows REST principles for clarity and predictability.
- **Error Handling**: Comprehensive error responses with appropriate HTTP status codes.

## Environment Variables

Create a `.env` file in the project root to customize settings. You can use `.env.example` as a template:

```env
DATABASE_URL=sqlite:///./conflict_monitor.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: 
- The `.env` file is gitignored and should not be committed to version control
- Change the `SECRET_KEY` to a strong random value in production
- You can generate a secure key using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## Testing

To test the API:

1. Start the server: `uvicorn app.main:app --reload`
2. Visit `http://localhost:8000/docs` for interactive API documentation
3. Use the Swagger UI to test all endpoints
4. Or use the cURL/Python examples provided above

### Authorizing in Swagger UI

To use authenticated endpoints in Swagger UI:

1. First, login using the `POST /auth/login` endpoint to get your access token
2. Click the **"Authorize"** button (lock icon) at the top right of the Swagger UI
3. In the authorization dialog, you'll see a "Value" field
4. Paste your access token (just the token string, without "Bearer")
5. Click **"Authorize"** and then **"Close"**
6. Now all protected endpoints will automatically include your token in requests

**Note**: The API uses HTTPBearer authentication, which provides a simple token input field in Swagger UI for easy testing.

## License

This project is created for a home exercise.

