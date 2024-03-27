import json

import db
import time
import pymongo
import numpy as np
from tools import *
from flask_cors import CORS
from config import *
from get_data import *
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


@app.route('/api/getMenuTypes', methods=['GET'])
def getMenuTypes():
    """
    获取游戏菜单类型
    :return:
    """
    response = {
        "data": ['Hot','New', 'slot_N0.4_false', 'slot_N0.5_false', 'slot_N0.6_false', 'slot_TAIWANver_false',
                 'slot_true', 'cr_Pachinko_CLOSE_', 'cr_Pachinko_MAX_', 'cr_Pachinko_MID_', 'cr_Pachinko_LM_',
                 'cr_Pachinko_L_', 'oneslot,onepachinko'],
        "message": 'success'
    }
    return jsonify(response)


@app.route('/api/searchMenuGames', methods=['GET'])
def searchMenuGames():
    """
    查询菜单游戏列表
    key_type: Hot,New,slot_N0.4_false,slot_N0.5_false,slot_N0.6_false,slot_TAIWANver_false,slot_true,cr_Pachinko_CLOSE_
    cr_Pachinko_MAX_,cr_Pachinko_MID_,cr_Pachinko_LM_,cr_Pachinko_L_,oneslot,onepachinko
    :return:
    """
    result = {}
    message = 'success'
    data = request.args
    key = str(data.get('key', ''))
    curPage = int(data.get('curPage', 1))
    pageSize = int(data.get('pageSize', 20))
    if not data:
        message = 'key is a necessary parameter'
    try:
        result = get_game_list(curPage, pageSize, key)
    except Exception as e:
        print(e)
        message = str(e)
    response = {
        "data": result,
        "message": message
    }
    return jsonify(response)


@app.route('/api/searchMachines', methods=['GET'])
def searchMachines():
    """
    查询机器列表详情
    :return:
    """
    result = []
    message = 'success'
    data = request.args
    game_id = int(data.get('game_id', 0))
    if not game_id:
        message = 'game_id is a necessary parameter'
    try:
        result = get_game_detail(game_id)
    except Exception as e:
        print(e)
        message = str(e)
    response = {
        "data": result,
        "message": message
    }
    return jsonify(response)


@app.route('/api/searchPlay', methods=['POST'])
def searchPlay():
    """
    查询正在玩的机器列表
    :return:
    """
    result = []
    message = 'success'
    data = request.json
    user_token = data.get('user_token', '')
    try:
        result = get_playing_list(user_token)
    except Exception as e:
        print(e)
        message = str(e)
    response = {
        "data": result,
        "message": message
    }
    return jsonify(response)


@app.route('/api/removeMachine', methods=['POST'])
def removeMachine():
    """
    查询正在玩的机器列表
    :return:
    """
    result = ''
    message = 'success'
    data = request.json
    machine_id = int(data.get('machine_id', 0))
    user_token = data.get('user_token', '')
    if not machine_id:
        message = 'machine_id is a necessary parameter'
    if not user_token:
        message = 'user_token is a necessary parameter'
    try:
        result = push_stop_machine(machine_id, user_token)
    except Exception as e:
        print(e)
        message = str(e)
    response = {
        "data": result,
        "message": message
    }
    return jsonify(response)


@app.route('/api/getVideo', methods=['GET'])
def getVideo():
    """
    获取游戏视频列表
    video_type: 1,弹珠机；2,老虎机
    :return:
    """
    result = ''
    message = 'success'
    data = request.args
    print(data)
    video_type = int(data.get('video_type', 1))
    print(video_type)
    if not video_type:
        message = 'video_type is a necessary parameter'
    try:
        if video_type == 1:
            d_video_list = db.Redis(0).get_list('danZhuJi')
            result = db.Redis(0).get_values(d_video_list)
        if video_type == 2:
            l_video_list = db.Redis(0).get_list('laoHuJi')
            result = db.Redis(0).get_values(l_video_list)
    except Exception as e:
        print(e)
        message = str(e)
    response = {
        "data": result,
        "message": message
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)
