import json
import os
from typing import Any

import pandas as pd
from actions.api.nowapi import NowApi
from actions.constants import ACTIONS_PATH
from actions.utils.create_log import logger


class Stock:
    def __init__(self):
        # api定义
        self.api = NowApi()
        self.api_params = self.api.params
        self.api_params["app"] = "finance.stock_realtime"
