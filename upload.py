#-*- coding:utf-8 -*-
"""
upload files
"""
import os
import json
import web
from util import *
import config

class upload:
    def POST(self, path):
        """ upload to the current dir """
        file_path = get_file_path(path)
        dir_path = os.path.dirname(file_path)
        i = web.input(myfile={})
        result = []
        if 'myfile' in i:
            filepath = i.myfile.filename.replace('\\', '/')
            filename = filepath.split('/')[-1]
            fullpath = os.path.join(dir_path, filename)
            fout = open(fullpath, 'wb')
            fout.write(i.myfile.file.read())
            fout.close()
            result.append({'name': get_site_path(fullpath), 'length':len(i.myfile.value)})
            web.header('content-type', 'text/json')
            return json.dumps({'files':result})

class delfile:
    """
    delete the attachment but donot commit at this stage
    """
    def GET(self, path):
        """ delete file from current dir """
        if ext_name(path) in ['md', 'txt']:
            return json.dumps({'result':False, 'reason':'can only delete the attachment!'})
        file_path = get_file_path(path)
        try:
            os.remove(file_path)
            return json.dumps({'result':True})
        except OSError,ex:
            return json.dumps({'result':False, 'reason': str(ex)})

def listfile(path):
    """ list file on the given path """
    file_path = get_file_path(path)
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        return [] #dir not exits
    files = os.listdir(dir_name)
    def relpath(fname):
        fullpath = os.path.join(dir_name, fname)
        left = fullpath.replace(config.datadir, config.baseurl)
        return left.replace('\\', '/')
    #list all file but txt and md files
    attachments = [relpath(f) for f in files if ext_name(f) in ['jpg','gif','png','zip','rar','7z']]
    return attachments
