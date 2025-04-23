# URL Shorty

**URL Shorty** is a lightweight RESTful API that lets users create and manage shortened URLs. It supports **custom short codes** using human-friendly words, making URLs easier to share and remember.

---

## 🚀 Features

- 🔗 Create short URLs with custom codes
- 🔍 Retrieve original URLs by short code
- ✏️ Update URL for an existing short code
- ❌ Delete short URLs
- 📜 List all stored URLs
- 👤 User registration and OAuth2-based authorization

> **Note:** All endpoints for URL Shorty features require **Bearer token ( Authorization: Bearer TOKEN_HERE ) headers**. Users must authenticate using bearer token to access any feature.

---

> After logging in, use the token as a `Bearer` token in the `Authorization` header to access the URL Shorty features:
> ```http
> Authorization: Bearer <access_token>
> ```

---

# 📚 API Endpoints

### 🛠 Server & Health Check _(Requires Authorization)_

- `GET /`  
  _Check if the server and database are healthy._



### 🔗 URL Management _(Requires Authorization)_

- `GET /url/list/`  
  _Retrieve a list of all shortened URLs._

- `POST /url/shorten/`  
  _Create a new short URL with a custom short code._  
  **Request Body Example:**
  ```json
  {
    "original_url": "https://example.com",
    "short_code": "mycustomcode"
  }
  ```

- `GET /url/{shortCode}`  
  _Retrieve the original URL for the given `shortCode`._

- `PATCH /url/{shortCode}`  
  _Update the original URL for a given `shortCode`._  
  **Request Body Example:**
  ```json
  {
    "short_code": "mycustomcode",
    "updated_url": "https://new-destination.com"
  }
  ```

- `DELETE /url/{shortCode}`  
  _Delete the shortened URL associated with the given `shortCode`._

---


# 👤 User Management

### 🔹 POST `/usr/register`  
**Description:** Register a new user.  
**Request Body Example:**
```json
{
  "username": "ExampleUser",
  "password": "ExamplePassword"
}
```

---

### 🔹 POST `/usr/login`  
**Description:** Obtain OAuth2 access token and refresh token after login.  
**Form Data Example:**
```json
{
  "username": "ExampleUser",
  "password": "ExamplePassword"
}
```

---

### 🔹 GET `/usr/me`  
**Description:** Get current logged-in user's details from access token.  
**Headers:**
```
Authorization: Bearer <access_token>
```

---

### 🔹 POST `/usr/refresh`  
**Description:** Use a refresh token to obtain a new access token.  
**Request Body Example:**
```json
{
  "refresh_token": "<refresh_token>"
}
```

---

### 🔹 POST `/usr/logout`  
**Description:** Logs out the current user from backend by blacklisting the refresh token.  
**Request Body Example:**
```json
{
  "refresh_token": "<refresh_token>"
}
```

---

### 🔹 DELETE `/usr/delete`  
**Description:** Deletes the user account and related url.  
**Request Body Example:**
```json
{
  "username": "ExampleUser",
  "password": "ExamplePassword"
}
```


---

# 🛠️ Tech Stack

- **FastAPI** – Web framework for building APIs  
- **SQLAlchemy** – ORM for database interactions  
- **SQLite / PostgreSQL** – Database  
- **Pydantic** – Data validation and serialization  
- **Uvicorn** – ASGI server for running FastAPI apps  
- **Passlib** – Password hashing  
- **Python-JOSE** – JWT creation and verification  
- **OAuth2** – Secure authentication and token-based access  


---

