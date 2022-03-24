import json

from actions.api.nowapi import NowApi


class Stock:
    def __init__(self):
        # api定义
        self.api = NowApi()
        self.api_params = self.api.params
        self.api_params["app"] = "finance.stock_realtime"

    def fetch_stock(self, id: str) -> str:
        """根据输入或者槽值查询指数信息"""
        return self.get_content(id)

    def get_content(self, ids: str) -> str:
        """根据指数id查询指数信息，调用api接口

        Args:
            ids (str): 股票代码,多个逗号隔开，接口支持接收类型int和str, 统一为str

        Returns:
            str: 查询结果，映射为中文格式
        """
        self.api_params["stoSym"] = ids
        data = json.loads(self.api.get_data(self.api_params))
        success = data.get("success")
        text = data.get("text")

        if success is None or success == 0:
            ret = text
        else:
            ret = ""
            lists = text.get("result").get("lists")
            if lists is not None:
                for _, v in lists.items():
                    ret += f"自定义编号：{v.get('stoid')}\n"
                    ret += f"股票代号：{v.get('symbol')}\n"
                    ret += f"股票编号：{v.get('scode')}\n"
                    ret += f"股票名称：{v.get('sname')}\n"
                    ret += f"股票名称英文：{v.get('sname_eng')}\n"
                    ret += f"开盘价：{v.get('open_price')}\n"
                    ret += f"昨收价：{v.get('yesy_price')}\n"
                    ret += f"当前价：{v.get('last_price')}\n"
                    ret += f"最高价：{v.get('high_price')}\n"
                    ret += f"最低价：{v.get('low_price')}\n"
                    ret += f"涨跌额：{v.get('rise_fall')}\n"
                    ret += f"涨跌幅：{v.get('rise_fall_per')}\n"
                    ret += f"成交量：{v.get('volume')}\n"
                    ret += f"成交量额：{v.get('turn_volume')}\n"
        return ret

class StockHistory:
    def __init__(self):
        # api定义
        self.api = NowApi()
        self.api_params = self.api.params
        self.api_params["app"] = "finance.stock_history"
        # HT1D: 历史1天级别, HT1M 历史1分钟级别
        self.api_params["htType"] = "HT1D"

    def fetch_stock(self, ymd: str, id: str) -> str:
        """根据输入或者槽值查询指数信息

        Args:
            ymd (str): 时间yyyymmdd
            id (str): market id

        Returns:
            str: 查询结果
        """
        return self.get_content(ymd, id)

    def get_content(self, ymd: str, id: str) -> str:
        """根据指数id查询指数信息，调用api接口

        Args:
            ids (str): 指数id，接口支持接收类型int和str, 统一为str

        Returns:
            str: 查询结果，映射为中文格式
        """
        self.api_params["stoSym"] = id
        self.api_params["dateYmd"] = ymd
        data = json.loads(self.api.get_data(self.api_params))
        success = data.get("success")
        text = data.get("text")

        if success is None or success == 0:
            ret = text
        else:
            ret = ""
            dt_lst = text.get("result").get("dtList")
            if dt_lst is not None:
                for v in dt_lst:
                    ret += f"数据日期：{v.get('dateYmd')}\n"
                    ret += f"开盘价：{v.get('openPrice')}\n"
                    ret += f"收盘价：{v.get('closePrice')}\n"
                    ret += f"最高价：{v.get('highPrice')}\n"
                    ret += f"最低价：{v.get('lowPrice')}\n"
                    ret += f"成交量：{v.get('volume')}\n"
                    ret += f"成交额：{v.get('turnover')}\n"
        return ret
