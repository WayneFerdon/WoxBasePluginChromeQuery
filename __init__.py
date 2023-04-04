# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2023-04-02 22:18:13
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-03 00:55:29
# FilePath: \FlowLauncherPluginChromeQueryBase\__init__.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import os, sys
pluginDir = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(pluginDir)
sys.path.append(pluginDir)
sys.path.append(parent)

from ChromeQuery import *