#!/usr/bin/env python3.6

from urllib import request, parse
import json
from http.client import HTTPResponse
import glob
import sys
import gzip
import shutil
import os
import logging


def read_plugin_list_file_to_list(filename):
    file = open(filename, 'r')
    plugins_list = file.readlines()
    plugin_list = []
    for plugin in plugins_list:
        plugin_list.append(plugin.rstrip('\n'))
    return plugin_list


def write_plugin_set_to_file(plugin_set, filename):
    file = open(filename, 'w')
    count = len(plugin_set)
    i = 0
    for ext in plugin_set:
        file.write(ext)
        i += 1
        if i < count:
            file.write('\n')
    pass


def exist_plugin_files_to_plugin_list():
    plugin_list = []
    exist_file_list = []
    for plugin_ext in ('*.zip', '*.jar'):
        for filename in glob.glob(plugin_ext):
            filename_strip = filename.rstrip('.zip').rstrip('.jar')
            filename_split = filename_strip.split('_')
            plugin_list.append(filename_split[0] + '_' + filename_split[1])
            exist_file_list.append(filename_strip)
    return plugin_list, exist_file_list


def criteria_set_to_list(criteria_set):
    criteria_list = []
    for criteria in criteria_set:
        criteria_list.append(criteria)
    return criteria_list


def download_plugin(plugin_info_list, exist_plugin_list):
    download_url_template = 'http://plugins.jetbrains.com/files/'
    for info in plugin_info_list:
        filename = info.get('name') + '_' + info.get('version')
        url_file_path = info.get('url_file_path')
        if filename in exist_plugin_list:
            logging.info("%s exists, skip", filename)
            continue
        else:
            for exist_plugin in exist_plugin_list:
                if info.get('name') in exist_plugin:
                    os.remove(exist_plugin + '.' + url_file_path.split('.')[-1])
                    logging.info("Deleted old version of %s", exist_plugin)
                    break

        logging.info("Now downloading %s", filename)
        download_url = download_url_template + url_file_path
        request.urlretrieve(download_url, filename +
                            '.' + url_file_path.split('.')[-1])
    pass


def main():
    plugins_query_url = 'http://plugins.jetbrains.com/plugin/updates?'
    plugin_list_filename = sys.argv[1]
    plugin_list_from_list_file = read_plugin_list_file_to_list(
        plugin_list_filename)
    plugin_list_from_plugin_file, exist_plugin_list = exist_plugin_files_to_plugin_list()
    plugin_set = set()
    plugin_set.update(plugin_list_from_list_file)
    plugin_set.update(plugin_list_from_plugin_file)
    write_plugin_set_to_file(plugin_set, plugin_list_filename)

    plugin_info_list = []
    for plugin in plugin_set:
        req = request.Request(plugins_query_url +
                              parse.urlencode({'pluginId': plugin.split('_')[0]}))
        resp: HTTPResponse = request.urlopen(req)
        resp_body = json.loads(resp.read().decode('utf-8'))
        latest_update = resp_body.get('updates')[0]
        plugin_info_list.append({'name': plugin,
                                 'url_file_path': latest_update.get('file'),
                                 'version': latest_update.get('version')})

    download_plugin(plugin_info_list, exist_plugin_list)
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

