from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS
from os import path, remove, chdir
from time import sleep

import subprocess
import threading
import glob

# Route setup
Mp4ToHLS_blueprint = Blueprint('Mp4ToHLS_blueprint', __name__, url_prefix='/api')
CORS(Mp4ToHLS_blueprint, resources=r'/api/*')

# Init storage path
videoToConvertPath = '/home/tubetargeterapp/hq.myneocast.com/public/uploads/'
hlsChannelPath = '/nginx/channels/'

def converter(data):
    """
    background Process handled by Threads
    :return: None
    """
    print(data)
    print("Started Task (MP4 to HLS) ...")
    print(threading.current_thread().name)
    sleep(5)

    if data['action'] == 'createHLS':
        if path.exists(f"{data['streamPath']}.m3u8"):
            for file in glob.glob(f"{data['streamPath']}*.ts"):
                remove(file)
            remove(f"{data['streamPath']}.m3u8")

        command = ["ffmpeg", "-re", "-f", "concat", "-i", data['fileName'], "-b:v", "1M", "-g", "60", "-hls_time", "10", "-hls_list_size", "0", "-hls_segment_size", "17000000", data['streamPath']+'.m3u8']

        if path.exists(data['filePath']):
            chdir(data['filePath'])
            if subprocess.run(command).returncode == 0:   
                print ("Conversion successful")
                print("Task completed .....")

    elif data['action'] == 'deleteHLS':
        if path.exists(f"{data['filePath']}{data['fileName']}.m3u8"):
            try:
                for file in glob.glob(f"{data['filePath']}{data['fileName']}*.ts"):
                    remove(file)
                remove(f"{data['filePath']}{data['fileName']}.m3u8")
            except Exception as e:
                print(e)
                raise Exception('Unable to delete hls')
            print("Delete HLS Task completed .....")

# Routes
@Mp4ToHLS_blueprint.route('/mp4/convert/hls', methods=['POST']) 
def toHLS():
    data = {
        'action': request.json.get('action', ''),
        'filePath': request.json.get('filePath', ''),
        'fileName': request.json.get('fileName', ''),
        'streamPath': request.json.get('streamPath', ''),
    }
    
    threading.Thread(target=converter(data)).start()

    return make_response(jsonify({
        'message': 'Task is being processed'
    }))