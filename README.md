# URL Shorty

URL Shorty is a lightweight RESTful API for creating and managing shortened URLs. Users can define custom short codes using words, making links easy to remember and share.

## Features

- Create short URLs with custom codes
- Read original URLs by short code
- Update URL for existing short code
- Delete URLs
- List all stored URLs

## API Endpoints

- `GET /` - Server and DB health check
- `GET /url/list/` - List all URLs
- `POST /url/shorten/` - Create a new short URL
- `GET /url/shortCode` - Retrieve original URL
- `PATCH /url/shortCode` - Update an existing short URL
- `DELETE /url/shortCode` - Delete a short URL

## Tech Stack

- FastAPI 
- SQLModel
- Pydantic
- PostGreSql