from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import threading
import queue
from main import download_and_merge

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global queue for download status
download_queue = queue.Queue()
download_status = {}

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
    import uuid
    download_id = str(uuid.uuid4())
    
    # Start download in background thread
    def download_worker():
        try:
            download_status[download_id] = {
                'status': 'downloading',
                'progress': 0,
                'message': 'Starting download...'
            }
            
            # Call the existing download function
            download_and_merge(url, output_path)
            
            download_status[download_id] = {
                'status': 'completed',
                'progress': 100,
                'message': 'Download completed successfully!'
            }
            
        except Exception as e:
            download_status[download_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Error: {str(e)}'
            }
    
    thread = threading.Thread(target=download_worker)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'download_id': download_id,
        'message': 'Download started'
    })

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
        if filename.endswith('.mp4'):
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