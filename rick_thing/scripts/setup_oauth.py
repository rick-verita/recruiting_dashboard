#!/usr/bin/env python3
"""
OAuth2 setup script for Gmail API.

This script helps you generate the refresh token needed to authenticate
with the Gmail API. Run this once to set up your credentials.

Prerequisites:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable the Gmail API
4. Configure OAuth consent screen
5. Create OAuth 2.0 credentials (Desktop app type)
6. Download the credentials and save as 'credentials.json' in this directory

Usage:
    python scripts/setup_oauth.py
"""

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def main():
    """Run the OAuth2 flow and save credentials."""
    print("=" * 60)
    print("Gmail API OAuth2 Setup")
    print("=" * 60)
    print()

    # Check for credentials file
    if not Path(CREDENTIALS_FILE).exists():
        print(f"ERROR: {CREDENTIALS_FILE} not found!")
        print()
        print("Please follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable the Gmail API")
        print("4. Go to 'APIs & Services' > 'Credentials'")
        print("5. Create OAuth 2.0 Client ID (Application type: Desktop app)")
        print("6. Download the JSON and save as 'credentials.json'")
        print()
        return

    creds = None

    # Check for existing token
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth2 flow...")
            print("A browser window will open for you to authorize the application.")
            print()

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print(f"Token saved to {TOKEN_FILE}")

    print()
    print("=" * 60)
    print("SUCCESS! Add these values to your .env file:")
    print("=" * 60)
    print()

    # Load credentials.json to get client_id and client_secret
    with open(CREDENTIALS_FILE) as f:
        creds_data = json.load(f)
        installed = creds_data.get("installed", creds_data.get("web", {}))
        client_id = installed.get("client_id", "")
        client_secret = installed.get("client_secret", "")

    print(f"GMAIL_CLIENT_ID={client_id}")
    print(f"GMAIL_CLIENT_SECRET={client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
