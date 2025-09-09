#!/usr/bin/env python3
"""
YouTube Upload Script
"""

import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests
import json

def upload_video(access_token, video_file, title, description, privacy_status="private", category_id="22"):
    """Upload video to YouTube using access token"""
    
    try:
        # Build YouTube service
        youtube = build('youtube', 'v3', developerKey='dummy')
        
        # Setup video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['processed', 'automated'],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media file upload object
        media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
        
        # Create authorized request function
        def authorized_request(http, *args, **kwargs):
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {access_token}'
            kwargs['headers'] = headers
            return http.request(*args, **kwargs)
        
        youtube._http.request = authorized_request
        
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
        
        print(f"✅ Successfully uploaded: {title}")
        print(f"Video ID: {response['id']}")
        return response
        
    except Exception as e:
        print(f"❌ Error uploading video: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload video to YouTube')
    parser.add_argument('--access_token', required=True, help='OAuth 2.0 access token')
    parser.add_argument('--file', required=True, help='Video file to upload')
    parser.add_argument('--title', required=True, help='Video title')
    parser.add_argument('--description', required=True, help='Video description')
    parser.add_argument('--privacy', default='private', help='Privacy status')
    
    args = parser.parse_args()
    
    upload_video(
        args.access_token,
        args.file,
        args.title,
        args.description,
        args.privacy
    )
