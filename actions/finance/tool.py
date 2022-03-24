import os
from typing import Any

import pandas as pd

from actions.constants import ACTIONS_PATH


class Tool:
    def __init__(self):
        # 文件路径
        self.world_index_path = os.path.join(ACTIONS_PATH, "data/world_index.txt")
        self.stock_path = os.path.join(ACTIONS_PATH, "data/stock.csv")

    def convert_market_id(self, market_name: str) -> Any:
        """convert market name to market id

        Args:
            market_name (str): market name

        Returns:
            str: market id
        """
        df = pd.read_table(self.world_index_path, sep=" ", header=None)
        df.columns = ["id", "name"]
        df_tmp = df[df.name.str.contains(market_name)]

        if df_tmp.empty:
            df_tmp2 = df[df.name.apply(self.is_contain_by, args=(market_name,))]
            if df_tmp2.empty:
                return None
            return str(df_tmp2.id.values[0])
        else:
            return str(df_tmp.id.values[0])

    def is_contain_by(self, name, by_name):
        """ be contained """
        if by_name.__contains__(name):
            return True
        return False

    def get_world_index_name(self):
        """ get world index name content """
        df = pd.read_table(self.world_index_path, sep=" ", header=None)
        df.columns = ["id", "name"]
        names = df.name.values
        return "\n".join(names)

    def convert_company_id(self, company_name: str) -> Any:
        """convert company name to company id

        Args:
            company_name (str): market name

        Returns:
            str: company id
        """
        df = pd.read_csv(self.stock_path)
        df_tmp = df[df.name.str.contains(company_name)]

        if df_tmp.empty:
            df_tmp2 = df[df.name.apply(self.is_contain_by, args=(company_name,))]
            if df_tmp2.empty:
                return None
            return str(df_tmp2.sid.values[0])
        else:
            return str(df_tmp.sid.values[0])

    def get_company_name(self):
        """ get company name content """
        df = pd.read_csv(self.stock_path)
        sh_ser = df[df.sid.str.contains("sh")].iloc[:1000, 1]
        sz_ser = df[df.sid.str.contains("sz")].iloc[:500, 1]
        hk_ser = df[df.sid.str.contains("hk")].iloc[:500, 1]
        us_ser = df[~df.sid.str.contains("hk|sh|sz")].iloc[:500, 1]

        ser = sh_ser.append([sz_ser, hk_ser, us_ser])
        return "\n".join(ser.values)


if __name__ == "__main__":
    tool = Tool()
    id = tool.convert_market_id("上证指数")
    print(type(id), id)
    name = tool.get_world_index_name()
    print(name)

    id2 = tool.convert_company_id("互联医疗")
    print(type(id2), id2)
    name2 = tool.get_company_name()
    print(name2)
