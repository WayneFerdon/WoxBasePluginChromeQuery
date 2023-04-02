# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 17:07:35
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-03 03:39:49
# FilePath: \WoxPluginBase_ChromeQuery\ChromeQuery.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from WoxPluginBase_Query import *

import webbrowser
from ChromeCache import *

class ChromeQuery(Query):
    PlatformCaches = dict[Platform, Cache]()

    def _getDatas_(self) -> list[ChromeData]:
        return None

    def _getResult_(self, regex:RegexList, data:ChromeData):
        return None

    def _extraContextMenu_(self, data:ChromeData, iconPath:str):
        return []

    def query(self, query:str):
        results = list()
        regex = RegexList(query)
        self._datas_ = self._getDatas_()
        for data in self._datas_:
            result = self._getResult_(regex, data)
            if result is None:
                continue
            results.append(result)
        return results

    def context_menu(self, index:int):
        self.query('')
        data = self._datas_[index]

        results = [
            self.getCopyDataResult('URL', data.url, data.icon), 
            self.getCopyDataResult('Title', data.title, data.icon)
        ]
        results += self._extraContextMenu_(data)
        return results

    @classmethod
    def _openUrl_(cls, url:str):
        webbrowser.open(url)

    class InstallationCheck(Query.InstallationCheck):
        def PluginName(self) -> str:
            return 'WoxPluginBase_ChromeQuery'

if __name__ == "__main__":
    ChromeQuery.InstallationCheck()