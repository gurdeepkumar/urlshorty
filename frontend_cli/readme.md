# URLShorty CLI

A command-line interface (CLI) frontend for interacting with the URLShorty API. This tool allows users to register, log in, manage their user accounts, and create/manage shortened URLs.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python (version 3.6 or higher recommended)
- pip (Python package installer)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/gurdeepkumar/urlshorty.git
cd urlshorty/frontend_cli
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  
# On Windows use `venv\Scripts\activate`
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create a file with name .env in the same folder(urlshorty/frontend_cli) and add folliwng information:

```bash
BASE_URL = "https://urlshorty.gurdeepkumar.com"
# Update base url if you are running URLShorty on local machine.
```

## 📦 User Commands

##### Make sure you are in urlshorty/frontend_cli folder.

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

##### User must be logged in to use the following features.

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

## 💡 About

This CLI tool is a lightweight frontend for the URLShorty API, allowing users to manage URLs and user sessions directly from the terminal using simple commands.
