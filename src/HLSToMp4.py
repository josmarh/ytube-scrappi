from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS
from os import path, stat
from time import strftime, gmtime, sleep

import subprocess
import secrets
import threading
import requests

# Route setup
HLSToMp4_blueprint = Blueprint('HLSToMp4_blueprint', __name__, url_prefix='/api')
CORS(HLSToMp4_blueprint, resources=r'/api/*')

# Init storage path
basedir = path.abspath(path.dirname(__file__))
targetPath = path.join(basedir, '..', 'static/mp4/')
# targetPath = 'C:/Users/"BUYPC COMPUTER"/Documents/SupremeWeb/Projects/viloud/public/uploads'
targetPathMain = '/home/tubetargeterapp/linkomaticapp.com/app/static/mp4/'

def converter(data):
    """
    background Process handled by Threads
    :return: None
    """
    print("Started Task (HLS to MP4)...")
    print(threading.current_thread().name)
    sleep(5)

    command_1 = ["ffmpeg", "-i", data['link'], "-acodec", "copy", "-vcodec", "copy", data['target']]
    command_2 = ["ffmpeg", "-i", data['link'], "-acodec", "copy", "-bsf:a", "aac_adtstoasc", "-vcodec",  "copy", data['target']]

    if subprocess.run(command_1).returncode == 0:
        print ("command_1 Script Ran Successfully...")
    elif subprocess.run(command_2).returncode == 0:
        print ("command_2 Script Ran Successfully...")

    if path.exists(data['target']):
        # Get video length
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", data['target']],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

        videoLength = round(float(result.stdout))
        if videoLength >= 3600:
            actualTime = strftime("%H:%M:%S", gmtime(videoLength))
        else:
            actualTime = strftime("%M:%S", gmtime(videoLength))
        fileSize = stat(data['target']).st_size
    else:
        raise Exception('Unable to convert hls')

    # post to webhook
    requests.post(data['webhook'], data={
        'duration': actualTime,
        'durationInSec': videoLength,
        'fileSize': fileSize,
        'videoTitle': data['filename'],
        'webhook': data['webhook'],
        'user': data['user'],
        'webhookReferer': data['webhookReferer'],
        'jobOwner': data['jobOwner'],
        'lhash': data['lhash'],
        'channels': data['channels'],
    })

    print("Task completed .....")
    
    
# Routes
@HLSToMp4_blueprint.route('/hls/convert', methods=['POST']) 
def toMP4():
    name = secrets.token_hex(16)
    filename = f"{name}.mp4" 

    data = {
        'link': request.json.get('link',''),
        'webhook': request.json.get('webhook', ''),
        'user': request.json.get('user', ''),
        'jobOwner': request.json.get('jobOwner', ''),
        'lhash': request.json.get('lhash', ''),
        'channels': request.json.get('channels', ''),
        'webhookReferer': request.json.get('webhookReferer', ''),
        'target': targetPath+filename,
        'filename': name
    }
    
    threading.Thread(target=converter(data)).start()

    return make_response(jsonify({
        'message': 'Task is being processed'
    }))