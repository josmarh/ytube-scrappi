from flask import Blueprint, request, jsonify
from flask_cors import CORS
from src.getRandomProxy import getRandomProxy
import requests
import urllib.parse
import json

# Route setup
autosuggest_blueprint = Blueprint('autosuggest_blueprint', __name__, url_prefix='/api')
CORS(autosuggest_blueprint, resources=r'/api/*')

@autosuggest_blueprint.route('/autosuggest/keywords', methods=['GET'])
def autoSuggestKeywords():
    if 'url' in request.args and 'provider' in request.args:
        url = urllib.parse.unquote(request.args['url'])
        provider = request.args['provider']

        proxy = getRandomProxy()
        proxies = {
            "http": f"http://{proxy['ip']}:{proxy['port']}"
        }
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
        }

        sortedKeywords = []
        # get first batch
        sortedKeywords = autoSuggestKeywordsSingle(url, provider, header, proxies)

        alphas = list('abcdefghijklmnopqrstuvwxyz1234567890')
        res = []

        for item in alphas:
            r = requests.get(url+item, headers=header, proxies=proxies, stream=True)
            r.raise_for_status()

            # with open('keyword.txt', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                res = chunk

            if validateJSON(res):
                resultJson = json.loads(res)
                if provider == 'youtube':
                    for i, v in enumerate(resultJson[1]):
                        if resultJson[1][i][0] != '':
                            sortedKeywords.append(resultJson[1][i][0])

                elif provider == 'google':
                    for i, v in enumerate(resultJson[1]):
                        if resultJson[1][i] != '':
                            sortedKeywords.append(resultJson[1][i])

        return jsonify({
            'data': sortedKeywords
        })
                

def autoSuggestKeywordsSingle(url, provider, header, proxies):

    r = requests.get(url, headers=header, proxies=proxies, stream=True)
    r.raise_for_status()
    res = []
    sortedKeywords = []

    for chunk in r.iter_content(chunk_size=8192):
        res = chunk

    if validateJSON(res):
        resultJson = json.loads(res)
        
        if provider == 'youtube':
            for i, v in enumerate(resultJson[1]):
                if resultJson[1][i][0] != '':
                    sortedKeywords.append(resultJson[1][i][0])

        elif provider == 'google':
            for i, v in enumerate(resultJson[1]):
                if resultJson[1][i] != '':
                    sortedKeywords.append(resultJson[1][i])

    return sortedKeywords


def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True