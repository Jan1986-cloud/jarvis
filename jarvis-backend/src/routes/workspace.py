from flask import Blueprint, jsonify, request
from src.models.user import User, GoogleToken, db
from src.services.google_api import google_service
from datetime import datetime
import json

workspace_bp = Blueprint('workspace', __name__)

def get_user_and_setup_google_service(user_id):
    """Helper function to get user and setup Google API service"""
    user = User.query.get_or_404(user_id)
    token = GoogleToken.query.filter_by(user_id=user_id).first()
    
    if not token or token.is_expired():
        return user, None, {'error': 'Google token expired or missing'}, 401
    
    # Setup Google API service with user credentials
    try:
        scopes = json.loads(token.scopes) if token.scopes else []
        google_service.set_credentials(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            expires_at=token.expires_at,
            scopes=scopes
        )
        return user, token, None, None
    except Exception as e:
        return user, token, {'error': f'Failed to setup Google API: {str(e)}'}, 500

# Gmail API Routes
@workspace_bp.route('/gmail/messages', methods=['GET'])
def get_gmail_messages():
    """Get Gmail messages"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user, token, error, status = get_user_and_setup_google_service(user_id)
    if error:
        return jsonify(error), status
    
    # Check credits
    if not user.use_credits(2):  # 2 credits for Gmail API call
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        # Get query parameters
        query = request.args.get('q', '')
        max_results = min(int(request.args.get('max_results', 10)), 50)
        
        # Get messages from Gmail API
        messages = google_service.get_gmail_messages(query=query, max_results=max_results)
        
        db.session.commit()  # Save credit usage
        
        return jsonify({
            'messages': messages,
            'query': query,
            'count': len(messages),
            'credits_used': 2,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credit usage on error
        user.add_credits(2)
        db.session.commit()
        return jsonify({'error': f'Gmail API error: {str(e)}'}), 500

@workspace_bp.route('/gmail/send', methods=['POST'])
def send_gmail():
    """Send Gmail message"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user, token, error, status = get_user_and_setup_google_service(user_id)
    if error:
        return jsonify(error), status
    
    data = request.json
    to_email = data.get('to')
    subject = data.get('subject')
    body = data.get('body')
    html_body = data.get('html_body')
    
    if not all([to_email, subject, body]):
        return jsonify({'error': 'Missing required fields: to, subject, body'}), 400
    
    # Check credits
    if not user.use_credits(3):  # 3 credits for sending email
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        # Send email via Gmail API
        result = google_service.send_gmail_message(
            to=to_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        db.session.commit()  # Save credit usage
        
        return jsonify({
            'message': 'Email sent successfully',
            'result': result,
            'to': to_email,
            'subject': subject,
            'credits_used': 3,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credit usage on error
        user.add_credits(3)
        db.session.commit()
        return jsonify({'error': f'Gmail send error: {str(e)}'}), 500

# Google Drive API Routes
@workspace_bp.route('/drive/files', methods=['GET'])
def get_drive_files():
    """Search Google Drive files"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user, token, error, status = get_user_and_setup_google_service(user_id)
    if error:
        return jsonify(error), status
    
    # Check credits
    if not user.use_credits(2):  # 2 credits for Drive API call
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        # Get query parameters
        query = request.args.get('q', '')
        max_results = min(int(request.args.get('max_results', 10)), 50)
        
        # Get files from Drive API
        files = google_service.get_drive_files(query=query, max_results=max_results)
        
        db.session.commit()  # Save credit usage
        
        return jsonify({
            'files': files,
            'query': query,
            'count': len(files),
            'credits_used': 2,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credit usage on error
        user.add_credits(2)
        db.session.commit()
        return jsonify({'error': f'Drive API error: {str(e)}'}), 500

@workspace_bp.route('/drive/files', methods=['POST'])
def create_drive_file():
    """Create new Google Drive file"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user, token, error, status = get_user_and_setup_google_service(user_id)
    if error:
        return jsonify(error), status
    
    data = request.json
    name = data.get('name')
    file_type = data.get('type', 'document')  # document, spreadsheet, presentation
    content = data.get('content', '')
    
    if not name:
        return jsonify({'error': 'File name required'}), 400
    
    # Check credits
    if not user.use_credits(5):  # 5 credits for creating file
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        # Create file via Drive API
        result = google_service.create_drive_file(
            name=name,
            file_type=file_type,
            content=content
        )
        
        db.session.commit()  # Save credit usage
        
        return jsonify({
            'message': 'File created successfully',
            'file': result,
            'credits_used': 5,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credit usage on error
        user.add_credits(5)
        db.session.commit()
        return jsonify({'error': f'Drive create error: {str(e)}'}), 500

# Google Calendar API Routes
@workspace_bp.route('/calendar/events', methods=['GET'])
def get_calendar_events():
    """Get Google Calendar events"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user, token, error, status = get_user_and_setup_google_service(user_id)
    if error:
        return jsonify(error), status
    
    # Check credits
    if not user.use_credits(2):  # 2 credits for Calendar API call
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        # Get query parameters
        max_results = min(int(request.args.get('max_results', 10)), 50)
        time_min = request.args.get('time_min')
        
        # Parse time_min if provided
        time_min_dt = None
        if time_min:
            try:
                time_min_dt = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid time_min format. Use ISO format.'}), 400
        
        # Get events from Calendar API
        events = google_service.get_calendar_events(
            max_results=max_results,
            time_min=time_min_dt
        )
        
        db.session.commit()  # Save credit usage
        
        return jsonify({
            'events': events,
            'count': len(events),
            'credits_used': 2,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credit usage on error
        user.add_credits(2)
        db.session.commit()
        return jsonify({'error': f'Calendar API error: {str(e)}'}), 500

@workspace_bp.route('/calendar/events', methods=['POST'])
def create_calendar_event():
    """Create Google Calendar event"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user, token, error, status = get_user_and_setup_google_service(user_id)
    if error:
        return jsonify(error), status
    
    data = request.json
    title = data.get('title')
    start_time = data.get('start')
    end_time = data.get('end')
    description = data.get('description', '')
    location = data.get('location', '')
    attendees = data.get('attendees', [])
    
    if not all([title, start_time, end_time]):
        return jsonify({'error': 'Missing required fields: title, start, end'}), 400
    
    # Check credits
    if not user.use_credits(3):  # 3 credits for creating event
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        # Create event via Calendar API
        result = google_service.create_calendar_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            attendees=attendees
        )
        
        db.session.commit()  # Save credit usage
        
        return jsonify({
            'message': 'Event created successfully',
            'event': result,
            'credits_used': 3,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credit usage on error
        user.add_credits(3)
        db.session.commit()
        return jsonify({'error': f'Calendar create error: {str(e)}'}), 500

# Workspace Summary Route
@workspace_bp.route('/workspace/summary', methods=['GET'])
def get_workspace_summary():
    """Get summary of workspace activity"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user, token, error, status = get_user_and_setup_google_service(user_id)
    if error:
        return jsonify(error), status
    
    # Check credits
    if not user.use_credits(5):  # 5 credits for comprehensive summary
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        summary = {}
        
        # Get recent emails (last 5)
        try:
            recent_emails = google_service.get_gmail_messages(
                query='is:unread',
                max_results=5
            )
            summary['unread_emails'] = len(recent_emails)
            summary['recent_emails'] = recent_emails[:3]  # Show top 3
        except Exception as e:
            summary['email_error'] = str(e)
        
        # Get upcoming events (next 5)
        try:
            upcoming_events = google_service.get_calendar_events(max_results=5)
            summary['upcoming_events'] = len(upcoming_events)
            summary['next_events'] = upcoming_events[:3]  # Show next 3
        except Exception as e:
            summary['calendar_error'] = str(e)
        
        # Get recent files (last 5)
        try:
            recent_files = google_service.get_drive_files(
                query='',
                max_results=5
            )
            summary['recent_files'] = recent_files[:3]  # Show top 3
        except Exception as e:
            summary['drive_error'] = str(e)
        
        db.session.commit()  # Save credit usage
        
        return jsonify({
            'summary': summary,
            'generated_at': datetime.utcnow().isoformat(),
            'credits_used': 5,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credit usage on error
        user.add_credits(5)
        db.session.commit()
        return jsonify({'error': f'Workspace summary error: {str(e)}'}), 500

