from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS
from os import path, stat
from time import strftime, gmtime, sleep
from pytube import YouTube

import secrets
import threading
import requests

# Route setup
youtubeToMp4_blueprint = Blueprint('youtubeToMp4_blueprint', __name__, url_prefix='/api')
CORS(youtubeToMp4_blueprint, resources=r'/api/*')

# Init storage path
basedir = path.abspath(path.dirname(__file__))
targetPath = path.join(basedir, '..', 'static/mp4/')
# targetPath = 'C:/Users/"BUYPC COMPUTER"/Documents/SupremeWeb/Projects/viloud/public/uploads'
# targetPath = '/home/tubetargeterapp/hq.myneocast.com/public/uploads/'

def converter(data):
    """
    background Process handled by Threads
    :return: None
    """
    print("Started Task ...")
    print(threading.current_thread().name)
    sleep(5)

    link = f"https://www.youtube.com/watch?v={data['videoId']}"
    youtubeObject = YouTube(link)
    downloadStream = youtubeObject.streams.get_by_itag(22)

    try:
        downloadStream.download(output_path=targetPath, filename=data['filename'])
        videoLength = youtubeObject.length
        videoTitle = youtubeObject.title

        if videoLength >= 3600:
            actualTime = strftime("%H:%M:%S", gmtime(videoLength))
        else:
            actualTime = strftime("%M:%S", gmtime(videoLength))
        fileSize = stat(data['target']).st_size
    except:
        raise Exception('Unable to convert to mp4')
    
    # post to webhook
    requests.post(data['webhook'], data={
        'duration': actualTime,
        'durationInSec': videoLength,
        'fileSize': fileSize,
        'videoTitle': videoTitle,
        'webhook': data['webhook'],
        'user': data['user'],
        'filename': data['filename'],
        'webhookReferer': data['webhookReferer'],
    })

    print("Task completed .....")

# Routes
@youtubeToMp4_blueprint.route('/youtube/convert', methods=['POST']) 
def toMP4():
    name = secrets.token_hex(16)
    filename = f"{name}.mp4" 

    data = {
        'videoId': request.json.get('videoId',''),
        'webhook': request.json.get('webhook', ''),
        'user': request.json.get('user', ''),
        'webhookReferer': request.json.get('webhookReferer', ''),
        'target': targetPath+filename,
        'filename': filename
    }
    
    threading.Thread(target=converter(data)).start()

    return make_response(jsonify({
        'message': 'Task is being processed'
    }))