#!/bin/env python

import os
import zipfile
import urllib.request
import shutil

pluginsKey = "GRAFANA_PLUGINS"
pluginsVolume = "/opt/plugins"


class ZipFileWithPermissions(zipfile.ZipFile):
    """ Custom ZipFile class handling file permissions. """

    def _extract_member(self, member, targetpath, pwd):
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)

        targetpath = super()._extract_member(member, targetpath, pwd)

        attr = member.external_attr >> 16
        if attr != 0:
            os.chmod(targetpath, attr)
        return targetpath


def getPlugins():
    result = list()
    if pluginsKey in os.environ and not (not os.environ[pluginsKey]):
        plugins = os.environ[pluginsKey].split(",")
        for plugin in plugins:
            parts = plugin.split(":")
            if len(parts) == 2:
                result.append((parts[0], parts[1]))
            else:
                print("Invalid syntax (version missing?): " + plugin)
    return result


def downloadPlugin(plugin):
    print(plugin)
    plugin_Key = plugin[0]
    url = "https://grafana.com/api/plugins/%s/versions/%s/download" % plugin
    if 'aliyun' in plugin_Key:
        print('下载阿里云的插件')
        url = "https://github.com/aliyun/%s/archive/master.zip" % plugin_Key
        print(url)
    file_name = "/tmp/%s_%s.zip" % plugin
    with urllib.request.urlopen(url) as response, open(file_name, "wb") as out_file:
        shutil.copyfileobj(response, out_file)
    return file_name


def extractPlugin(file_name):
    zip = ZipFileWithPermissions(file_name)
    zip.extractall(pluginsVolume)
    zip.close()


def installPlugin(plugin):
    try:
        file_name = downloadPlugin(plugin)
    except:
        print("Error downloading %s:%s" % plugin)
    else:
        extractPlugin(file_name)


def main():
    for plugin in getPlugins():
        installPlugin(plugin)


# 测试案例
# grafana的官方kubernetes镜像插件和阿里云的云监控插件
# GRAFANA_PLUGINS = 'grafana-kubernetes-app:1.0.1,aliyun-cms-grafana:latest'
# os.environ.setdefault('GRAFANA_PLUGINS', GRAFANA_PLUGINS)
main()
