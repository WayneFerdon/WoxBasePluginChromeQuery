# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 17:07:35
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-05 07:41:43
# FilePath: \Plugins\WoxPluginBase_ChromeQuery\ChromeQuery.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from WoxBasePluginQuery import *

import webbrowser
from ChromeCache import *

class ChromeQuery(QueryPlugin):
    PlatformCaches = dict[Platform, Cache]()

    def __getDatas__(self) -> list[ChromeData]:
        return None

    def __getResult__(self, regex:RegexList, data:ChromeData):
        return None

    def __extraContextMenu__(self, data:ChromeData):
        return []

    def query(self, query:str):
        results = list()
        regex = RegexList(query)
        self.__datas__ = self.__getDatas__()
        for data in self.__datas__:
            result = self.__getResult__(regex, data)
            if result is None:
                continue
            results.append(result)
        return results

    def context_menu(self, index:int):
        self.query('')
        data = self.__datas__[index]

        results = [
            self.getCopyDataResult('URL', data.url, data.icon), 
            self.getCopyDataResult('Title', data.title, data.icon)
        ]
        results += self.__extraContextMenu__(data)
        return results

    def openUrl(self, url:str):
        webbrowser.open(url)

if __name__ == "__main__":
    InstallationCheck()