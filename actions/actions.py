from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.calculator import calculator
from actions.dt import ass_dt
from actions.finance.tool import Tool
from actions.finance.world_index import WorldIndex, WorldIndexHistory
from actions.utils.create_log import logger
from actions.weather import seniverse


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


class FetchIndex(Action):
    def name(self) -> Text:
        return "action_fetch_index"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        for blob in tracker.latest_message["entities"]:
            if blob["entity"] != "global_indexs":
                response = Indexes().fetch_index()

                dispatcher.utter_message(text=response)

        return []


class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.debug('[action]action_calculate')
        equation = tracker.latest_message['text']
        logger.info(f'origin math expression: {equation}')
        expressions = calculator.calculate_mathematic_equation(equation)
        logger.info(f'extract math expression: {expressions[0]}')
        try:
            logger.info(f'expression value : {eval(expressions[0])}')
            dispatcher.utter_message(
                text=str(eval(expressions[0])))  # 只支持第一条数学表达式
        except Exception as e:
            logger.error(e)
            dispatcher.utter_message(text="无法计算出结果，请检查输入是否合法")

        return []


class ConsultStock(Action):
    def name(self) -> Text:
        return "action_consult_stock"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        relative_date = next(tracker.get_latest_entity_values("relative_date"), None)
        company = next(tracker.get_latest_entity_values("company"), None)
        logger.debug('relative_date')
        logger.debug(relative_date)
        logger.debug('company')
        logger.debug(company)
        if relative_date:
            rd = ass_dt.get_date_by_entity(relative_date)
            logger.debug('rd')
            logger.debug(rd)
        else:
            ti = next(tracker.get_latest_entity_values(
                "time"), None)
            logger.debug('ti')
            logger.debug(ti)

        dispatcher.utter_message(text="Hello World!")
        return []


class QueryWorldIndex(Action):
    """query world index"""

    def name(self) -> Text:
        return "action_query_index"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # date
        market_date_tmp = next(tracker.get_latest_entity_values("market_date"), None)
        if market_date_tmp:
            market_date = ass_dt.get_date_by_entity(market_date_tmp)
        else:
            # DucklingEntityExtractor
            duck_date = next(tracker.get_latest_entity_values("time"), None)
            market_date = ass_dt.get_date_by_value(duck_date)
        logger.info(f"market_data: {market_date}")

        # market
        market_name = next(tracker.get_latest_entity_values("market"), None)
        # 市场处理，如果找不到市场，则直接返回提示（可以查下列市场），不用再查询接口
        market_id = Tool.convert_market_id(market_name)
        if market_id is None:
            text = "可以查看如下全球指数情况\n"
            text += Tool.get_world_index_name()
            dispatcher.utter_message(text=text)
            return []
        logger.info(f"market_name: {market_name}, market_id: {market_id}")

        # 时间处理
        is_today = False
        market_strftime = None
        try:
            market_strftime = market_date.strftime("%Y%m%d")
        except Exception:
            is_today = True
        else:
            if market_strftime == datetime.today().strftime("%Y%m%d"):
                is_today = True
        logger.info(f"is_today: {is_today}, market_strftime: {market_strftime}")

        # 如果是当天，则调用index api, 否则调用index history api
        if is_today:
            response_text = WorldIndex().fetch_index(market_id)
        else:
            response_text = WorldIndexHistory().fetch_index(market_strftime, market_id)
        logger.info(f"api response_text: {response_text}")
        
        dispatcher.utter_message(text=response_text)
        return []
