from flask import Blueprint, request, jsonify, make_response, url_for
from flask_cors import CORS
from os import path, stat, rename, system, remove
from time import strftime
from time import gmtime

import subprocess
import json
import m3u8_To_MP4
import secrets

# Route setup
m3u8ToMp4_blueprint = Blueprint('m3u8ToMp4_blueprint', __name__, url_prefix='/api')
CORS(m3u8ToMp4_blueprint, resources=r'/api/*')

# Init storage path
basedir = path.abspath(path.dirname(__file__))
targetPath = path.join(basedir, '..', 'static/mp4/')

# Routes
@m3u8ToMp4_blueprint.route('/m3u8/convert', methods=['POST'])
def toMP4():
    link = request.json.get('link','')
    webhook = request.json.get('webhook', '')
    user = request.json.get('user', '')    

    try:
        m3u8_To_MP4.multithread_download(link)     

        # Extract video name
        link = link.split('/')
        link_pos = link[len(link)-1]
        name = link_pos.split('.')[0]
        filename = f"{name}.mp4" 

        # Rename file and move to path
        rename('m3u8_To_MP4.mp4', targetPath + filename)
        fileSize = stat(targetPath + filename).st_size
        downloadPath = url_for('static', filename='mp4/' + filename, _external=True)

        # Get video duration in seconds
        out = subprocess.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", targetPath+filename])
        ffprobe_data = json.loads(out)
        videoLength = round(float(ffprobe_data["format"]["duration"])) 

        if videoLength >= 3600:
            actualTime = strftime("%H:%M:%S", gmtime(videoLength))
        else:
            actualTime = strftime("%M:%S", gmtime(videoLength)) 
    except Exception as e:
        print(e)
        return make_response(jsonify({'error':'Unable to convert hls'}),422)    
    return make_response(jsonify({
        'downloadPath': downloadPath,
        'duration': actualTime,
        'durationInSec': videoLength,
        'fileSize': fileSize,
        'videoTitle': name,
        'webhook': webhook,
        'user': user,
        'status': 'success'
    }),201)


@m3u8ToMp4_blueprint.route('/m3u8/convert/v2', methods=['POST'])
def toMP4_v2():
    link = request.json.get('link','')
    webhook = request.json.get('webhook', '')
    user = request.json.get('user', '')
    name = secrets.token_hex(16)
    filename = f"{name}.mp4" 
    
    try:
        command = f"ffmpeg -i {link} -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 {targetPath+filename}"
        system(command)

        # Rename file and move to path
        # rename(filename, targetPath + filename)
        fileSize = stat(targetPath + filename).st_size
        downloadPath = url_for('static', filename='mp4/' + filename, _external=True)

        # Get video duration in seconds
        out = subprocess.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", targetPath+filename])
        ffprobe_data = json.loads(out)
        videoLength = round(float(ffprobe_data["format"]["duration"])) 

        if videoLength >= 3600:
            actualTime = strftime("%H:%M:%S", gmtime(videoLength))
        else:
            actualTime = strftime("%M:%S", gmtime(videoLength)) 
    except Exception as e:
        print(e)
        return make_response(jsonify({'error':'Unable to convert hls'}),422)
    return make_response(jsonify({
        'downloadPath': downloadPath,
        'duration': actualTime,
        'durationInSec': videoLength,
        'fileSize': fileSize,
        'videoTitle': name,
        'webhook': webhook,
        'user': user,
        'status': 'success'
    }),201)

@m3u8ToMp4_blueprint.route('/mp4/delete/v2', methods=['POST'])
def deleteMP4():
    videoId = request.json.get('videoId', '')

    try:
        remove(targetPath + videoId + '.mp4')
    except Exception as e:
        print(e)
        return make_response(jsonify({'error': 'Unable to remove file'}),422)
    return make_response(jsonify({
        'message': 'File removed.',
    }))