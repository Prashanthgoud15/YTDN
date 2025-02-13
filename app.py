from flask import Flask, request, jsonify, send_from_directory
import os
import yt_dlp

app = Flask(__name__)

# Folder to store downloaded files
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_video(url, format):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if format == 'mp4' else 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'retries': 3,  # Retry up to 3 times if download fails
        'ignoreerrors': True,  # Ignore errors and continue
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)
            return file_name
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None

@app.route('/')
def home():
    return send_from_directory(".", "index.html", mimetype="text/html")


@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format = data.get('format')

    if not url:
        return jsonify({"success": False, "detail": "URL is required"}), 400

    try:
        file_name = download_video(url, format)
        if file_name:
            return jsonify({"success": True, "file_name": os.path.basename(file_name)})
        else:
            return jsonify({"success": False, "detail": "Failed to download video. Please try again."}), 500
    except Exception as e:
        return jsonify({"success": False, "detail": str(e)}), 500

@app.route('/files/<filename>')
def files(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # Bind to 0.0.0.0 and use port 10000