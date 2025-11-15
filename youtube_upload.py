#!/usr/bin/env python3
"""
Updated YouTube Upload Script with better error handling
"""

import argparse
import os
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import google.auth.exceptions

def upload_video(access_token, video_file, title, description, privacy_status="private", category_id="22"):
    """Upload video to YouTube using access token"""
    
    try:
        print(f"Starting upload: {title}")
        print(f"Video file: {video_file} (Size: {os.path.getsize(video_file)} bytes)")
        
        # Create credentials object from access token
        credentials = Credentials(token=access_token)
        
        # Build YouTube service
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # Verify the token is valid
        try:
            channels_response = youtube.channels().list(
                part="snippet",
                mine=True
            ).execute()
            print("✅ Token validation successful")
        except Exception as e:
            print(f"❌ Token validation failed: {str(e)}")
            return None
        
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
        
        print("Uploading video...")
        
        # Create media file upload object
        media = MediaFileUpload(
            video_file, 
            chunksize=1024*1024,  # 1MB chunks
            resumable=True,
            mimetype='video/mp4'
        )
        
        # Execute upload request
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        retry_count = 0
        max_retries = 3
        
        while response is None and retry_count < max_retries:
            try:
                status, response = request.next_chunk()
                if status:
                    print(f"Upload progress: {int(status.progress() * 100)}%")
            except google.auth.exceptions.RefreshError as e:
                print(f"❌ Authentication error: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying... ({retry_count}/{max_retries})")
                    time.sleep(5)
                else:
                    raise
            except Exception as e:
                print(f"❌ Upload error: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying... ({retry_count}/{max_retries})")
                    time.sleep(5)
                else:
                    raise
        
        if response is not None:
            print(f"✅ Successfully uploaded: {title}")
            print(f"Video ID: {response['id']}")
            return response
        else:
            print("❌ Upload failed after all retries")
            return None
        
    except Exception as e:
        print(f"❌ Error uploading video: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload video to YouTube')
    parser.add_argument('--access_token', required=True, help='OAuth 2.0 access token')
    parser.add_argument('--file', required=True, help='Video file to upload')
    parser.add_argument('--title', required=True, help='Video title')
    parser.add_argument('--description', required=True, help='Video description')
    parser.add_argument('--privacy', default='private', help='Privacy status')
    
    args = parser.parse_args()
    
    # Verify file exists
    if not os.path.exists(args.file):
        print(f"❌ Error: File {args.file} does not exist")
        exit(1)
    
    result = upload_video(
        args.access_token,
        args.file,
        args.title,
        args.description,
        args.privacy
    )
    
    if result is None:
        exit(1)
