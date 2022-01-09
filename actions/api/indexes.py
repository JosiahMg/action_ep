import json
import os
from typing import Any

import pandas as pd
import requests

from actions.constants import DEFAULT_TIMEOUT
from actions.utils.create_log import logger


class Indexes():
    def __init__(self):
        self.http_url = "http://api.k780.com"
        self.https_url = "https://sapi.k780.com"

        self.params = {
            "app": "finance.globalindex",
            "inxids": None,
            "appkey": "10003",
            "sign": "b59bc3ef6191eb9f747dd4e83c99f2a4",
            "format": "json"
        }

    @staticmethod
    def read_global_index_txt() -> list:
        """
        读取全球指数txt文件，返回指数列表

        Returns:
            list: [str1, str2, ...]
        """
        file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/global_index.txt")
        with open(file, encoding="utf-8") as f:
            content = f.readlines()

        return content

    @staticmethod
    def get_index_ids(name: str) -> Any:
        """
        根据指数名称获取指数id

        Args:
            name (str): 指数名称

        Returns:
            Any: None or frist id value
        """
        file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/global_index.txt")
        df = pd.read_table(file, sep="  ", header=None)
        df.columns = ["id", "name"]
        df_tmp = df[df.name.str.contains(name)]

        if df_tmp.empty:
            # todo 应该支持筛选 输入大于指数名称（被包含），如输入“上证指数数”，文件中的“上证指数”也应符合要求
            return None
        else:
            return str(df_tmp.id.values[0])

    def query_global_index(self) -> str:
        """
        查询已收录的全球指数，从文件中读取

        Returns:
            str: 查询结果
        """
        content = self.read_global_index_txt()
        content = "".join(content)

        return "编号 名称\n" + content

    def __api(self, ids: str) -> str:
        """
        根据指数id查询指数信息，调用api接口

        Args:
            ids (str): 指数id，接口支持接收类型int和str, 统一为str

        Returns:
            str: 查询结果，映射为中文格式
        """
        self.params["inxids"] = ids
        ret = ""
        try:
            response = requests.get(self.http_url, params=self.params, timeout=DEFAULT_TIMEOUT)
            result = json.loads(response.text)
            if result:
                if result.get("success") != "0":
                    lst = result.get("result").get("lists")
                    if lst is not None:
                        for k, v in lst.items():
                            ret += f"版块：{v.get('typeid')}\n"
                            ret += f"指数名称：{v.get('inxnm')}\n"
                            ret += f"昨日收盘价：{v.get('yesy_price')}\n"
                            ret += f"今日开盘价：{v.get('open_price')}\n"
                            ret += f"当前价：{v.get('last_price')}\n"
                            ret += f"涨跌额：{v.get('rise_fall')}\n"
                            ret += f"涨跌幅：{v.get('rise_fall_per')}\n"
                            ret += f"最高价：{v.get('high_price')}\n"
                            ret += f"最低：{v.get('low_price')}\n"
                            ret += f"成交量：{v.get('volume')}(部分股指为0，以实际数据为准)\n"
                            ret += f"成交额：{v.get('turnover')}(部分股指为0，以实际数据为准)\n"
                            ret += f"数据更新时间：{v.get('uptime')}\n"
                else:
                    error_msg = result.get("msg")
                    ret += error_msg
            else:
                logger.error(ret)
                ret += "查询失败"
        except requests.ConnectionError as ex:
            logger.error(ex)
        except Exception as ex:
            logger.error(ex)

        return ret

    def fetch_index(self, x: str) -> str:
        """
        根据输入或者槽值查询指数信息

        Args:
            x (str): 输入或者槽值

        Returns:
            str: 查询结果
        """
        x = x.strip()

        if x.isdigit():
            ids = x
        else:
            ids = self.get_index_ids(x)

        if ids is None:
            content = "暂只支持查询列表中的指数信息"
            logger.error("查找信息" + str(x))
            logger.error("匹配id" + str(ids))
        else:
            content = self.__api(ids)

        return "指数查询结果如下\n" + content
