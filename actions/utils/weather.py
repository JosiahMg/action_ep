"""
Weather data is provided by https://www.seniverse.com/,
below code are modified from https://github.com/seniverse/seniverse-api-demos

FREE version only get future 3 days!
"""
import os
import requests
import json
from actions.utils.const_value import API, KEY, UNIT, LANGUAGE


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
