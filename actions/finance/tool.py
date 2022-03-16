import os
from typing import Any

import pandas as pd

from actions.constants import ACTIONS_PATH


class Tool:
    def __init__(self):
        # 文件路径
        self.world_index_path = os.path.join(ACTIONS_PATH, "data/world_index.txt")

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
        if by_name.__contains__(name):
            return True
        return False

    def get_world_index_name(self):
        """ get world index id and name content"""
        with open(self.world_index_path, encoding="utf-8") as f:
            content = f.readlines()

        return "".join(content)


if __name__ == "__main__":
    tool = Tool()
    id = tool.convert_market_id("上证指数")
    print(type(id), id)
    name = tool.get_world_index_name()
    print(name)

