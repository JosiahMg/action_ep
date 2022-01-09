# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from datetime import datetime
from typing import Any, Text, Dict, List

from actions.api.indexes import Indexes
from actions.dt import ass_dt
from actions.utils.create_log import logger
from actions.weather import seniverse
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionTellDate(Action):
    '''
    # TODO: 指定日期询问星期
    function: 询问日期的动作
    '''

    def name(self) -> Text:
        return "action_tell_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 首先判断是否有DIETClassifier识别的实体 用于获取date的实体(大后天 大前天)
        logger.debug('[action]action_tell_date')

        entity_date = next(
            tracker.get_latest_entity_values("relative_date"), None)

        if entity_date:
            logger.debug(f'[entity value:relative_date]{entity_date}')
            dispatcher.utter_message(
                text=ass_dt.get_date_by_entity(entity_date))
        else:
            value_date = next(tracker.get_latest_entity_values(
                "time"), None)  # DucklingEntityExtractor
            logger.debug(f'[entity value:time]{value_date}')
            dispatcher.utter_message(
                text=ass_dt.get_date_by_value(value_date))

        return []


class ActionDateDifferent(Action):
    def name(self) -> Text:
        return "action_date_different"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.debug('[action]action_date_different')
        dt_list = []

        for dt in tracker.get_latest_entity_values("time"):
            dt_list.append(dt)

        logger.debug(f'[entity value:time]{dt_list}')
        if len(dt_list) == 0:
            dispatcher.utter_message(response='utter_un_come_true')

        if len(dt_list) == 1:
            d0 = ass_dt.get_datetime(dt_list[0])
            d1 = datetime.today()

        if len(dt_list) == 2:
            d0 = ass_dt.get_datetime(dt_list[0])
            d1 = ass_dt.get_datetime(dt_list[1])

        if d1 > d0:
            d0, d1 = d1, d0
        days = (d0 - d1).days

        dispatcher.utter_message(
            text=f"{d1.strftime('%Y-%m-%d')} 与 {d0.strftime('%Y-%m-%d')} 相差 {days} 天")

        return []


class ActionTellTime(Action):
    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.debug('[action]:action_tell_time')
        # 首先判断是否有DIETClassifier识别出Place实体
        entity_local = next(tracker.get_latest_entity_values("place"), None)
        if entity_local:
            logger.debug(f'[entity value:place]{entity_local}')
            dispatcher.utter_message(
                text=ass_dt.get_time_by_entity(entity_local))
        else:
            value_date = next(tracker.get_latest_entity_values(
                "time"), None)  # DucklingEntityExtractor
            logger.debug(f'[entity value:time]{entity_local}')
            dispatcher.utter_message(
                text=ass_dt.get_time_by_value(value_date))

        return []


class ActionTimeDifferent(Action):
    def name(self) -> Text:
        return "action_time_different"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.debug('[action]action_time_different')
        place_list = set()

        for dt in tracker.get_latest_entity_values("place"):
            place_list.add(dt)
        logger.debug(f'[entity value:place]{place_list}')
        dispatcher.utter_message(
            text=ass_dt.get_place_time_different(list(place_list)))

        return []


class ActionTellWeather(Action):
    def name(self) -> Text:
        return "action_tell_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.debug('[action]action_tell_weather')
        entity_local = tracker.get_slot("place")
        entity_date = next(
            tracker.get_latest_entity_values("relative_date"), None)

        day_delta = 0
        if entity_date:
            logger.info(f'extract relative_date entity: {entity_date}')
            day_delta = ass_dt.get_day_delta(entity_date)
            if day_delta:
                if day_delta < 0:
                    dispatcher.utter_message(text="不支持过去时间的天气查询！")
                    return []
                if day_delta > 2:
                    dispatcher.utter_message(text="仅支持查询三天内的天气！")
                    return []
        logger.info(f'extract local entity: {entity_local}')
        weather_res = seniverse.get_weather_by_day(entity_local, day_delta)
        logger.info(f'get weather info: {weather_res}')
        if not weather_res:
            dispatcher.utter_message(text="暂不支持县级以下级别的天气查询！")
            return []

        dispatcher.utter_message(text=f"{weather_res['city_name']}的天气: ")
        for wea in weather_res['daily']:
            wea_str = f"{wea['date']}: 白天{wea['text_day']} 夜晚{wea['text_night']} 最高气温{wea['high']}° 最低气温{wea['low']}° {wea['wind_direction']}风{wea['wind_scale']}级"
            dispatcher.utter_message(text=wea_str)

        return []


class QueryGlobalIndex(Action):
    def name(self) -> Text:
        return "action_query_global_index"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        for blob in tracker.latest_message["entities"]:
            if blob["entity"] != "global_indexs":
                # response = Indexes().query_global_index()
                response = Indexes().fetch_index()
                dispatcher.utter_message(text=response)

        return []
