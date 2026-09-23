# Library Management API

A RESTful backend API for managing a library system. The application provides functionality for user authentication, role-based access control, book management, and book borrowing and returning.

The project was built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, and **JWT-based authentication**.

---

## Overview

The Library Management API is a backend application designed to handle the core operations of a library system.

Users can create accounts, authenticate using JWT tokens, view available books, borrow books, return borrowed books, and view their borrowing history.

The system also supports different user roles. Regular members can interact with books and their own borrowing records, while administrators have additional permissions for managing the library's book collection.

The project was built as a practical backend development project to apply concepts such as:

- REST API development
- Authentication and authorization
- Role-based access control
- Relational database design
- SQLAlchemy ORM
- Database migrations with Alembic
- Dependency injection with FastAPI
- Password hashing and JWT authentication
- API testing with Postman
- Linux server deployment

---

## Features

### User Authentication

The API provides authentication functionality for registered users.

Users can:

- Register an account
- Log in with their credentials
- Receive a JWT access token
- Use the access token to access protected endpoints

Authentication is handled using JWT tokens, while passwords are securely hashed rather than stored as plain text.

---

### Role-Based Access Control

The application supports different user roles.

#### Member

Regular registered users can:

- View books
- Borrow available books
- Return books they have borrowed
- View their borrowing history

New users are assigned the `member` role by default.

#### Admin

Administrators have additional permissions for managing the library.

Admins can:

- Add new books
- Manage the library's book collection
- Access functionality restricted to administrative users

Administrative endpoints verify the authenticated user's role before allowing the requested operation.

---

## Book Management

The API manages books and keeps track of their availability.

Each book contains information such as:

- ID
- Title
- Author
- ISBN
- Total copies
- Available copies
- Active status
- Creation timestamp
- Update timestamp

The application distinguishes between the **total number of copies** owned by the library and the **number of copies currently available for borrowing**.

For example:

```text
Total copies:     10
Available copies: 9
```

This means the library owns 10 copies of the book and currently has 9 available because one copy is being borrowed.

When a book is borrowed:

```text
available_copies -= 1
```

When a book is returned:

```text
available_copies += 1
```

This allows the system to keep track of the current inventory of each book.

---

## Borrowing System

Authenticated members can borrow books through the API.

Before creating a borrowing record, the application checks that:

1. The user is authenticated.
2. The requested book exists.
3. The book is available.
4. The user does not already have an active borrowing record for the same book.

When a book is successfully borrowed:

- A borrowing record is created.
- The available copy count is decreased.
- The borrowing date is recorded.
- A due date is stored.

When a book is returned:

- The borrowing record is marked as returned.
- The return timestamp is recorded.
- The available copy count is increased.

A borrowing record uses `returned_at` to determine whether the borrowing is still active.

For example:

```text
returned_at = NULL
```

means the book has not yet been returned.

A populated `returned_at` value means the book has been returned.

---

## Borrowing History

Users can view their own borrowing history.

The borrowing records contain information such as:

- Borrowing ID
- Book
- User
- Borrowed date
- Due date
- Return date

This allows the API to distinguish between active and completed borrowing transactions.

---

## Technology Stack

| Technology | Purpose                                 |
| ---------- | --------------------------------------- |
| Python     | Programming language                    |
| FastAPI    | Web framework for building the REST API |
| PostgreSQL | Relational database                     |
| SQLAlchemy | ORM and database interaction            |
| Alembic    | Database migrations                     |
| Pydantic   | Data validation and serialization       |
| JWT        | Authentication tokens                   |
| OAuth2     | Authentication flow                     |
| Postman    | API testing                             |
| Git        | Version control                         |
| GitHub     | Source code hosting                     |
| Ubuntu     | Linux server environment                |

---

## Project Architecture

The application follows a modular structure where different responsibilities are separated into different modules.

A simplified version of the project structure looks like:

```text
library-management-api/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── oauth2.py
│   ├── config.py
│   │
│   └── routers/
│       ├── auth.py
│       ├── user.py
│       ├── book.py
│       └── borrowing.py
│
├── alembic/
│   ├── versions/
│   └── ...
│
├── alembic.ini
├── requirements.txt
├── .env
└── README.md
```

> The exact structure may vary depending on the current version of the project.

### Main Components

#### `main.py`

The main entry point of the FastAPI application.

It creates the FastAPI application and registers the different API routers.

---

#### `database.py`

Responsible for database configuration and SQLAlchemy session management.

It contains the database connection configuration and the `get_db` dependency used by API routes to obtain database sessions.

---

#### `models.py`

Contains the SQLAlchemy database models.

The main models include:

- `User`
- `Book`
- `Borrowing`

These models represent the application's database tables and their relationships.

---

#### `schemas.py`

Contains Pydantic schemas used for:

- Request validation
- Response serialization
- Defining the expected structure of API data

---

#### `oauth2.py`

Contains authentication-related functionality, including:

- OAuth2 password authentication
- JWT token creation
- Retrieving the currently authenticated user
- Protecting API endpoints

---

#### `config.py`

Contains application configuration and environment-based settings.

Sensitive configuration values such as database credentials and JWT configuration are loaded from environment variables rather than being hard-coded into the application.

---

#### `routers/`

The router modules organize API endpoints by functionality.

```text
auth.py
```

Handles registration and authentication.

```text
user.py
```

Handles user-related functionality.

```text
book.py
```

Handles book-related operations.

```text
borrowing.py
```

Handles borrowing and returning books.

---

## Database Relationships

The application uses PostgreSQL as its relational database.

The main relationships are:

```text
User
 │
 │ 1
 │
 │
 │ many
 ▼
Borrowing
 │
 │ many
 │
 │ 1
 ▼
Book
```

A user can have multiple borrowing records.

A book can appear in multiple borrowing records over time.

Each borrowing record belongs to one user and one book.

This allows the system to preserve the history of previous borrowing transactions rather than creating a separate record for every copy of a book.

---

## Authentication Flow

The authentication process works approximately as follows:

```text
User Registration
       │
       ▼
User stored in database
       │
       ▼
User Login
       │
       ▼
Credentials verified
       │
       ▼
JWT Access Token Created
       │
       ▼
Client sends token
       │
       ▼
Protected API Endpoint
       │
       ▼
Token verified
       │
       ▼
Current user identified
       │
       ▼
Request allowed
```

Protected endpoints use FastAPI dependencies to verify the authenticated user before allowing access.

Administrative endpoints perform an additional role check.

---

## API Endpoints

### Authentication

| Method | Endpoint          | Description                                 |
| ------ | ----------------- | ------------------------------------------- |
| `POST` | `/users/register` | Register a new user                         |
| `POST` | `/auth/login`     | Authenticate a user and receive a JWT token |

### Books

| Method | Endpoint | Description    | Access              |
| ------ | -------- | -------------- | ------------------- |
| `GET`  | `/books` | View books     | Authenticated users |
| `POST` | `/books` | Add a new book | Admin               |

### Borrowings

| Method | Endpoint                            | Description                | Access              |
| ------ | ----------------------------------- | -------------------------- | ------------------- |
| `POST` | `/borrowings`                       | Borrow a book              | Authenticated users |
| `GET`  | `/borrowings/me`                    | View own borrowing history | Authenticated users |
| `PUT`  | `/borrowings/{borrowing_id}/return` | Return a borrowed book     | Authenticated users |
| `GET`  | `/borrowings`                       | View borrowing records     | Authenticated users |

> Endpoint paths and access rules should be updated in this README if the API changes.

---

## Environment Variables

The application uses environment variables for configuration and sensitive information.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/library_management

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

The actual `.env` file should **not** be committed to GitHub.

A production environment should use its own secure values for database credentials and JWT secrets.

---

## Running the Project Locally

### 1. Clone the repository

```bash
git clone git@github.com:NiyatHannibal/library-management-api.git
```

Move into the project directory:

```bash
cd library-management-api
```

---

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file and provide the required database and authentication settings.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/library_management
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

### 5. Run database migrations

Apply the existing Alembic migrations:

```bash
alembic upgrade head
```

This creates or updates the database schema according to the migration history.

---

### 6. Start the FastAPI application

Run the development server with:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI also provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## Database Migrations

Alembic is used to manage changes to the PostgreSQL database schema.

After making changes to SQLAlchemy models, a migration can be generated with:

```bash
alembic revision --autogenerate -m "describe your change"
```

The migration can then be applied with:

```bash
alembic upgrade head
```

The migration history allows the database schema to be changed in a controlled and reproducible way.

---

## Testing

The API has been tested using **Postman**.

Testing includes functionality such as:

- User registration
- User authentication
- JWT-protected routes
- Admin authorization
- Book creation
- Book retrieval
- Book borrowing
- Book returning
- Borrowing history

The API can also be tested through FastAPI's automatically generated Swagger documentation at:

```text
/docs
```

---

## Security Considerations

The application follows several basic security practices:

- Passwords are hashed before being stored.
- JWT tokens are used for authenticated requests.
- Protected routes require authentication.
- Administrative operations require the appropriate role.
- Database credentials are stored through environment variables.
- Sensitive `.env` files should not be committed to version control.

For production deployment, additional security measures should be considered, including:

- HTTPS
- Secure secret management
- Production database credentials
- Proper CORS configuration
- Firewall configuration
- Secure server configuration
- Reverse proxy configuration

---

## Deployment

The application is being prepared for deployment on a Linux server environment using Ubuntu.

The deployment process includes:

```text
GitHub Repository
       │
       ▼
Ubuntu Server
       │
       ▼
Clone Project
       │
       ▼
Python Environment
       │
       ▼
PostgreSQL
       │
       ▼
Environment Configuration
       │
       ▼
Alembic Migrations
       │
       ▼
FastAPI Application
       │
       ▼
Application Server
       │
       ▼
Nginx Reverse Proxy
       │
       ▼
Internet
```

The deployment setup is intended to provide experience with running a Python backend application in a Linux production environment.

---

## What I Learned From This Project

This project was built to practice backend development concepts beyond simply writing API endpoints.

Key areas practiced include:

- Designing a relational database
- Creating SQLAlchemy models
- Working with PostgreSQL
- Building RESTful APIs with FastAPI
- Validating request and response data with Pydantic
- Implementing JWT authentication
- Implementing role-based authorization
- Managing database relationships
- Managing database schema changes with Alembic
- Handling business logic for borrowing and returning books
- Testing APIs using Postman
- Using Git and GitHub for version control
- Working with Linux and Ubuntu
- Preparing a backend application for deployment

---

## Future Improvements

Possible future improvements include:

- Book search and filtering
- Pagination for book and borrowing lists
- Admin user management
- Updating and deleting books
- Borrowing due-date validation
- Overdue borrowing detection
- Book reservation functionality
- Automated tests with `pytest`
- Improved error handling
- API rate limiting
- Production logging
- CI/CD automation
- Containerization with Docker

---

## Project Status

**Current status:** Backend functionality implemented and tested locally.

The project is currently being prepared for deployment on an Ubuntu server.

The deployment phase is being used to practice:

- Linux server administration
- SSH
- Git-based deployment
- Python application setup
- PostgreSQL configuration
- Environment configuration
- Database migrations
- Application servers
- Nginx reverse proxy configuration
