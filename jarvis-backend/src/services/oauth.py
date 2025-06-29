"""
Google OAuth Setup Helper
Handles Google OAuth2 authentication flow
"""

import os
import json
import secrets
from typing import Dict, Optional, Tuple
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Google OAuth Configuration
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/contacts'
]

# Default client configuration (for demo purposes)
DEFAULT_CLIENT_CONFIG = {
    "web": {
        "client_id": "demo-client-id.apps.googleusercontent.com",
        "project_id": "jarvis-demo-project",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "demo-client-secret",
        "redirect_uris": ["http://localhost:5000/api/auth/callback"]
    }
}

class GoogleOAuthHelper:
    """Helper class for Google OAuth operations"""
    
    def __init__(self, client_config: Dict = None):
        """Initialize OAuth helper with client configuration"""
        self.client_config = client_config or DEFAULT_CLIENT_CONFIG
        self.redirect_uri = "http://localhost:5000/api/auth/callback"
    
    def create_flow(self) -> Flow:
        """Create OAuth flow object"""
        flow = Flow.from_client_config(
            self.client_config,
            scopes=SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        return flow
    
    def get_authorization_url(self) -> Tuple[str, str]:
        """Get authorization URL and state for OAuth flow"""
        flow = self.create_flow()
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state
        )
        
        return authorization_url, state
    
    def exchange_code_for_tokens(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for tokens"""
        try:
            flow = self.create_flow()
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            return {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'expires_in': 3600,  # Default 1 hour
                'scope': ' '.join(SCOPES),
                'token_type': 'Bearer'
            }
        except Exception as e:
            print(f"Error exchanging code for tokens: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token using refresh token"""
        try:
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri=self.client_config['web']['token_uri'],
                client_id=self.client_config['web']['client_id'],
                client_secret=self.client_config['web']['client_secret']
            )
            
            credentials.refresh(Request())
            
            return {
                'access_token': credentials.token,
                'expires_in': 3600,
                'token_type': 'Bearer'
            }
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None

# Global OAuth helper instance
oauth_helper = GoogleOAuthHelper()

def get_google_oauth_url() -> Tuple[str, str]:
    """Get Google OAuth authorization URL and state"""
    return oauth_helper.get_authorization_url()

def exchange_code_for_tokens(code: str) -> Optional[Dict]:
    """Exchange authorization code for tokens"""
    return oauth_helper.exchange_code_for_tokens(code)

def refresh_google_token(refresh_token: str) -> Optional[Dict]:
    """Refresh Google access token"""
    return oauth_helper.refresh_access_token(refresh_token)

def setup_oauth_credentials():
    """Setup OAuth credentials file for development"""
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'google_credentials.json')
    
    # Create config directory if it doesn't exist
    os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
    
    if not os.path.exists(credentials_path):
        with open(credentials_path, 'w') as f:
            json.dump(DEFAULT_CLIENT_CONFIG, f, indent=2)
        
        print(f"Created sample OAuth credentials file at: {credentials_path}")
        print("Please replace with your actual Google OAuth credentials for production use.")
        print("\nTo get real credentials:")
        print("1. Go to https://console.developers.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Workspace APIs")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download and replace the credentials file")
    
    return credentials_path

# Initialize OAuth setup
if __name__ == "__main__":
    setup_oauth_credentials()
    print("OAuth helper initialized successfully!")
    
    # Test OAuth URL generation
    try:
        auth_url, state = get_google_oauth_url()
        print(f"Test OAuth URL: {auth_url[:100]}...")
        print(f"State: {state}")
    except Exception as e:
        print(f"Error testing OAuth: {e}")

# Export functions
__all__ = [
    'GoogleOAuthHelper',
    'oauth_helper',
    'get_google_oauth_url',
    'exchange_code_for_tokens',
    'refresh_google_token',
    'setup_oauth_credentials',
    'SCOPES'
]

