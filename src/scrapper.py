from __future__ import print_function # Python 2/3 compatibiltiy
from namedentities import *
from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS
from src.getRandomProxy import getRandomProxy
import requests
import json 

# Route setup
scrapper_blueprint = Blueprint('scrapper_blueprint', __name__, url_prefix='/api')
CORS(scrapper_blueprint, resources=r'/api/*')

@scrapper_blueprint.route('/video/ismonetized', methods=['POST'])
def scrapeVideo():
    videoIds = json.loads(request.json['videoIds'])

    proxy = getRandomProxy()
    proxies = {
        "http": f"http://{proxy['ip']}:{proxy['port']}",
        # "https": f"https://{proxy['ip']}:{proxy['port']}",
    }
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    }

    # videoIds = ["LRP8d7hhpoQ", "trW_lD9sBt0", "2NGjNQVbydc"]
    sortedIds = []
    isMonetizedStatus = ""

    for item in videoIds:
        try:
            r = requests.get("https://www.youtube.com/watch?v="+item, headers=header, proxies=proxies)
            html = repr(named_entities(r.content.decode("utf-8")))
            pos = html.find("getAdBreakUrl")

            if pos < 0:
                isMonetizedStatus = "NOT-MONETIZED"
            else:
                isMonetizedStatus = "MONETIZED"

            sortedIds.append({
                "vid": item,
                "status": isMonetizedStatus
            })
        except Exception as e:
            return make_response(jsonify({"error": e}), 422)

    return make_response(jsonify({
        "monetizedStatus": sortedIds,
        "status_code": 201
    }),201) 