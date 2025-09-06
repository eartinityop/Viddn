#!/usr/bin/env python3
"""
YouTube Upload Script using Service Account
"""

import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video(credentials_file, video_file, title, description, privacy_status="private", category_id="22", tags=None):
    """Upload video to YouTube using service account credentials"""
    
    # Authenticate with service account
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=['https://www.googleapis.com/auth/youtube.upload']
    )
    
    # Build YouTube service
    youtube = build('youtube', 'v3', credentials=credentials)
    
    # Setup video metadata
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or ['processed', 'automated'],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Create media file upload object
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    
    # Execute upload request
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    
    print(f"Video uploaded successfully! Video ID: {response['id']}")
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload video to YouTube')
    parser.add_argument('--credentials', required=True, help='Service account JSON file')
    parser.add_argument('--file', required=True, help='Video file to upload')
    parser.add_argument('--title', required=True, help='Video title')
    parser.add_argument('--description', required=True, help='Video description')
    parser.add_argument('--privacy', default='private', help='Privacy status (public, private, unlisted)')
    parser.add_argument('--category', default='22', help='YouTube category ID')
    parser.add_argument('--tags', nargs='+', help='Video tags')
    
    args = parser.parse_args()
    
    upload_video(
        args.credentials,
        args.file,
        args.title,
        args.description,
        args.privacy,
        args.category,
        args.tags
    )
