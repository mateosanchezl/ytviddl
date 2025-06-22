from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import threading
import queue
import subprocess
import signal
import psutil
import uuid
from main import sanitize_filename
from pytubefix import YouTube
from pytubefix.cli import on_progress

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global storage for download status and processes
download_status = {}
download_processes = {}
download_threads = {}

class CancellableDownload:
    def __init__(self, download_id, url, output_path):
        self.download_id = download_id
        self.url = url
        self.output_path = output_path
        self.cancelled = False
        self.current_process = None
        
    def cancel(self):
        """Cancel the download"""
        self.cancelled = True
        if self.current_process:
            try:
                # Kill the ffmpeg process if it's running
                parent = psutil.Process(self.current_process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Update status
        download_status[self.download_id] = {
            'status': 'error',
            'progress': 0,
            'message': 'cancelled'
        }
    
    def download_and_merge(self):
        """Modified version of your download_and_merge function with cancellation support"""
        try:
            if self.cancelled:
                return
                
            print(f"Processing URL: {self.url}")
            yt = YouTube(self.url, on_progress_callback=on_progress)

            # Update status
            download_status[self.download_id] = {
                'status': 'downloading',
                'progress': 10,
                'message': 'getting video info...'
            }

            if self.cancelled:
                return

            # Get video title and create safe filename
            video_title = sanitize_filename(yt.title)
            final_filename = os.path.join(self.output_path, f"{video_title}.mp4")
            
            # Temporary filenames with unique IDs to prevent conflicts
            video_temp_file = os.path.join(self.output_path, f"video_temp_{self.download_id}.mp4")
            audio_temp_file = os.path.join(self.output_path, f"audio_temp_{self.download_id}.mp4")

            # Get the best streams
            video_stream = yt.streams.filter(
                adaptive=True, file_extension='mp4', only_video=True
            ).order_by('resolution').desc().first()
            
            audio_stream = yt.streams.filter(
                adaptive=True, file_extension='mp4', only_audio=True
            ).order_by('abr').desc().first()

            if not video_stream or not audio_stream:
                download_status[self.download_id] = {
                    'status': 'error',
                    'progress': 0,
                    'message': 'no suitable streams found'
                }
                return

            if self.cancelled:
                return

            # Download video
            download_status[self.download_id] = {
                'status': 'downloading',
                'progress': 30,
                'message': 'downloading video...'
            }
            
            video_stream.download(output_path=self.output_path, filename=f"video_temp_{self.download_id}.mp4")

            if self.cancelled:
                self.cleanup_temp_files(video_temp_file, audio_temp_file)
                return

            # Download audio
            download_status[self.download_id] = {
                'status': 'downloading',
                'progress': 60,
                'message': 'downloading audio...'
            }
            
            audio_stream.download(output_path=self.output_path, filename=f"audio_temp_{self.download_id}.mp4")

            if self.cancelled:
                self.cleanup_temp_files(video_temp_file, audio_temp_file)
                return

            # Merge using FFmpeg
            download_status[self.download_id] = {
                'status': 'downloading',
                'progress': 85,
                'message': 'merging video and audio...'
            }
            
            command = [
                'ffmpeg',
                '-i', video_temp_file,
                '-i', audio_temp_file,
                '-c:v', 'copy',
                '-c:a', 'copy',
                final_filename,
                '-y'  # Overwrite output file if it exists
            ]
            
            # Start ffmpeg process
            self.current_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for completion or cancellation
            stdout, stderr = self.current_process.communicate()
            
            if self.cancelled:
                self.cleanup_temp_files(video_temp_file, audio_temp_file)
                # Also remove partial final file
                if os.path.exists(final_filename):
                    os.remove(final_filename)
                return
            
            if self.current_process.returncode != 0:
                download_status[self.download_id] = {
                    'status': 'error',
                    'progress': 0,
                    'message': f'ffmpeg error: {stderr[:100]}...'
                }
                return

            # Success
            download_status[self.download_id] = {
                'status': 'completed',
                'progress': 100,
                'message': 'download completed!'
            }

            print(f"Successfully created: '{final_filename}'")

        except Exception as e:
            if not self.cancelled:
                download_status[self.download_id] = {
                    'status': 'error',
                    'progress': 0,
                    'message': f'error: {str(e)[:50]}...'
                }
            print(f"An error occurred while processing {self.url}: {e}")

        finally:
            # Clean up temporary files
            self.cleanup_temp_files(video_temp_file, audio_temp_file)
            
            # Clean up references
            if self.download_id in download_processes:
                del download_processes[self.download_id]
            if self.download_id in download_threads:
                del download_threads[self.download_id]
    
    def cleanup_temp_files(self, video_temp_file, audio_temp_file):
        """Clean up temporary files"""
        for temp_file in [video_temp_file, audio_temp_file]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass


@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    output_path = data.get('output_path', './vids')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Generate a unique ID for this download
    download_id = str(uuid.uuid4())

    # Create cancellable download instance
    cancellable_download = CancellableDownload(download_id, url, output_path)
    download_processes[download_id] = cancellable_download

    # Start download in background thread
    def download_worker():
        cancellable_download.download_and_merge()

    thread = threading.Thread(target=download_worker)
    thread.daemon = True
    thread.start()
    
    download_threads[download_id] = thread

    return jsonify({
        'download_id': download_id,
        'message': 'Download started'
    })


@app.route('/api/cancel/<download_id>', methods=['POST'])
def cancel_download(download_id):
    try:
        if download_id in download_processes:
            cancellable_download = download_processes[download_id]
            cancellable_download.cancel()
            return jsonify({'message': 'Download cancelled'})
        else:
            return jsonify({'error': 'Download not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<download_id>', methods=['GET'])
def get_download_status(download_id):
    status = download_status.get(download_id, {
        'status': 'not_found',
        'progress': 0,
        'message': 'Download not found'
    })
    return jsonify(status)


@app.route('/api/videos', methods=['GET'])
def list_videos():
    output_path = request.args.get('path', './vids')
    if not os.path.exists(output_path):
        return jsonify([])

    videos = []
    for filename in os.listdir(output_path):
        if filename.endswith('.mp4') and not filename.startswith('video_temp_') and not filename.startswith('audio_temp_'):
            file_path = os.path.join(output_path, filename)
            file_size = os.path.getsize(file_path)
            videos.append({
                'filename': filename,
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2)
            })

    return jsonify(videos)


if __name__ == '__main__':
    app.run(debug=True, port=5000)