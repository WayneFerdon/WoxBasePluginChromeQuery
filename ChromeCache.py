# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 16:08:29
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-03 01:18:30
# FilePath: \Wox.Base.Plugin.ChromeHistoryc:\Users\WayneFerdon\AppData\Local\FlowLauncher\app-1.14.0\Plugins\WoxPluginBase_ChromeQuery\ChromeCache.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
import os
import json
import sqlite3
import shutil
from enum import Enum

class Platform():
    class Type(Enum):
        Chrome = 0, 
        Edge = 1
    class BookmarkSetting():
        def __init__(self, rootURL:str, url:str = None, rootID:int = 1) -> None:
            self.rootURL = rootURL
            self.url = rootURL + '?id={}/' if url is None else url
            self.rootID = rootID
        
        def getInternalUrl(self, id:int):
            if id <= self.rootID:
                return self.rootURL
            return self.url.format(id)
    
    def __init__(self, type:Type, bookmarkSetting:BookmarkSetting) -> None:
        self.type = type
        self.bookmarkSetting = bookmarkSetting
    
    def getInternalUrl(self, id:int):
        return self.bookmarkSetting.getInternalUrl(id)

    __Defined__ = None

    @property
    def name(self):
        return f'[@{str(self.type.name)}]'

    @staticmethod
    def GetDefined():
        if Platform.__Defined__ is None:
            Platform.__Defined__ = [
            Platform(
                Platform.Type.Chrome,
                Platform.BookmarkSetting('chrome://bookmarks/')
            ),
            Platform(
                Platform.Type.Edge,
                Platform.BookmarkSetting('edge://favorites/')
            )
        ]
        return Platform.__Defined__

class ChromeData():
    class Type(Enum):
        url = 0, 
        folder = 1, 

    def __init__(self,platform:Platform, title:str, url:str, type:Type=Type.url):
        self.platform = platform
        self.title = title
        self.url = url
        self.type = type
        match type:
            case ChromeData.Type.folder:
                self.icon = ChromeData.FOLDER_ICON
            case ChromeData.Type.url:
                iconID = ChromeCache.getIconID(self.url)
                if iconID != 0:
                    iconPath = ChromeData.__getIconPath__(iconID)
                else:
                    iconPath = ChromeCache.getCaches()[platform].PLATFORM_ICON
                self.icon = ChromeData.__getAbsPath__(iconPath)

    @staticmethod
    def __getAbsPath__(iconPath):
        return os.path.join(os.path.abspath('./'), iconPath)

    FOLDER_ICON = __getAbsPath__('./Images/folderIcon.png')

    @staticmethod
    def __getIconPath__(iconID):
        if not os.path.exists('./Images/Temp'):
            os.makedirs('./Images/Temp')
        return './Images/Temp/icon{}.png'.format(iconID)

class Bookmark(ChromeData):
    def __init__(self, platform:Platform, title:str, url:str, path:str, id:int, directoryID:int, type:ChromeData.Type):
        ChromeData.__init__(self,platform, title, url, type)
        self.path = path
        self.id = id
        self.directory = platform.getInternalUrl(directoryID)

class History(ChromeData):
    def __init__(self, platform:Platform, title:str, url:str, lastVisitTime:int):
        ChromeData.__init__(self, platform, title, url)
        self.lastVisitTime = lastVisitTime

class BitMap():
    def __init__(self, image, width, height) -> None:
        self.image = image
        self.width = width
        self.height = height

class Cache:
    def __init__(self, platform):
        self.__setPlatform__(platform)
        self.__loadcons__()
    
    def __setPlatform__(self, platform:Platform):
        localAppData = os.environ['localAppData'.upper()]
        match platform.type:
            case Platform.Type.Chrome:
                self.PLATFORM_ICON = './Images/chromeIcon.png'
                self.__DATA_PATH__ = '/Google/Chrome/'
            case Platform.Type.Edge:
                self.PLATFORM_ICON = './Images/edgeIcon.png'
                self.__DATA_PATH__ = '/Microsoft/Edge/'
        self.__DATA_PATH__ = localAppData + self.__DATA_PATH__ + 'User Data/Default/'

    def __loadcons__(self):
        cursor = sqlite3.connect(self.__getReadOnlyData__('Favicons')).cursor()
        bitmapCursorResults = cursor.execute(
            'SELECT icon_id, image_data, width, height '
            'FROM favicon_bitmaps'
        ).fetchall()
        urlCursorResults = cursor.execute(
            'SELECT page_url, icon_id '
            'FROM icon_mapping'
        ).fetchall()
        cursor.close()
        bitmaps, urls = bitmapCursorResults, urlCursorResults
        bitmapInfos = dict[int, BitMap]()

        for iconID, image, width, height in bitmaps:
            if iconID in bitmapInfos.keys() \
            and (width < bitmapInfos[iconID].width
            or height < bitmapInfos[iconID].height):
                continue
            bitmapInfos[iconID] = BitMap(image,width,height)
    
        self.__ICON_DICT__ = dict[str, int]()
        for url, iconID in urls:
            self.__ICON_DICT__[url] = iconID

        for iconID in bitmapInfos.keys():
            imageData = bitmapInfos[iconID].image
            try:
                with open(ChromeData.__getIconPath__(iconID), 'wb') as f:
                    f.write(imageData)
            except PermissionError:
                pass

    def __getReadOnlyData__(self, dataName):
        sourceData = self.__DATA_PATH__ + dataName
        readOnlyData = self.__DATA_PATH__ + dataName + 'ToRead'
        shutil.copyfile(sourceData, readOnlyData)
        return readOnlyData

    def __loadBookmarks__(self) -> str:
        with open(self.__DATA_PATH__ + 'Bookmarks', 'r', encoding='UTF-8') as f:
            bookmarkData = json.load(f)
        return bookmarkData

    def __loadHistories__(self) -> list:
        cursor = sqlite3.connect(self.__getReadOnlyData__('History')).cursor()
        histories = cursor.execute(
            'SELECT urls.url, urls.title, urls.last_visit_time '
            'FROM urls, visits '
            'WHERE urls.id = visits.url'
        ).fetchall()
        cursor.close()
        return histories

class ChromeCache:
    __Caches__ = None

    @staticmethod
    def getCaches() -> dict[Platform, Cache]:
        if ChromeCache.__Caches__ is None:
            ChromeCache.__Caches__ = dict[Platform, Cache]()
            for platfrom in Platform.GetDefined():
                ChromeCache.__Caches__[platfrom] = Cache(platfrom)
        return ChromeCache.__Caches__
    
    @staticmethod
    def getIconID(url):
        for platform in Platform.GetDefined():
            cache = ChromeCache.getCaches()[platform]
        for keyURL in cache.__ICON_DICT__.keys():
            if url in keyURL:
                return cache.__ICON_DICT__[keyURL]
        return 0

    @staticmethod
    def getHistories() -> list[History]:
        results = list[History]()
        for platform in Platform.GetDefined():
            cache = ChromeCache.getCaches()[platform]
            historyInfos = cache.__loadHistories__()
            histories = dict[str, History]()
            for url, title, lastVisitTime in historyInfos:
                key = platform.name + url + title
                if key not in histories.keys():
                    histories[key] = History(platform, title, url, lastVisitTime)
                    continue
                if histories[key].lastVisitTime >= lastVisitTime:
                    continue
                histories[key].lastVisitTime = lastVisitTime
            histories = list(histories.values())
            histories.sort(key=lambda history:history.lastVisitTime, reverse=True)
            results+=histories
        return results

    @staticmethod
    def getBookmarks() -> list[Bookmark]:
        def getChildren(platform:Platform, children:dict, ancestors:str, parentID:int) -> list[Bookmark]:
            bookmarks = list()
            for item in children:
                title, id = item['name'], int(item['id'])
                type = Bookmark.Type[item['type']]
                match type:
                    case Bookmark.Type.url:
                        url = item['url']
                    case Bookmark.Type.folder:
                        url = ancestors + item['name'] + '/'
                        bookmarks += getChildren(platform, item['children'], url, id)
                bookmarks.append(Bookmark(platform, title, url, ancestors, id, parentID, type))
            return bookmarks
        
        bookmarks = list[Bookmark]()
        for platform in Platform.GetDefined():
            cache = ChromeCache.getCaches()[platform]
            data = cache.__loadBookmarks__()
            for root in data['roots']:
                try:
                    childItems = data['roots'][root]['children']
                except Exception:
                    continue
                bookmarks.append(Bookmark(platform, root, root+ '/', platform.getInternalUrl(0), data['roots'][root]['id'], 0, Bookmark.Type.folder))
                bookmarks += getChildren(platform, childItems, root + '/', 0)
        return bookmarks
