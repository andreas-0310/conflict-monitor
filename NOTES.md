# Design Decisions and Tradeoffs

## Database

### SQLite Choice
- **Decision**: Used SQLite as the database for simplicity and ease of deployment
- **Tradeoff**: SQLite is perfect for local development and simple deployments, but has limitations in high-concurrency scenarios. For production, PostgreSQL or MySQL would be better choices for better concurrency handling and performance.

### Indexing Strategy
- **Decision**: Added indexes on frequently queried columns (country, admin1, user_id) and a composite index on (country, admin1) for efficient lookups
- **Rationale**: 
  - Single-column indexes on `country` and `admin1` for filtering queries
  - Composite index on (country, admin1) for DELETE endpoint lookups
  - Indexes on foreign keys (user_id) for JOIN operations
  - All indexes are created automatically by SQLAlchemy from model definitions
- **Tradeoff**: More indexes mean slower writes, but significantly faster reads. Given this is a read-heavy application, the tradeoff is beneficial.

### Query Optimization
- **Decision**: Used SQLAlchemy ORM with explicit queries to avoid N+1 problems
- **Implementation**: 
  - Used `.filter().in_()` for multiple country queries instead of multiple queries
  - Used bulk operations for data loading
  - Proper use of transactions for data integrity
- **Tradeoff**: ORM adds some overhead compared to raw SQL, but provides better security (SQL injection prevention) and maintainability.

## Authentication

### JWT Tokens
- **Decision**: Implemented JWT-based authentication for stateless, scalable authentication
- **Tradeoff**: JWT tokens cannot be revoked until expiry. For production with strict security requirements, consider implementing token blacklisting or using refresh tokens with shorter access token lifetimes.

### Password Hashing
- **Decision**: Used bcrypt via passlib for password hashing
- **Rationale**: bcrypt is industry standard, secure, and has built-in salt generation
- **Tradeoff**: bcrypt is slower than simpler hashing algorithms, but this is a feature (makes brute-force attacks harder), not a bug.

### Admin Functionality
- **Decision**: Added `is_admin` boolean flag to User model
- **Tradeoff**: Simple but effective for basic use cases. For more complex permission systems, consider role-based access control (RBAC) with a separate roles/permissions table.

## API Design

### RESTful Endpoints
- **Decision**: Followed REST principles for endpoint design
- **Rationale**: RESTful APIs are predictable, well-understood, and work well with standard HTTP methods
- **Note**: The DELETE endpoint uses a request body instead of path parameters, which is less RESTful but allows for more complex deletion criteria. This is a common pattern when deletion requires multiple identifiers.

### Pagination
- **Decision**: Implemented offset-based pagination with configurable page size
- **Tradeoff**: Offset-based pagination is simple and works well for moderate datasets, but cursor-based pagination would be better for very large datasets (millions of records) as it avoids performance issues with large offsets.

### Multiple Countries Support
- **Decision**: Allowed comma-separated country names in the GET /conflictdata/{country} endpoint
- **Rationale**: More flexible than requiring separate requests for each country
- **Tradeoff**: Slightly more complex parsing, but provides better user experience

### Background Jobs
- **Decision**: Implemented risk score calculation using background job pattern with `asyncio.run_in_executor()`
- **Current Implementation**: Calculation runs in a background executor thread, demonstrating the background job pattern. The function creates its own database session for thread safety.
- **Implementation Details**: 
  - Uses `asyncio.run_in_executor()` to run calculation in background thread
  - Background function (`calculate_average_risk_score_background`) creates its own DB session
  - Result is rounded to 2 decimal places
- **For Production**: For heavy workloads or distributed systems, consider Celery with Redis/RabbitMQ for true distributed task processing
- **Tradeoff**: Background executor pattern allows non-blocking calculation while still returning results. For fire-and-forget operations, FastAPI BackgroundTasks would be more appropriate.

## Validation

### Input Validation
- **Decision**: Used Pydantic models for request/response validation
- **Rationale**: Automatic validation, type checking, and clear error messages
- **Tradeoff**: Pydantic adds some overhead, but the benefits (type safety, automatic validation, clear errors) far outweigh the minimal performance cost.

### Feedback Text Length
- **Decision**: Enforced 10-500 character limit on feedback text
- **Implementation**: Used both Pydantic Field constraints and custom validator
- **Tradeoff**: Strict validation may reject some valid use cases, but ensures data quality and prevents abuse.

## Error Handling

### HTTP Status Codes
- **Decision**: Used appropriate HTTP status codes (400, 401, 403, 404, 422)
- **Rationale**: Follows HTTP standards for better API clarity
- **Tradeoff**: More status codes to handle on the client side, but provides better API usability.

### Error Messages
- **Decision**: Provided descriptive error messages in responses
- **Tradeoff**: More verbose responses, but significantly better developer experience and debugging.

## Data Loading

### CSV Import
- **Decision**: Created a separate script for loading CSV data
- **Rationale**: Separates data loading from application code, allows for easy re-imports
- **Implementation**: Used bulk operations for efficiency
- **Tradeoff**: Manual step required, but provides flexibility and avoids coupling data loading with application startup.

## Security Considerations

### SQL Injection Prevention
- **Decision**: Used SQLAlchemy ORM exclusively (no raw SQL queries)
- **Rationale**: ORM automatically parameterizes queries, preventing SQL injection
- **Tradeoff**: ORM has slight performance overhead, but security is worth it.

### Secret Key Management
- **Decision**: Used environment variables for sensitive configuration (via pydantic-settings)
- **Rationale**: Best practice for configuration management
- **For Production**: Use secure secret management (AWS Secrets Manager, HashiCorp Vault, etc.)

### Password Requirements
- **Decision**: Password length validation (6-11 characters) implemented
- **Rationale**: Balances security with usability. The length limit is within bcrypt's 72-byte limit.
- **Tradeoff**: Length-only validation is simpler but less secure than complexity requirements. For production, consider adding requirements for uppercase, lowercase, numbers, and special characters.

## Testing Strategy

### No Unit Tests Included
- **Decision**: Focused on implementation rather than testing for this exercise
- **For Production**: Should include:
  - Unit tests for business logic
  - Integration tests for API endpoints
  - Database migration tests
  - Security tests (authentication, authorization)

## Future Improvements

1. **Database Migrations**: Add Alembic for database version control
2. **Caching**: Add Redis caching for frequently accessed data (risk scores, country lists)
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Logging**: Add structured logging (e.g., using Python's logging module with JSON formatter)
5. **Monitoring**: Add health check endpoints and metrics collection
6. **API Versioning**: Consider API versioning strategy for future changes
7. **Documentation**: Consider adding more detailed API documentation with examples
8. **Data Export**: Add endpoints for exporting data in different formats (JSON, CSV)
9. **Search/Filtering**: Add advanced search and filtering capabilities
10. **Audit Logging**: Track changes to conflict data for compliance/auditing

