# URLShorty CLI

A command-line interface (CLI) frontend for interacting with the URLShorty API. This tool allows users to register, log in, manage their user accounts, and create/manage shortened URLs.

### ⚠️ Note

> Users must log in to use all features.

---

## 📦 User Commands

### 🔐 Register a New User
```bash
python urlshorty_cli.py user register --username <username> --password <password>
```

### 🔑 Login and Obtain Access Token
```bash
python urlshorty_cli.py user login --username <username> --password <password>
```

### 👤 Get Logged-in User Details
```bash
python urlshorty_cli.py user me
```

### 🚪 Logout
```bash
python urlshorty_cli.py user logout
```

### 🗑️ Delete User Account
```bash
python urlshorty_cli.py user delete --username <username> --password <password>
```

---

## 🌐 URL Commands

### ❤️ Check API Health
```bash
python urlshorty_cli.py url health
```

### 📄 List All Shortened URLs
```bash
python urlshorty_cli.py url list
```

### ✨ Create a Shortened URL
```bash
python urlshorty_cli.py url create --original_url <original_url> --short_code <short_code>
```

### 🔎 Retrieve Original URL
```bash
python urlshorty_cli.py url get --short_code <short_code>
```

### ♻️ Update a Shortened URL
```bash
python urlshorty_cli.py url update --short_code <short_code> --updated_url <updated_url>
```

### 🧹 Delete a Shortened URL
```bash
python urlshorty_cli.py url delete --short_code <short_code>
```

---

## 🧪 Requirements

- Python 3.7+
- `requests` and `python-dotenv` Python packages
- Access to the URLShorty API
- CLI authentication token after login

---

## 💡 About

This CLI tool is a lightweight frontend for the URLShorty API, allowing users to manage URLs and user sessions directly from the terminal using simple commands.
