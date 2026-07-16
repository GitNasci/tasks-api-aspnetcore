# Tasks API

A RESTful task management API developed with ASP.NET Core 8, Entity Framework Core and SQLite.

## Features

- Create, retrieve, update and delete tasks
- DTO-based request validation
- SQLite data persistence
- Entity Framework Core migrations
- Repository pattern
- Dependency injection
- Asynchronous database operations
- Automated repository tests with xUnit
- Docker support with persistent storage

## Technologies

- C#
- .NET 8
- ASP.NET Core Web API
- Entity Framework Core
- SQLite
- xUnit
- Docker
- Swagger / OpenAPI
- Git

## Architecture

```text
HTTP Client
    ↓
TasksController
    ↓
ITaskRepository
    ↓
EfTaskRepository
    ↓
TasksDbContext
    ↓
SQLite
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/Tasks` | Retrieve all tasks |
| GET | `/api/Tasks/{id}` | Retrieve a task by ID |
| POST | `/api/Tasks` | Create a task |
| PUT | `/api/Tasks/{id}` | Update a task |
| DELETE | `/api/Tasks/{id}` | Delete a task |

## Example request

```json
{
  "title": "Prepare interview",
  "description": "Study ASP.NET Core and REST APIs",
  "isCompleted": false
}
```

## Run locally

### Requirements

- .NET 8 SDK
- Git

Clone the repository and restore its dependencies:

```bash
dotnet restore
```

Run the API:

```bash
dotnet run --project TasksApi
```

Open the Swagger interface using the address displayed in the terminal:

```text
http://localhost:<port>/swagger
```

The SQLite database is created and updated automatically using Entity Framework Core migrations.

## Run the tests

```bash
dotnet test
```

The tests use an isolated in-memory SQLite database and do not modify the application database.

## Run with Docker

Build the image:

```bash
docker build -t tasks-api .
```

Run the container with a persistent Docker volume:

```bash
docker run --rm --name tasks-api -p 8080:8080 -e ASPNETCORE_ENVIRONMENT=Development -e "ConnectionStrings__TasksDatabase=Data Source=/app/data/tasks.db" -v tasks-api-data:/app/data tasks-api
```

Open:

```text
http://localhost:8080/swagger
```

## Project structure

```text
TasksApiSolution/
├── TasksApi/
│   ├── Controllers/
│   ├── Data/
│   ├── Dtos/
│   ├── Migrations/
│   ├── Models/
│   └── Repositories/
├── TasksApi.Tests/
├── Dockerfile
├── .dockerignore
└── TasksApiSolution.sln
```

## Author

Diogo Nascimento  
