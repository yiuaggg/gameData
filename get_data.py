import math
import requests
from tools import get_token


headers = {
    "Token": get_token()
}


def get_game_detail(game_id):
    """
    获取游戏详情
    :return:
    """
    request_url = "https://api.dasheng66.com/game/searchMachines"
    format_data = {
        "gameId": game_id,
        "closeShop": "false"
    }
    response = requests.get(request_url, params=format_data, headers=headers)
    try:
        game_info_list = response.json()
    except Exception as e:
        print(e)
        print('token 过期')
        game_info_list = None
    result_list = []
    if game_info_list:
        for game_info in game_info_list:
            playUrlList = []
            machineId = game_info['machineId']
            base_url = "https://www.dasheng66.com/amigoh5/#/game?machineId={}&bitType={}&token="
            playUrlList.append(base_url.format(machineId, 'LC'))
            playUrlList.append(base_url.format(machineId, 'SD'))
            playUrlList.append(base_url.format(machineId, 'HD'))
            res_info = {
                "isPlaying": game_info['isPlaying'],  # 是否在使用中
                "playerId": game_info['playerId'],  # 使用者用户ID
                "machineName": game_info['machineName'],  # 机器名称
                "machineId": game_info['machineId'],  # 机器ID
                "playUrls": playUrlList,  # 游戏页面url
                "durations": game_info['slotSignalBagDuration']['durations'],  # 柱状图数据组
                "probability": game_info['slotSignalBagDuration']['probability'],  # 合并确率
                "tdMaxProfit": game_info['slotSignalBagDuration']['tdMaxProfit'],  # 今日最高
                "agoMaxProfit": game_info['slotSignalBagDuration']['agoMaxProfit'],  # 历史最高
                "current_num": game_info['slotSignalBagDuration']['num'],  # 当前数量
                "totalRound": game_info['slotSignalBagDuration']['totalRound'],  # 累计
                "ydTotalRound": game_info['slotSignalBagDuration']['ydTotalRound'],  # 昨日次数
                "tdRBCount": game_info['slotSignalBagDuration']['tdRBCount'],  # 今日RB数
                "ydRBCount": game_info['slotSignalBagDuration']['ydRBCount'],  # 昨日RB数
                "bdRBCount": game_info['slotSignalBagDuration']['bdRBCount'],  # 前日RB数
                "tdBBCount": game_info['slotSignalBagDuration']['tdBBCount'],  # 今日BB数
                "ydBBCount": game_info['slotSignalBagDuration']['ydBBCount'],  # 昨日BB数
                "bdBBCount": game_info['slotSignalBagDuration']['bdBBCount'],  # 前日BB数
                "restartTime": game_info['slotSignalBagDuration']['restartTime'],  # 重启时间
            }
            result_list.append(res_info)
    return result_list


def get_game_list(page_number, pageSize, key):
    """
    获取游戏机列表数据
    :return:
    """
    request_url = "https://api.dasheng66.com/game/searchMenuGames"
    format_data = {
        "key": key,
        "curPage": page_number,
        "pageSize": pageSize,
        "name": ""
    }
    response = requests.get(request_url, params=format_data, headers=headers)
    try:
        json_data = response.json()
    except Exception as e:
        print(e)
        json_data = None
        print('token 过期')
    if json_data:
        game_info_list = []
        game_list = json_data.get('items')
        page_info = json_data.get('page')
        for game in game_list:
            machineType = game['machineType']
            if machineType == 'Pachinko':
                roundCost = int(game.get('odds', 0)) * float(game.get('roundAmount')) * 10
                if len(str(roundCost)) > 10:
                    roundCost = float(str(roundCost)[:6])
                result = {
                    'gameId': game['gameId'],  # 游戏ID
                    'gameType': game['gameType'],  # 游戏类型
                    'name': game['japaneseName'],  # 游戏名称
                    'joinJackpot': game['joinJackpot'],  # 是否参与赏金活动
                    'machineType': machineType,  # 游戏类型
                    'probability': game['probability'].split('/')[-1],  # 天井数
                    'coverImg': game['gameUrl'],  # 游戏机封面
                    'inRushRate': game['inRushRate'],  # 突入
                    'rushRate': game['rushRate'],  # 继续率
                    'eachBead': (float(game.get('costRate', 0)) * 10)*(int(game.get('odds'))/2),  # 每珠
                    'roundCost': roundCost,  # 每回合扣
                    'residue': int(game.get('totalSeats')) - int(game.get('surplusSeats'))  # 剩余可用台数
                }
            else:
                result = {
                    'gameId': game['gameId'],  # 游戏ID
                    'gameType': game['gameType'],  # 游戏类型
                    'name': game['japaneseName'],  # 游戏名称
                    'joinJackpot': game['joinJackpot'],  # 是否参与赏金活动
                    'machineType': machineType,  # 游戏类型
                    'probability': game['probability'],  # 天井
                    'coverImg': game['gameUrl'],  # 游戏机封面
                    'slotType': game['slotType'],  # 游戏机类型
                    'realAdd': game['realAdd'],  # 纯增
                    'odds': game.get('odds', 0)*10,  # 每枚
                    'residue': int(game.get('totalSeats'))-int(game.get('surplusSeats'))  # 剩余可用台数
                }
            game_info_list.append(result)
        result_info = {"page": page_info, "rows": game_info_list}
    else:
        result_info = None
    return result_info


def get_playing_list(token):
    """
    获取正在玩的机器列表
    :return:
    """
    if token:
        headers['Token'] = token
    request_url = "https://api.dasheng66.com/game/searchPlay"
    response = requests.get(request_url, headers=headers)
    try:
        result = response.json()
    except Exception as e:
        print(e)
        print('token 过期')
        result = None
    return result


def push_stop_machine(machine_id, token):
    """
    停止正在玩的机器
    :param machine_id:
    :param token:
    :return:
    """
    if token:
        headers['Token'] = token
    request_url = "https://api.dasheng66.com/game/remove/{}".format(machine_id)
    response = requests.post(request_url, headers=headers)
    try:
        result = response.json()
    except Exception as e:
        print(e)
        print('token 过期')
        result = None
    return result


if __name__ == '__main__':
    res = get_game_detail(1683)
    print(res)
