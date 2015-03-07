#-*- coding:utf8 -*-
import os
import ConfigParser
import logging

config = ConfigParser.ConfigParser()
path = os.path.realpath(__file__)
rootdir = os.path.dirname(path)
conf = os.path.join(rootdir, 'config.ini')
config.read(conf)
data_dir = config.get('app', 'datadir') #get the data dir
datadir = os.path.join(rootdir, data_dir)
hgwebpath = config.get('app', 'hgwebpath')
devmode = (config.get('app', 'devmode').lower() == 'true')
cashost = config.get('app', 'cashost')
session_dir = config.get('app', 'session_dir')
user_list = [f for f in config.get('app','allowed_user').split(',') if not f == '']
baseurl = config.get('app', 'baseurl')
#
session = None
