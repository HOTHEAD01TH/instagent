import os
import random
from instagrapi import Client
import schedule
import time
from dotenv import load_dotenv
import ffmpeg
import numpy as np
from PIL import Image
import io
import pickle
import gc

load_dotenv()

# Path to reels folder
REELS_FOLDER = "reels/"

# Instagram credentials from env
USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

def login():
    try:
        cl = Client()
        # Try to load saved session
        if os.path.exists('session.pkl'):
            with open('session.pkl', 'rb') as f:
                session = pickle.load(f)
                cl.set_settings(session)
                cl.login(USERNAME, PASSWORD)
                print("✅ Logged in using cached session!")
        else:
            # First time login
            cl.login(USERNAME, PASSWORD)
            # Save session for future use
            with open('session.pkl', 'wb') as f:
                pickle.dump(cl.get_settings(), f)
            print("✅ Logged in and saved session!")
        return cl
    except Exception as e:
        # If session is invalid, try fresh login
        try:
            if os.path.exists('session.pkl'):
                os.remove('session.pkl')  # Remove invalid session
            cl = Client()
            cl.login(USERNAME, PASSWORD)
            with open('session.pkl', 'wb') as f:
                pickle.dump(cl.get_settings(), f)
            print("✅ Logged in with fresh session!")
            return cl
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return None

def process_video(video_path):
    """Process video to match Instagram requirements (9:16 ratio)"""
    try:
        # Get video info
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        duration = int(float(probe['format']['duration']) * 1000)  # ms
        
        output_path = video_path + "_processed.mp4"
        
        # Force resize to 1080x1920 (Instagram Reels aspect ratio)
        stream = (
            ffmpeg
            .input(video_path)
            .filter('scale', 1080, 1920, force_original_aspect_ratio='decrease')
            .filter('pad', 1080, 1920, '(ow-iw)/2', '(oh-ih)/2')
            .output(
                output_path,
                acodec='aac',
                vcodec='libx264',
                **{
                    'b:v': '4000k',
                    'maxrate': '5000k',
                    'bufsize': '8000k',
                    'preset': 'medium',
                    'profile:v': 'high',
                    'level': '4.2',
                    'pix_fmt': 'yuv420p',
                    'movflags': '+faststart',
                    'c:a': 'aac',
                    'b:a': '128k',
                    'ar': '44100'
                }
            )
        )
        
        # Run the ffmpeg command
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        # Get thumbnail
        thumb_data = get_thumbnail(output_path)
        return output_path, (1080, 1920), duration, thumb_data
            
    except Exception as e:
        print(f"❌ Video processing failed: {e}")
        return None, None, None, None

def get_thumbnail(video_path):
    """Extract thumbnail from video"""
    try:
        out, _ = (
            ffmpeg
            .input(video_path)
            .filter('select', 'eq(n,0)')
            .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
            .run(capture_stdout=True, quiet=True)
        )
        
        img = Image.open(io.BytesIO(out))
        thumb_buffer = io.BytesIO()
        img.save(thumb_buffer, format='JPEG')
        return thumb_buffer.getvalue()
    except Exception as e:
        print(f"❌ Thumbnail extraction failed: {e}")
        return None

def upload_reel():
    if os.listdir(REELS_FOLDER):
        video = random.choice(os.listdir(REELS_FOLDER))
        video_path = os.path.join(REELS_FOLDER, video)
        caption = "🔥 Check this out! #EscapeTheMatrix #TheRealWorld #AndrewTate #TateSpeech #MindsetMatters #SuccessMindset #Motivation #SelfImprovement #WealthBuilding #AlphaMindset #UnfilteredTruth #PersonalDevelopment #BreakTheNorm #RiseAbove #HustleHard #LiveLifeOnYourTerms #ChallengeYourself #FearlessLiving #EmpowerYourself #WinningMindset"

        try:
            # Upload the video
            cl.clip_upload(
                video_path,
                caption=caption
            )
            print(f"✅ Uploaded: {video}")
            
            # Wait for file handles to be released
            time.sleep(15)  # Increased wait time
            
            # Force Python garbage collection
            gc.collect()
            
            try:
                # Delete video file
                if os.path.exists(video_path):
                    os.chmod(video_path, 0o777)  # Give full permissions
                    os.remove(video_path)
                    print(f"✅ Deleted video: {video}")
                
                # Delete thumbnail
                thumb_path = video_path + ".jpg"
                if os.path.exists(thumb_path):
                    os.chmod(thumb_path, 0o777)  # Give full permissions
                    os.remove(thumb_path)
                    print(f"✅ Deleted thumbnail: {video}.jpg")
            except Exception as e:
                print(f"⚠️ Could not delete {video}: {e}")
                
        except Exception as e:
            print(f"❌ Failed to upload {video}: {e}")
    else:
        print("📂 No more reels to upload!")

# Schedule daily uploads
schedule.every().day.at("13:00").do(upload_reel)
schedule.every().day.at("15:00").do(upload_reel)
schedule.every().day.at("18:00").do(upload_reel)
schedule.every().day.at("21:00").do(upload_reel)

# Start the bot
cl = login()
if cl:
    print("🚀 Automation started...")
    upload_reel()  # Post a random reel immediately
    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    print("⚠️ Exiting due to login failure.")
