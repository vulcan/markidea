#-*- coding:utf-8 -*-
import os
import logging
import config
"""
utitlity functions
"""
def get_file_path(path):
    return os.path.join(config.datadir, path)

def ext_name(fname):
    return fname.split('.')[-1]

def get_site_path(fullpath):
    """ get path relative to site root path """
    return fullpath.replace(config.datadir, config.baseurl).replace('\\','/')

def getLogger(config, module=None):
    """ util function to get logger """
    if module:
        logger = logging.getLogger(module)
    else:
        logger = logging.getLogger()
    handler = config.get('logger', 'handler')
    handler_arg = config.get('logger', 'handler_arg')
    format = config.get('logger', 'format', raw=True)
    level = config.get('logger', 'level')
    hdlr = None
    if handler:
        if handler_arg:
            hdlr = getattr(logging, handler)(handler_arg)
        else:
            hdlr = getattr(logging, handler)()
        if format:
            formatter = logging.Formatter(format)
            hdlr.setFormatter(formatter)
    if hdlr:
        logger.addHandler(hdlr)

    if level:
        try:
            logger.setLevel(getattr(logging, level))
        except AttributeError:
            pass

    return logger
#init default logger
logger = getLogger(config.config)

def session_val(key):
    """
    extract the session value with a specified key
    if not key defined, it will return None instead of raising Exception
    """
    if config.session is None:
        return None

    value = None
    try:
        value = config.session[key]
    except KeyError:
        pass
    return value

def current_user():
    if config.session is None:
        return None
    return "%s@your.com" % config.session.username
