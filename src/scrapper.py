from __future__ import print_function # Python 2/3 compatibiltiy
from namedentities import *
from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS
from src.getRandomProxy import getRandomProxy
import requests
import json
import time

# Route setup
scrapper_blueprint = Blueprint('scrapper_blueprint', __name__, url_prefix='/api')
CORS(scrapper_blueprint, resources=r'/api/*')

@scrapper_blueprint.route('/video/ismonetized', methods=['POST'])
def scrapeVideo():
    proxy = getRandomProxy()
    proxies = {
        "http": f"http://{proxy['ip']}:{proxy['port']}",
    }
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    }

    videoIds = json.loads(request.json['videoIds'])
    # videoIds = ["LRP8d7hhpoQ", "trW_lD9sBt0", "2NGjNQVbydc"]
    # "[\"LRP8d7hhpoQ\",\"trW_lD9sBt0\",\"2NGjNQVbydc\"]"

    sortedIds = []
    isMonetizedStatus = ""

    for vidId in videoIds:
        try:
            url = "https://www.youtube.com/watch?v="+vidId
            r = requests.get(url, timeout=20)
            html = repr(named_entities(r.content.decode("utf-8")))
            # # pos = html.find("getAdBreakUrl")
            pos = html.find("yt_ad")

            if pos < 0:
                isMonetizedStatus = "NOT-MONETIZED"
            else:
                isMonetizedStatus = "MONETIZED"

            sortedIds.append({
                "vid": vidId,
                "status": isMonetizedStatus
            })
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 422)
        
        time.sleep(15)

    return make_response(jsonify({
        "monetizedStatus": sortedIds,
        "status_code": 201
    }),201) 