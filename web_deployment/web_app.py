#!/usr/bin/env python3
"""
YouTube Downloader - Web Interface
Advanced Features: YouTube, Instagram, Facebook downloader with modern UI
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import os
import sys
import uuid
import threading
import queue
import json
import time

try:
    import yt_dlp as ytdlp
except ImportError:
    print("yt-dlp is required. Install with: pip install yt-dlp")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-' + str(uuid.uuid4()))
CORS(app)

# Store download progress and queues
downloads_progress = {}
download_queues = {}
active_downloads = {}
downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads', 'YouTube Downloader')

# Create downloads folder if not exists
if not os.path.exists(downloads_folder):
    os.makedirs(downloads_folder)


def get_downloads_folder():
    """Get default Downloads folder for Windows"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        downloads = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
        winreg.CloseKey(key)
        if os.path.exists(downloads):
            return os.path.join(downloads, 'YouTube Downloader')
    except:
        pass

    alternatives = [
        os.path.join(os.path.expanduser('~'), 'Downloads', 'YouTube Downloader'),
        os.path.join(os.path.expanduser('~'), 'downloads', 'YouTube Downloader'),
        os.path.join(os.path.expanduser('~'), 'YouTube Downloader')
    ]

    for path in alternatives:
        parent = os.path.dirname(path)
        if os.path.exists(parent):
            if not os.path.exists(path):
                os.makedirs(path)
            return path

    return os.path.join(os.path.expanduser('~'), 'YouTube Downloader')


def progress_hook(download_id):
    """Create progress hook for specific download with SSE support"""
    def hook(d):
        status = d.get('status')
        progress_data = None

        if status == 'downloading':
            speed = d.get('speed')
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes')
            eta = d.get('eta')
            pct = 0

            try:
                if total_bytes and downloaded:
                    pct = (downloaded / total_bytes) * 100
            except:
                pct = 0

            progress_data = {
                'status': 'downloading',
                'progress': round(pct, 2),
                'speed': round(speed / (1024 * 1024), 2) if speed else 0,
                'eta': int(eta) if eta else 0,
                'downloaded': downloaded,
                'total': total_bytes
            }
        elif status == 'finished':
            progress_data = {
                'status': 'finished',
                'progress': 100,
                'message': 'Download completed successfully!'
            }
        elif status == 'error':
            progress_data = {
                'status': 'error',
                'message': 'Error during download'
            }

        if progress_data:
            downloads_progress[download_id] = progress_data
            # Send to SSE queue if exists
            if download_id in download_queues:
                try:
                    download_queues[download_id].put(progress_data)
                except:
                    pass
    return hook


def download_video_async(download_id, url, quality, mode, audio_format, platform, browser=None, video_format='mp4', is_playlist=False):
    """Async download function with playlist support"""
    try:
        folder = get_downloads_folder()

        # Set output template based on platform
        if platform == 'instagram':
            output_template = os.path.join(folder, "Instagram - %(title)s [%(id)s].%(ext)s")
        elif platform == 'facebook':
            output_template = os.path.join(folder, "Facebook - %(title)s [%(id)s].%(ext)s")
        else:
            if is_playlist:
                output_template = os.path.join(folder, "%(playlist)s", "%(playlist_index)s - %(title)s [%(id)s].%(ext)s")
            else:
                output_template = os.path.join(folder, "%(uploader)s - %(title)s [%(id)s].%(ext)s")

        opts = {
            'outtmpl': output_template,
            'noplaylist': not is_playlist,
            'ignoreerrors': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook(download_id)],
            'retries': 3,
            'verbose': False,
            'continuedl': True,
        }

        # Add browser cookies for Instagram/Facebook
        if platform in ['instagram', 'facebook'] and browser:
            opts['cookiesfrombrowser'] = (browser, None, None, None)

        # Format selection
        if mode == 'audio':
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': '192',
            }]
        elif mode == 'video':
            if quality == 'best':
                opts['format'] = f'bestvideo[ext={video_format}]/bestvideo/best'
            elif quality == 'worst':
                opts['format'] = f'worstvideo[ext={video_format}]/worstvideo'
            else:
                opts['format'] = f'bestvideo[height<={quality}][ext={video_format}]/bestvideo[height<={quality}]/bestvideo/best'

            # Add post-processor to convert to desired format if needed
            if video_format and video_format != 'mp4':
                opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': video_format,
                }]
        else:  # both
            if quality == 'best':
                opts['format'] = f'best[ext={video_format}]/bestvideo[ext={video_format}]+bestaudio/bestvideo+bestaudio/best'
            elif quality == 'worst':
                opts['format'] = f'worst[ext={video_format}]/worstvideo+worstaudio/worst'
            else:
                opts['format'] = f'best[height<={quality}][ext={video_format}]/bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'

            # Add post-processor to convert to desired format if needed
            if video_format and video_format != 'mp4':
                opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': video_format,
                }]

        progress_data = {
            'status': 'starting',
            'progress': 0,
            'message': 'Starting download...'
        }
        downloads_progress[download_id] = progress_data
        if download_id in download_queues:
            download_queues[download_id].put(progress_data)

        with ytdlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

        completion_data = {
            'status': 'completed',
            'progress': 100,
            'message': 'Download completed successfully!',
            'folder': folder
        }
        downloads_progress[download_id] = completion_data
        if download_id in download_queues:
            download_queues[download_id].put(completion_data)

    except Exception as e:
        error_data = {
            'status': 'error',
            'progress': 0,
            'message': str(e)
        }
        downloads_progress[download_id] = error_data
        if download_id in download_queues:
            download_queues[download_id].put(error_data)
    finally:
        if download_id in active_downloads:
            del active_downloads[download_id]


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/download', methods=['POST'])
def download():
    """Start download (single, playlist, or batch)"""
    data = request.json
    urls = data.get('urls', [])
    url = data.get('url')
    quality = data.get('quality', 'best')
    mode = data.get('mode', 'both')
    audio_format = data.get('audio_format', 'mp3')
    video_format = data.get('video_format', 'mp4')
    platform = data.get('platform', 'youtube')
    browser = data.get('browser', 'chrome')
    is_playlist = data.get('is_playlist', False)

    # Handle both single URL and batch URLs
    if url and not urls:
        urls = [url]

    if not urls:
        return jsonify({'error': 'URL is required'}), 400

    download_ids = []

    for single_url in urls:
        # Generate unique download ID
        download_id = str(uuid.uuid4())
        download_ids.append(download_id)
        active_downloads[download_id] = {
            'url': single_url,
            'platform': platform,
            'started_at': time.time()
        }

        # Start download in background thread
        thread = threading.Thread(
            target=download_video_async,
            args=(download_id, single_url, quality, mode, audio_format, platform, browser, video_format, is_playlist)
        )
        thread.daemon = True
        thread.start()

    return jsonify({
        'download_ids': download_ids,
        'download_id': download_ids[0] if download_ids else None,  # backward compatibility
        'message': f'Started {len(download_ids)} download(s)'
    })


@app.route('/api/progress/<download_id>')
def get_progress(download_id):
    """Get download progress (polling method - legacy)"""
    progress = downloads_progress.get(download_id, {
        'status': 'unknown',
        'progress': 0,
        'message': 'Download not found'
    })
    return jsonify(progress)


@app.route('/api/progress/stream/<download_id>')
def stream_progress(download_id):
    """Stream download progress via Server-Sent Events (SSE)"""
    def generate():
        # Create queue for this download
        q = queue.Queue()
        download_queues[download_id] = q

        # Send initial status if exists
        if download_id in downloads_progress:
            initial = downloads_progress[download_id]
            yield f"data: {json.dumps(initial)}\n\n"

        try:
            while True:
                # Wait for progress update (timeout after 30 seconds)
                try:
                    progress_data = q.get(timeout=30)
                    yield f"data: {json.dumps(progress_data)}\n\n"

                    # Stop streaming if completed or error
                    if progress_data.get('status') in ['completed', 'error']:
                        break
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield f": heartbeat\n\n"
        finally:
            # Clean up queue
            if download_id in download_queues:
                del download_queues[download_id]

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/info', methods=['POST'])
def get_video_info():
    """Get video/playlist information with thumbnail"""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist'
        }

        with ytdlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Check if it's a playlist
            is_playlist = 'entries' in info

            if is_playlist:
                entries = list(info.get('entries', []))
                playlist_count = len(entries)

                # Get first video for preview
                first_video = entries[0] if entries else {}

                return jsonify({
                    'is_playlist': True,
                    'playlist_title': info.get('title', 'Unknown Playlist'),
                    'playlist_count': playlist_count,
                    'uploader': info.get('uploader', 'Unknown'),
                    'thumbnail': first_video.get('thumbnail', info.get('thumbnail', '')),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
                })
            else:
                # Single video
                return jsonify({
                    'is_playlist': False,
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'views': info.get('view_count', 0),
                    'formats': len(info.get('formats', [])),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else '',
                    'upload_date': info.get('upload_date', ''),
                    'channel': info.get('channel', info.get('uploader', 'Unknown'))
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/queue')
def get_queue():
    """Get current download queue status"""
    queue_status = []
    for download_id, info in active_downloads.items():
        progress = downloads_progress.get(download_id, {})
        queue_status.append({
            'id': download_id,
            'url': info.get('url', ''),
            'platform': info.get('platform', ''),
            'progress': progress.get('progress', 0),
            'status': progress.get('status', 'unknown'),
            'started_at': info.get('started_at', 0)
        })
    return jsonify({'queue': queue_status, 'count': len(queue_status)})


if __name__ == '__main__':
    print("=" * 70)
    print("YouTube Downloader - Web Interface".center(70))
    print("by Mohammed (Star)".center(70))
    print("=" * 70)

    # Get port from environment variable (for deployment) or use 5000
    port = int(os.environ.get('PORT', 5000))

    print(f"\nServer starting on: http://0.0.0.0:{port}")
    print(f"Downloads folder: {get_downloads_folder()}")
    print("\nPress CTRL+C to stop the server\n")
    print("=" * 70)
    print("\n© 2025 Mohammed (Star). All rights reserved.\n")

    # Run with host 0.0.0.0 to accept external connections
    app.run(debug=False, host='0.0.0.0', port=port)


