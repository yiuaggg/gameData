import time
import pymongo
import numpy as np
from tools import *
from flask_cors import CORS
from config import *
from functools import wraps
from flask import Flask, jsonify, request, g


app = Flask(__name__)
CORS(app, resources=r'/*')
app.config["SECRET_KEY"] = SECRET_KEY


def login_required(func):
    """ 鉴权装饰器 """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # 获取请求中带的token
        r_token = request.headers.get("Authorization")
        if r_token:
            try:
                data = decrypt_token(r_token)
                g.username = data.get("username")
                expiration = data.get("expiration")
            except Exception as e:
                print(e)
                return jsonify(code="4000", msg="Authentication failed, token format error")

            # 获取存储的token
            s_token = db.Redis(1).get_value(g.username)

            # 验证token是否匹配
            if s_token != r_token:
                return jsonify(code="4000", msg="Authentication failed, token mismatch")

            # 验证token是否失效
            if expiration < int(time.time()):
                return jsonify(code="4010", msg="Authentication failed, token has expired")

        else:
            return jsonify(code="4000", msg="Authentication failed, token needs to be carried")

        # 还可以继续验证接口签名
        return func(*args, **kwargs)
    return wrapper


@app.route('/api/token', methods=['GET'])
def get_token():
    """
    获取 token
    :return:
    """
    message = 'success'
    data = request.args
    api_key = data.get('api_key', '')
    exp, token = generate_token(api_key)
    response = {
        'token': token,
        'expiration': exp.get('expiration', 0)
    }
    db.Redis(1).insert_data(api_key, token, ex=API_EXPIRATION)
    result = {
        'message': message,
        'data': response
    }
    return jsonify(result)


@app.route('/site/search', methods=['POST'])
def search_site():
    """
    数据源主体相似搜索接口
    :return:
    """
    message = 'success'
    data = request.json
    input_text = data.get('input')
    format_text = format_input(input_text)
    emb = m3e.encode(format_text)
    embeddings = np.array(emb, dtype=np.float32).tobytes()
    results = redis_search.knn_search(5, embeddings)
    format_res_list = []
    for result in results:
        score = float(result.score)*1000
        if score < 200:
            format_res = {"id": result.site_id, "name": result.name, "status": result.status, "score": score}
            format_res_list.append(format_res)
    response = {
        "data": format_res_list,
        "message": message
    }
    return jsonify(response)


@app.route('/site/info', methods=['GET'])
def get_site_info():
    """
    数据源主体详情获取接口
    :return:
    """
    result = {}
    message = 'success'
    data = request.args
    if len(data) >= 2:
        message = 'params only input one'
    else:
        site_id = int(data.get('site_id', 0))
        code = str(data.get('code', ''))
        mongo = pymongo.MongoClient(MONGO_HOST, 27017)[MONGODB_NAME][MONGODB_SET_NAME]
        if site_id:
            result = mongo.find_one({'site_id': site_id})
        elif code:
            result = mongo.find_one({'unicode': code})
        else:
            message = 'please check params'
        if result:
            result.pop('_id')
    response = {
        "data": result,
        "message": message
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)