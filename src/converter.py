from flask import Blueprint, request, jsonify, make_response, url_for
from flask_cors import CORS
from os import path, stat, remove
from pytube import YouTube
from time import strftime
from time import gmtime

# Route setup
converter_blueprint = Blueprint('converter_blueprint', __name__, url_prefix='/api')
CORS(converter_blueprint, resources=r'/api/*')

# Init storage path
basedir = path.abspath(path.dirname(__file__))
targetPath = path.join(basedir, '..', 'static/mp4/')

# Routes
@converter_blueprint.route('/mp4/convert', methods=['POST'])
def toMP4():
    videoId = request.json.get('videoId', '')
    webhook = request.json.get('webhook', '')
    user = request.json.get('user', '')
    link = 'https://www.youtube.com/watch?v='+videoId
    
    youtubeObject = YouTube(link)
    downloadStream = youtubeObject.streams.get_by_itag(22)

    try:
        filename = f"{videoId}.mp4"
        downloadStream.download(output_path=targetPath, filename=filename)
        videoLength = youtubeObject.length
        videoTitle = youtubeObject.title

        if videoLength >= 3600:
            actualTime = strftime("%H:%M:%S", gmtime(videoLength))
        else:
            actualTime = strftime("%M:%S", gmtime(videoLength))
        fileSize = stat(targetPath + filename).st_size
        downloadPath = url_for('static', filename='mp4/' + filename, _external=True)
    except:
        return make_response(jsonify({'error': 'Unable to convert video'}),422)
    return make_response(jsonify({
        'downloadPath': downloadPath,
        'duration': actualTime,
        'durationInSec': videoLength,
        'fileSize': fileSize,
        'videoTitle': videoTitle,
        'webhook': webhook,
        'user': user,
        'status': 'success'
    }),201)


# https://youtu.be/kV_jtZGVkn4
@converter_blueprint.route('/mp4/delete', methods=['POST'])
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
