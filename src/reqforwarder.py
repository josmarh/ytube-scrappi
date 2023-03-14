from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS
from src.getRandomProxy import getRandomProxy
from src.autoSuggestKeyword import validateJSON
from proxy_requests import ProxyRequests
import requests
import urllib.parse
import json

# Route setup
forwarder_blueprint = Blueprint('forwarder_blueprint', __name__, url_prefix='/api')
CORS(forwarder_blueprint, resources=r'/api/*')

@forwarder_blueprint.route('/req', methods=['GET'])
def reqForward():
    if 'url' in request.args:
        url = urllib.parse.unquote(request.args['url'])

        proxy = getRandomProxy()
        proxies = {
            "http": f"http://{proxy['ip']}:{proxy['port']}" 
        }
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
        }

        response = []
        print(proxies)
        try:
            r = requests.get(url, headers=header, proxies=proxies)
            r.raise_for_status()

            if validateJSON(r.content):
                response = json.loads(r.content)

        except Exception as e:
            return make_response(jsonify({"error": "something went wrong"}), 422)

        return jsonify({
            'content': response
        })
