import json
from typing import Any

import requests

from actions.constants import DEFAULT_TIMEOUT
from actions.utils.create_log import logger


class NowApi:
    def __init__(self):
        self.http_url = "http://api.k780.com"
        self.https_url = "https://sapi.k780.com"
        self.params = {
            "appkey": "10003",
            "sign": "b59bc3ef6191eb9f747dd4e83c99f2a4",
            "format": "json"
        }

    def get_data(self, params: Any) -> Any:
        """根据指数id查询指数信息，调用api接口

        Args:
            params (Any): 接口参数

        Returns:
            Any: 查询结果
        """
        ret = {"success": 0, "text": "查询异常"}
        try:
            response = requests.get(self.http_url, params=params, timeout=DEFAULT_TIMEOUT)
            text = json.loads(response.text)
            if text:
                if text.get("success") != "0":
                    ret["success"] = 1
                    ret["text"] = text
                else:
                    error_msg = text.get("msg")
                    ret["text"] = error_msg
                    logger.info(error_msg)
            else:
                text = "查询失败"
                ret["text"] = text
                logger.error(text)
        except requests.exceptions.ConnectionError as ex:
            logger.error(ex)
        except requests.exceptions.RequestException as ex:
            logger.error(ex)
        except Exception as ex:
            logger.error(ex)

        return json.dumps(ret)
