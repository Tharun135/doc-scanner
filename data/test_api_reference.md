# API Reference Documentation

## Overview

The XYZ API provides programmatic access to system features and data.

## Authentication

All API requests require authentication using JWT tokens.

Tokens can be obtained by sending credentials to the /auth/login endpoint.

## Endpoints

### GET /api/users

Returns a list of users in the system.

Parameters:
- limit (optional): Maximum number of results
- offset (optional): Number of results to skip

Response:
```json
{
  "users": [],
  "total": 0
}
```

### POST /api/users

Creates a new user in the system.

Request body:
- username (required): User's login name
- email (required): User's email address
- role (optional): User role (default: "user")

HTTP status codes:
- 200: User created successfully
- 400: Invalid request data
- 401: Authentication required
- 403: Insufficient permissions

### PUT /api/users/:id

The user profile will be updated with the provided data.

### DELETE /api/users/:id

Removes a user from the system. This action cannot be undone.

## Rate Limiting

API requests are limited to 1000 requests per hour per API key.

Exceeding the rate limit will result in HTTP 429 responses.

## Error Handling

All errors return a standard error response format.

The error message should be displayed to the user for debugging purposes.
