import argparse
from email import header
import requests
import json
import sys
from dotenv import load_dotenv
import os


# Load .env if it exists
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Create .env file with settings for the app.")
    sys.exit()

BASE_URL = os.getenv("BASE_URL")


def get_access_token():
    # Always read access token from auth.txt
    auth_path = os.path.join(os.path.dirname(__file__), "auth.txt")
    if not os.path.exists(auth_path):
        print("User is not logged in.")
        return None

    access_token = None
    with open(auth_path, "r") as f:
        for line in f:
            if line.startswith("access_token="):
                access_token = line.strip().split("=", 1)[1]
                break

    if not access_token:
        print("User is not logged in.")
        return None
    else:
        return access_token


def get_header(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def beautify(response):
    print(f"\nStatus Code: {response.status_code}")
    try:
        parsed = response.json()
        print(json.dumps(parsed, indent=4))
    except ValueError:
        print("Raw Response:", response.text)


# User-related functions
def register(args):
    auth_path = os.path.join(os.path.dirname(__file__), "auth.txt")
    if os.path.exists(auth_path):
        print("User needs to logout to register a new account.")
        return
    else:
        payload = {"username": args.username, "password": args.password}
        res = requests.post(f"{BASE_URL}/usr/register", json=payload)
        if res.status_code == 200:
            print(f"{res.json()['username']} registered successfully")
        else:
            print(res.json()["detail"])


def login(args):
    auth_path = os.path.join(os.path.dirname(__file__), "auth.txt")
    if os.path.exists(auth_path):
        print("User is already logged in.")
        return

    payload = {"username": args.username, "password": args.password}
    res = requests.post(f"{BASE_URL}/usr/login", json=payload)

    if res.status_code == 200:
        tokens = res.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")

        if access_token and refresh_token:
            auth_path = os.path.join(os.path.dirname(__file__), "auth.txt")
            with open(auth_path, "w") as f:
                f.write(f"access_token={access_token}\n")
                f.write(f"refresh_token={refresh_token}\n")
            print("User logged in successfully.")
        else:
            print("Tokens not found in response.")
    else:
        print("Login failed.")


def refresh():
    # Read refresh_token from auth.txt
    auth_path = os.path.join(os.path.dirname(__file__), "auth.txt")
    if not os.path.exists(auth_path):
        print("User is not logged in.")
        return

    refresh_token = None
    with open(auth_path, "r") as f:
        for line in f:
            if line.startswith("refresh_token="):
                refresh_token = line.strip().split("=", 1)[1]
                break

    if not refresh_token:
        print("User is not logged in.")
        return

    payload = {"refresh_token": refresh_token}
    res = requests.post(f"{BASE_URL}/usr/refresh", json=payload)

    # If refresh is successful, update access_token in auth.txt
    if res.status_code == 200:
        new_access_token = res.json().get("access_token")
        if new_access_token:
            # Read existing lines and replace access_token line
            with open(auth_path, "r") as f:
                lines = f.readlines()

            with open(auth_path, "w") as f:
                for line in lines:
                    if line.startswith("access_token="):
                        f.write(f"access_token={new_access_token}\n")
                    else:
                        f.write(line)
            return new_access_token
        else:
            print("New access token not found in response.")
    else:
        print("User is not logged in.")


def get_me(args):

    # Always read access token from auth.txt
    auth_path = os.path.join(os.path.dirname(__file__), "auth.txt")
    if not os.path.exists(auth_path):
        print("User is not logged in.")
        return

    access_token = None
    with open(auth_path, "r") as f:
        for line in f:
            if line.startswith("access_token="):
                access_token = line.strip().split("=", 1)[1]
                break

    if not access_token:
        print("User is not logged in.")
        return

    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(f"{BASE_URL}/usr/me", headers=headers)

    if "detail" in res.json():
        if res.json()["detail"] == "Invalid token":
            access_token = refresh()
            headers = {"Authorization": f"Bearer {access_token}"}
            res = requests.get(f"{BASE_URL}/usr/me", headers=headers)

    print(f"{res.json()['username']} is currently logged in.")


def logout(args):
    # Read refresh_token from auth.txt
    auth_path = os.path.join(os.path.dirname(__file__), "auth.txt")
    if not os.path.exists(auth_path):
        print("User is not logged in.")
        return

    refresh_token = None
    with open(auth_path, "r") as f:
        for line in f:
            if line.startswith("refresh_token="):
                refresh_token = line.strip().split("=", 1)[1]
                break

    if not refresh_token:
        print("User is not logged in.")
        return

    payload = {"refresh_token": refresh_token}
    res = requests.post(f"{BASE_URL}/usr/logout", json=payload)

    # If logout successful, delete auth.txt
    if res.status_code == 200:
        try:
            os.remove(auth_path)
            print("Logged out successfully.")
        except Exception as e:
            print(f"Failed to log out from client side. {e}")
    else:
        print("Logout failed.")


def delete_account(args):

    payload = {"username": args.username, "password": args.password}
    res = requests.delete(f"{BASE_URL}/usr/delete", json=payload)

    # If account deletion is successful, delete auth.txt
    if res.status_code == 200:
        auth_path = os.path.join(os.path.dirname(__file__), "auth.txt")
        if os.path.exists(auth_path):
            os.remove(auth_path)
        print("Account deleted.")
    else:
        print(res.json()["detail"])


# URL-related functions


def check_health(args):

    access_token = get_access_token()
    if not access_token:
        return

    header = get_header(access_token)
    res = requests.get(f"{BASE_URL}/", headers=header)

    if res.status_code == 401:
        if "detail" in res.json() and res.json()["detail"] == "Invalid token":
            new_access_token = refresh()
            new_header = get_header(new_access_token)
            res = requests.get(f"{BASE_URL}/", headers=new_header)

    if res.status_code == 200:
        print(f"Hi, {res.json()['user']}. {res.json()['status']}")

    else:
        print(res.json()["detail"])


def list_urls(args):
    access_token = get_access_token()
    if not access_token:
        return

    header = get_header(access_token)
    res = requests.get(f"{BASE_URL}/url/list/", headers=header)

    if res.status_code == 401:
        if "detail" in res.json() and res.json()["detail"] == "Invalid token":
            new_access_token = refresh()
            new_header = get_header(new_access_token)
            res = requests.get(f"{BASE_URL}/url/list/", headers=new_header)

    if res.status_code == 200:
        beautify(res)
    else:
        print(res.json()["detail"])


def create_url(args):
    access_token = get_access_token()
    if not access_token:
        return

    header = get_header(access_token)
    payload = {"original_url": args.original_url, "short_code": args.short_code}
    res = requests.post(
        f"{BASE_URL}/url/shorten/", headers=header, data=json.dumps(payload)
    )

    if res.status_code == 401:
        if "detail" in res.json() and res.json()["detail"] == "Invalid token":
            new_access_token = refresh()
            new_header = get_header(new_access_token)
            res = requests.post(
                f"{BASE_URL}/url/shorten/", headers=new_header, data=json.dumps(payload)
            )

    if res.status_code == 200:
        beautify(res)
    else:
        print(res.json()["detail"])


def retrieve_url(args):
    access_token = get_access_token()
    if not access_token:
        return

    header = get_header(access_token)
    res = requests.get(f"{BASE_URL}/url/{args.short_code}", headers=header)

    if res.status_code == 401:
        if "detail" in res.json() and res.json()["detail"] == "Invalid token":
            new_access_token = refresh()
            new_header = get_header(new_access_token)
            res = requests.get(f"{BASE_URL}/url/{args.short_code}", headers=new_header)

    if res.status_code == 200:
        beautify(res)
    else:
        print(res.json()["detail"])


def update_url(args):
    access_token = get_access_token()
    if not access_token:
        return

    header = get_header(access_token)
    payload = {"updated_url": args.updated_url, "short_code": args.short_code}
    res = requests.patch(f"{BASE_URL}/url/", headers=header, data=json.dumps(payload))

    if res.status_code == 401:
        if "detail" in res.json() and res.json()["detail"] == "Invalid token":
            new_access_token = refresh()
            new_header = get_header(new_access_token)
            res = requests.patch(
                f"{BASE_URL}/url/", headers=new_header, data=json.dumps(payload)
            )

    if res.status_code == 200:
        beautify(res)
    else:
        print(res.json()["detail"])


def delete_url(args):
    access_token = get_access_token()
    if not access_token:
        return

    header = get_header(access_token)
    payload = {"short_code": args.short_code}
    res = requests.delete(f"{BASE_URL}/url/", headers=header, data=json.dumps(payload))

    if res.status_code == 401:
        if "detail" in res.json() and res.json()["detail"] == "Invalid token":
            new_access_token = refresh()
            new_header = get_header(new_access_token)
            res = requests.delete(
                f"{BASE_URL}/url/", headers=new_header, data=json.dumps(payload)
            )

    if res.status_code == 200:
        beautify(res)
    else:
        print(res.json()["detail"])


def main():
    parser = argparse.ArgumentParser(description="User and URL CLI for API")
    subparsers = parser.add_subparsers(dest="command")

    # User commands
    user_parser = subparsers.add_parser("user", help="User related commands")
    user_subparsers = user_parser.add_subparsers(dest="user_command")

    # Register
    parser_register = user_subparsers.add_parser("register")
    parser_register.add_argument("--username", required=True)
    parser_register.add_argument("--password", required=True)
    parser_register.set_defaults(func=register)

    # Login
    parser_login = user_subparsers.add_parser("login")
    parser_login.add_argument("--username", required=True)
    parser_login.add_argument("--password", required=True)
    parser_login.set_defaults(func=login)

    # Get Me
    parser_me = user_subparsers.add_parser("me")
    parser_me.set_defaults(func=get_me)

    # Refresh
    parser_refresh = user_subparsers.add_parser("refresh")
    parser_refresh.add_argument("--refresh_token", required=True)
    parser_refresh.set_defaults(func=refresh)

    # Logout
    parser_logout = user_subparsers.add_parser("logout")
    parser_logout.set_defaults(func=logout)

    # Delete Account
    parser_delete = user_subparsers.add_parser("delete")
    parser_delete.add_argument("--username", required=True)
    parser_delete.add_argument("--password", required=True)
    parser_delete.set_defaults(func=delete_account)

    # URL commands
    url_parser = subparsers.add_parser("url", help="URL related commands")
    url_subparsers = url_parser.add_subparsers(dest="url_command")

    # Health Check
    parser_health = url_subparsers.add_parser("health")
    parser_health.set_defaults(func=check_health)

    # List URLs
    parser_list = url_subparsers.add_parser("list")
    parser_list.set_defaults(func=list_urls)

    # Create URL
    parser_create = url_subparsers.add_parser("create")
    parser_create.add_argument("--original_url", required=True)
    parser_create.add_argument("--short_code", required=True)
    parser_create.set_defaults(func=create_url)

    # Get URL
    parser_get = url_subparsers.add_parser("get")
    parser_get.add_argument("--short_code", required=True)
    parser_get.set_defaults(func=retrieve_url)

    # Update URL
    parser_update = url_subparsers.add_parser("update")
    parser_update.add_argument("--short_code", required=True)
    parser_update.add_argument("--updated_url", required=True)
    parser_update.set_defaults(func=update_url)

    # Delete URL
    parser_delete_url = url_subparsers.add_parser("delete")
    parser_delete_url.add_argument("--short_code", required=True)
    parser_delete_url.set_defaults(func=delete_url)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
