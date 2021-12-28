"""
Weather data is provided by https://www.seniverse.com/,
below code are modified from https://github.com/seniverse/seniverse-api-demos

# 心知天气接口  https://www.seniverse.com/
知心天气接口  只提供未来三天免费的天气查询
"""
import os
import requests
import json

try:
    from actions.private import KEY  # KEY值需要
except Exception:
    KEY = ""
    print('Please register https://www.seniverse.com get KEY')


UID = "U785B76FC9"  # 用户ID

LOCATION = 'beijing'  # 所查询的位置，可以使用城市拼音、v3 ID、经纬度等
API = 'https://api.seniverse.com/v3/weather/daily.json'  # API URL，可替换为其他 URL
UNIT = 'c'  # 单位
LANGUAGE = 'zh-Hans'  # 查询结果的返回语言


def fetch_weather(location, start=0, days=15):
    result = requests.get(API, params={
        'key': KEY,
        'location': location,
        'language': LANGUAGE,
        'unit': UNIT,
        'start': start,
        'days': days
    }, timeout=3)
    result = result.json()  # dict
    return result


def get_weather_by_day(location, day=0):
    """
    指定具体哪一天的天气, 目前只支持三天
    0: 今天
    1: 明天
    2: 后天
    """
    normal_result = {}
    result = fetch_weather(location)
    try:
        normal_result['city_name'] = result["results"][0]["location"]['name']
        normal_result['daily'] = []
        if isinstance(day, int):
            normal_result['daily'].append(result["results"][0]["daily"][day])
        elif isinstance(day, list):
            for d in sorted(day):
                normal_result['daily'].append(result["results"][0]["daily"][d])
    except Exception as e:
        print("You don't have access to data of this city.")
    return normal_result


if __name__ == '__main__':
    # default_location = "上海"
    # result = fetch_weather(default_location)
    # print(json.dumps(result, ensure_ascii=False))

    default_location = "武汉"
    result = get_weather_by_day(default_location)
    print(json.dumps(result, ensure_ascii=False))
