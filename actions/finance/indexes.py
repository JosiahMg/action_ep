import json
import os
from typing import Any

import pandas as pd
from actions.api.nowapi import NowApi
from actions.constants import ACTIONS_PATH
from actions.utils.create_log import logger


class Indexes:
    def __init__(self):
        # 文件路径
        self.global_index_file = os.path.join(ACTIONS_PATH, "global_index.txt")
        # api定义
        self.api = NowApi()
        self.api_params = self.api.params
        self.api_params["app"] = "finance.globalindex"

    @staticmethod
    def read_file(file: str) -> []:
        """读取全球指数文件，返回指数列表

        Args:
            file (str): 文件路径

        Returns:
            list: [str1, str2, ...]
        """
        with open(file, encoding="utf-8") as f:
            content = f.readlines()

        return content

    @staticmethod
    def get_index_ids(table_file: str, name: str) -> Any:
        """根据指数名称获取指数id

        Args:
            table_file (str): 文件路径
            name (str): 指数名称

        Returns:
            Any: None or frist id value
        """
        df = pd.read_table(table_file, sep="  ", header=None)
        df.columns = ["id", "name"]
        df_tmp = df[df.name.str.contains(name)]

        if df_tmp.empty:
            # todo 应该支持筛选 输入大于指数名称（被包含），如输入“上证指数数”，文件中的“上证指数”也应符合要求
            return None
        else:
            return str(df_tmp.id.values[0])

    def query_global_index(self) -> str:
        """查询已收录的全球指数，从文件中读取

        Returns:
            str: 查询结果
        """
        content = self.read_file(file=self.global_index_file)

        return "编号 名称\n" + "".join(content)

    def fetch_index(self, x: str) -> str:
        """根据输入或者槽值查询指数信息

        Args:
            x (str): 输入或者槽值

        Returns:
            str: 查询结果
        """
        x = x.strip()

        if x.isdigit():
            ids = x
        else:
            ids = self.get_index_ids(table_file=self.global_index_file, name=x)

        if ids is None:
            content = "暂只支持查询列表中的指数信息"
            logger.error(f"查找信息:{str(x)}, 匹配id:{str(ids)}")
        else:
            content = self.get_content(ids)

        return "指数查询结果如下\n" + content

    def get_content(self, ids: str) -> str:
        """根据指数id查询指数信息，调用api接口

        Args:
            ids (str): 指数id，接口支持接收类型int和str, 统一为str

        Returns:
            str: 查询结果，映射为中文格式
        """
        self.api_params["inxids"] = ids
        data = json.loads(self.api.get_data(self.api_params))
        success = data.get("success")
        text = data.get("text")

        if success is None or success == 0:
            ret = text
        else:
            ret = ""
            lst = text.get("result").get("lists")
            if lst is not None:
                for _, v in lst.items():
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

        return ret
