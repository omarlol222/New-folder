import os
import sys
import tempfile
import shutil
from pathlib import Path
from flask import Flask, request, jsonify, send_file
import subprocess
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "manim-renderer"})

@app.route('/render', methods=['POST'])
def render():
    """
    Render a Manim script and return the video file
    Expected JSON: { "script": "manim python code" }
    """
    try:
        data = request.get_json()
        script = data.get('script')
        
        if not script:
            return jsonify({"error": "No script provided"}), 400

        # Create temporary directory for this render
        temp_dir = tempfile.mkdtemp(prefix='manim_')
        script_path = os.path.join(temp_dir, 'scene.py')
        output_dir = os.path.join(temp_dir, 'media')
        
        logger.info(f"Rendering script in {temp_dir}")
        
        # Write script to file
        with open(script_path, 'w') as f:
            f.write(script)
        
        # Extract scene class name from script
        scene_name = extract_scene_name(script)
        if not scene_name:
            return jsonify({"error": "No Scene class found in script"}), 400
        
        logger.info(f"Found scene class: {scene_name}")
        
        # Run manim to render the script
        # -pql = preview quality low (faster), -qh = quality high
        cmd = [
            'manim',
            '-qm',  # medium quality
            '--format=mp4',
            '--media_dir', output_dir,
            script_path,
            scene_name
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Manim error: {result.stderr}")
            return jsonify({
                "error": "Manim rendering failed",
                "details": result.stderr
            }), 500
        
        # Find the generated video file
        video_path = find_video_file(output_dir)
        
        if not video_path:
            logger.error(f"No video file found in {output_dir}")
            return jsonify({"error": "Video file not generated"}), 500
        
        logger.info(f"Video generated: {video_path}")
        
        # Send the video file
        response = send_file(
            video_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name='animation.mp4'
        )
        
        # Clean up temp directory after sending
        @response.call_on_close
        def cleanup():
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up {temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up: {e}")
        
        return response
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Rendering timeout (max 2 minutes)"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def extract_scene_name(script):
    """Extract the Scene class name from the script"""
    for line in script.split('\n'):
        line = line.strip()
        if line.startswith('class ') and '(Scene)' in line:
            # Extract class name
            class_name = line.split('class ')[1].split('(')[0].strip()
            return class_name
    return None

def find_video_file(media_dir):
    """Find the generated MP4 video file"""
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            if file.endswith('.mp4'):
                return os.path.join(root, file)
    return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
