# URL Shorty

About
-----

**URL Shorty** is a RESTful API built with FastAPI that allows users to create and manage shortened URLs. It supports custom short codes using human-friendly words and provides secure user registration and authentication to manage personal links. Designed for speed and simplicity.


**Frontend:** [URLShorty CLI](./frontend_cli)

---

## 🚀 Features

- 🔗 Create short URLs with custom codes
- 🔍 Retrieve original URLs by short code
- ✏️ Update URL for an existing short code
- ❌ Delete short URLs
- 📜 List all stored URLs
- 👤 User registration and OAuth2-based authorization

---

> After logging in, use the token as a `Bearer` token in the `Authorization` header to access the URL Shorty features:
> ```http
> Authorization: Bearer <access_token>
> ```

---

## 📚 API Endpoints


### 👤 User Management

#### 🔹 POST `/usr/register`  
**Description:** Register a new user.  
**Request Body Example:**
```json
{
  "username": "ExampleUser",
  "password": "ExamplePassword"
}
```

---

#### 🔹 POST `/usr/login`  
**Description:** Obtain access token and refresh token after login.  
**Request Body Example:**
```json
{
  "username": "ExampleUser",
  "password": "ExamplePassword"
}
```

---

#### 🔹 GET `/usr/me`  
**Description:** Get current logged-in user's details with access token.  
**Headers:**
```
Authorization: Bearer <access_token>
```

---

#### 🔹 POST `/usr/refresh`  
**Description:** Use a refresh token to obtain a new access token.  
**Request Body Example:**
```json
{
  "refresh_token": "<refresh_token>"
}
```

---

#### 🔹 POST `/usr/logout`  
**Description:** Logs out the current user from backend by blacklisting the refresh token.  
**Request Body Example:**
```json
{
  "refresh_token": "<refresh_token>"
}
```

---

#### 🔹 DELETE `/usr/delete`  
**Description:** Deletes the user account and related url.  
**Request Body Example:**
```json
{
  "username": "ExampleUser",
  "password": "ExamplePassword"
}
```

---

### 🛠 Server & Health Check

#### 🔹 GET `/health/`  
**Description:** Check if the server and database are healthy.

---

### 🔗 URL Management _(Requires Authorization)_

#### 🔹 GET `/url/list/`  
**Description:** Retrieve a list of all shortened URLs.

#### 🔹 POST `/url/shorten/`  
**Description:** Create a new short URL with a custom short code.  
**Request Body Example:**
```json
{
  "original_url": "https://example.com",
  "short_code": "mycustomcode"
}
```

#### 🔹 GET `/url/{shortCode}`  
**Description:** Retrieve the original URL for the given `shortCode`.

#### 🔹 PATCH `/url/`  
**Description:** Update the original URL for a given `shortCode`.  
**Request Body Example:**
```json
{
  "short_code": "mycustomcode",
  "updated_url": "https://new-destination.com"
}
```

#### 🔹 DELETE `/url/`  
**Description:** Delete the shortened URL associated with the given `shortCode`.
**Request Body Example:**
```json
{
  "short_code": "mycustomcode",
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
## 🖥️ Frontend: URLShorty CLI
**Directory:** `/frontend_cli`

You can use the command-line interface (CLI) frontend to interact with the URLShorty API directly from your terminal. This tool supports all core URLShorty features, allowing you to manage your links efficiently without leaving the command line.