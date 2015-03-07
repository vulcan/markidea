#-*- coding:utf-8 -*-
"""
integrate with CAS
"""
import web
import urllib
from xml.dom import minidom
import config
import util
"""
intercept the request and retrieve the request path
"""
def casauth():
    """
    do the CAS authentication and return a NETID if authenticated succsesfull
    """
    i = web.input()
    url = web.ctx.home + web.ctx.path
    if not hasattr(i, 'ticket') or i.ticket == '':
        redir = config.cashost + 'login?service=' + url
        #print redir
        raise web.seeother(redir)
    #validate the ticket with CASHOST
    validateurl = config.cashost + 'serviceValidate?ticket=' + i.ticket
    validateurl += ("&service=" + url)
    sock = urllib.urlopen(validateurl)
    resp = sock.read() #the xml return
    sock.close()
    #print resp
    xmldoc = minidom.parseString(resp)
    ele = xmldoc.getElementsByTagName('cas:user')
    if ele and len(ele) > 0:
        strEle = ele[0].firstChild
        if strEle.nodeType == strEle.TEXT_NODE:
            return strEle.data
        else:
            return None
    else:
        return None

def interceptor(handler):
    path = web.ctx.path
    ignore_path = ('/error', '/login', '/logout', '/preview')
    if path.startswith('/static/') or path[path.rfind('/'):] in ignore_path:
        return handler() #handle directly
    #do cas validate
    from util import session_val

    netid = None
    if not session_val('username'):
        if config.devmode: #bypass authentication when in devmode
            netid = 'user'
        else:
            netid = casauth()
        if config.user_list: #if white list actived
            if netid not in config.user_list:
                raise web.forbidden()
        #authoriztion by the netId
        config.session.username = netid #attach netid to the session
    else:
        netid = session_val('username')

    return handler()

class logout:
    def GET(self):
        CASHOST = config.cashost
        #clean the self session
        config.session.kill()
        #go to the CAS for loging out
        raise web.seeother(CASHOST + 'logout')
