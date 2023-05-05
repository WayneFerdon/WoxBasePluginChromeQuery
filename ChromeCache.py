# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 16:08:29
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-23 17:02:38
# FilePath: \FlowLauncher\Plugins\WoxPluginBase_ChromeQuery\ChromeCache.py
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

class Platform(Enum):
    Chrome = 0
    Edge = 1

    __all__ = None

    @classmethod
    @property
    def all(cls):
        if cls.__all__:
            return cls.__all__
        
        cls.__all__ =  {
            Platform.Chrome: {
                cls.dataPath: '/Google/Chrome',
                cls.icon: './Images/chromeIcon.png',
                cls.bookmarkRoot: 'chrome://bookmarks/',
            },
            Platform.Edge: {
                cls.dataPath: '/Microsoft/Edge',
                cls.icon: './Images/edgeIcon.png',
                cls.bookmarkRoot: 'edge://favorites/',
            }
        }
        return cls.__all__

    @property
    def name(self):
        return f'[@{str(super().name)}]'

    @property
    def dataPath(self):
        localAppData = os.getenv('LocalAppData')
        return  f'{localAppData}{Platform.all[self][Platform.dataPath]}/User Data/Default/'

    @property
    def icon(self):
        return Platform.all[self][Platform.icon]
    
    @property
    def bookmarkRoot(self) -> str:
        return Platform.all[self][Platform.bookmarkRoot]

    @property
    def rootBookmarkID(self) -> int:
        if Platform.rootBookmarkID not in Platform.all[self].keys():
            return 1
        return Platform.all[self][Platform.rootBookmarkID]

    @property
    def url(self) -> str:
        given = None
        if Platform.url in Platform.all[self].keys():
            given = Platform.all[self][Platform.url]
        return self.bookmarkRoot + '?id={}' if given is None else given
    
    def getInternalUrl(self, id:int):
        if id <= self.rootBookmarkID:
            return self.bookmarkRoot
        return self.url.format(id)

class ChromeData():
    class Type(Enum):
        url = 0, 
        folder = 1,

    def __init__(self, platform:Platform, title:str, url:str, type:Type=Type.url):
        self.platform = platform
        self.title = title
        self.url = url
        self.type = type
        match type:
            case ChromeData.Type.folder:
                self.icon = ChromeData.FOLDER_ICON
            case ChromeData.Type.url:
                self.icon = ChromeCache.getIcon(self)

    @staticmethod
    def __getAbsPath__(iconPath):
        return os.path.join(os.path.abspath('./'), iconPath)

    FOLDER_ICON = __getAbsPath__('./Images/folderIcon.png')

    @staticmethod
    def __getIconPath__(platform:Platform, iconID:int):
        if not os.path.exists('./Images/Temp'):
            os.makedirs('./Images/Temp')
        return './Images/Temp/icon{}{}.png'.format(platform.name, iconID)

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
    def __init__(self, platform:Platform):
        self.platform = platform
        self.__loadIcons__()

    def __loadIcons__(self):
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
    
        self.iconDict = dict[str, int]()
        for url, iconID in urls:
            self.iconDict[url] = iconID

        for iconID in bitmapInfos.keys():
            imageData = bitmapInfos[iconID].image
            try:
                with open(ChromeData.__getIconPath__(self.platform, iconID), 'wb') as f:
                    f.write(imageData)
            except PermissionError:
                pass

    def __getReadOnlyData__(self, dataName):
        sourceData = self.platform.dataPath + dataName
        readOnlyData = self.platform.dataPath + dataName + 'ToRead'
        shutil.copyfile(sourceData, readOnlyData)
        return readOnlyData

    def __loadBookmarks__(self) -> str:
        with open(self.platform.dataPath + 'Bookmarks', 'r', encoding='UTF-8') as f:
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
    __caches__ = None

    @staticmethod
    def __getCaches__() -> dict[Platform, Cache]:
        if not ChromeCache.__caches__:
            ChromeCache.__caches__ = dict[Platform, Cache]()
            for platfrom in Platform.all:
                ChromeCache.__caches__[platfrom] = Cache(platfrom)
        return ChromeCache.__caches__
    
    @staticmethod
    def getIcon(data:ChromeData):
        url = data.url
        for platform in Platform.all:
            cache = ChromeCache.__getCaches__()[platform]
            for keyURL in cache.iconDict.keys():
                if url in keyURL:
                    return ChromeData.__getIconPath__(platform, cache.iconDict[keyURL])
        platform = data.platform
        return platform.icon

    @staticmethod
    def getHistories() -> list[History]:
        results = list[History]()
        for platform in Platform.all:
            cache = ChromeCache.__getCaches__()[platform]
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
                        url = ancestors + '/' + item['name']
                        bookmarks += getChildren(platform, item['children'], url, id)
                bookmarks.append(Bookmark(platform, title, url, ancestors, id, parentID, type))
            return bookmarks
        
        bookmarks = list[Bookmark]()
        for platform in Platform.all:
            cache = ChromeCache.__getCaches__()[platform]
            data = cache.__loadBookmarks__()
            for root in data['roots']:
                try:
                    childItems = data['roots'][root]['children']
                except Exception:
                    continue
                bookmarks.append(Bookmark(platform, root, root+ '/', platform.getInternalUrl(0), data['roots'][root]['id'], 0, Bookmark.Type.folder))
                bookmarks += getChildren(platform, childItems, root + '/', 0)
        return bookmarks
