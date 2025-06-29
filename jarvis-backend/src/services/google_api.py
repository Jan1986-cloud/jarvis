"""
Google Workspace API Service Module
Handles all Google API integrations for Jarvis
"""

import json
import base64
import email
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google API Scopes
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

class GoogleAPIService:
    """Service class for Google Workspace API integrations"""
    
    def __init__(self):
        self.credentials = None
        self.services = {}
    
    def set_credentials(self, access_token: str, refresh_token: str, 
                       expires_at: datetime, scopes: List[str]):
        """Set Google OAuth credentials"""
        token_info = {
            'token': access_token,
            'refresh_token': refresh_token,
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'your-client-id',  # TODO: Get from environment
            'client_secret': 'your-client-secret',  # TODO: Get from environment
            'scopes': scopes
        }
        
        self.credentials = Credentials.from_authorized_user_info(token_info)
        
        # Check if token needs refresh
        if self.credentials.expired:
            self.credentials.refresh(Request())
    
    def get_service(self, service_name: str, version: str = 'v1'):
        """Get or create Google API service"""
        service_key = f"{service_name}_{version}"
        
        if service_key not in self.services:
            if not self.credentials:
                raise ValueError("No credentials set")
            
            self.services[service_key] = build(
                service_name, version, credentials=self.credentials
            )
        
        return self.services[service_key]
    
    # Gmail API Methods
    def get_gmail_messages(self, query: str = '', max_results: int = 10) -> List[Dict]:
        """Get Gmail messages"""
        try:
            service = self.get_service('gmail')
            
            # Get message list
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            detailed_messages = []
            
            # Get detailed info for each message
            for msg in messages:
                msg_detail = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Parse message details
                headers = msg_detail['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Get message snippet
                snippet = msg_detail.get('snippet', '')
                
                # Check if unread
                labels = msg_detail.get('labelIds', [])
                unread = 'UNREAD' in labels
                
                detailed_messages.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'snippet': snippet,
                    'date': date,
                    'unread': unread,
                    'labels': labels
                })
            
            return detailed_messages
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def send_gmail_message(self, to: str, subject: str, body: str, 
                          html_body: str = None) -> Dict:
        """Send Gmail message"""
        try:
            service = self.get_service('gmail')
            
            # Create message
            message = email.mime.multipart.MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            # Add text body
            text_part = email.mime.text.MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = email.mime.text.MIMEText(html_body, 'html')
                message.attach(html_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            # Send message
            send_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'id': send_message['id'],
                'thread_id': send_message['threadId'],
                'status': 'sent'
            }
            
        except HttpError as error:
            raise Exception(f"Gmail send error: {error}")
    
    # Google Drive API Methods
    def get_drive_files(self, query: str = '', max_results: int = 10) -> List[Dict]:
        """Get Google Drive files"""
        try:
            service = self.get_service('drive', 'v3')
            
            # Build query
            search_query = query if query else "trashed=false"
            
            # Get files
            results = service.files().list(
                q=search_query,
                pageSize=max_results,
                fields="files(id,name,mimeType,modifiedTime,size,webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            formatted_files = []
            for file in files:
                # Determine file type
                mime_type = file.get('mimeType', '')
                if 'document' in mime_type:
                    file_type = 'document'
                elif 'spreadsheet' in mime_type:
                    file_type = 'spreadsheet'
                elif 'presentation' in mime_type:
                    file_type = 'presentation'
                elif 'folder' in mime_type:
                    file_type = 'folder'
                else:
                    file_type = 'file'
                
                formatted_files.append({
                    'id': file['id'],
                    'name': file['name'],
                    'type': file_type,
                    'mime_type': mime_type,
                    'modified': file.get('modifiedTime', ''),
                    'size': file.get('size', '0'),
                    'link': file.get('webViewLink', '')
                })
            
            return formatted_files
            
        except HttpError as error:
            raise Exception(f"Drive API error: {error}")
    
    def create_drive_file(self, name: str, file_type: str = 'document', 
                         content: str = '') -> Dict:
        """Create new Google Drive file"""
        try:
            service = self.get_service('drive', 'v3')
            
            # Define MIME types
            mime_types = {
                'document': 'application/vnd.google-apps.document',
                'spreadsheet': 'application/vnd.google-apps.spreadsheet',
                'presentation': 'application/vnd.google-apps.presentation',
                'folder': 'application/vnd.google-apps.folder'
            }
            
            mime_type = mime_types.get(file_type, mime_types['document'])
            
            # Create file metadata
            file_metadata = {
                'name': name,
                'mimeType': mime_type
            }
            
            # Create file
            file = service.files().create(
                body=file_metadata,
                fields='id,name,mimeType,createdTime,webViewLink'
            ).execute()
            
            return {
                'id': file['id'],
                'name': file['name'],
                'type': file_type,
                'mime_type': file['mimeType'],
                'created': file.get('createdTime', ''),
                'link': file.get('webViewLink', '')
            }
            
        except HttpError as error:
            raise Exception(f"Drive create error: {error}")
    
    # Google Calendar API Methods
    def get_calendar_events(self, max_results: int = 10, 
                           time_min: datetime = None) -> List[Dict]:
        """Get Google Calendar events"""
        try:
            service = self.get_service('calendar', 'v3')
            
            # Set time range
            if not time_min:
                time_min = datetime.utcnow()
            
            time_min_str = time_min.isoformat() + 'Z'
            
            # Get events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min_str,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'attendees': event.get('attendees', []),
                    'link': event.get('htmlLink', '')
                })
            
            return formatted_events
            
        except HttpError as error:
            raise Exception(f"Calendar API error: {error}")
    
    def create_calendar_event(self, title: str, start_time: str, end_time: str,
                             description: str = '', location: str = '',
                             attendees: List[str] = None) -> Dict:
        """Create Google Calendar event"""
        try:
            service = self.get_service('calendar', 'v3')
            
            # Create event
            event = {
                'summary': title,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC'
                }
            }
            
            # Add attendees if provided
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Create event
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                'id': created_event['id'],
                'title': created_event.get('summary', ''),
                'start': created_event['start'].get('dateTime', ''),
                'end': created_event['end'].get('dateTime', ''),
                'location': created_event.get('location', ''),
                'link': created_event.get('htmlLink', ''),
                'status': created_event.get('status', '')
            }
            
        except HttpError as error:
            raise Exception(f"Calendar create error: {error}")

# Global service instance
google_service = GoogleAPIService()

