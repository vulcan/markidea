#-*- coding:utf8 -*-
"""
handle mercurial repository related operations
"""
import codecs
import web
import hglib
from util import *

class showlog:
    """
    redirect or show the log information of the given file
    """
    def GET(self, path):
        #build log url based on the path
        client = connect_repo(path)
        rev = client.tip().rev
        repo_path = client.root()
        rel_dir = config.datadir.replace(repo_path, '').replace('\\', '/')
        if rel_dir == '/data':
            #in dev mode, the data repo shares with source repo
            path = "%s/%s" % (config.data_dir, path)
        logpage = get_hglog_url(rev, path)
        raise web.seeother(logpage)

def get_hglog_url(rev, path):
    logpage = "%s/log/%s/%s" % (config.hgwebpath, rev, path)
    return logpage


class remove:
    """
    delete the given page
    """
    def GET(self, path):
        file_path = get_file_path(path)
        client = connect_repo(path)
        client.remove(file_path)
        #TODO require message
        client.commit(message="delete file %s" % path, user="%s" % current_user()) #TODO get current user id
        client.close()
        raise web.seeother(config.baseurl+'/')

class save:
    """
    save the posted data to the repository
    """
    def POST(self, path):
        """
        write to file, overwrite
        commit the change
        """
        i = web.input()
        src = i.source
        #in case the out commit, update the repo first
        client = connect_repo(path)
        client.update()
        #write to file
        file_path = get_file_path(path)
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name) #create dirs in the path
            logger.info("created new directory %s." % dir_name)
        fsock = codecs.open(file_path, mode='w', encoding='utf-8')
        fsock.write(src)
        fsock.close()
        logger.info("write to file %s" % file_path)
        #commit to repo
        status = client.status(include=file_path)
        #commit only when actual changes happened
        if status is not None and len(status) > 0:
            if status[0][0] == '?':
                #add to the repo
                client.add(file_path)
            #commit TODO with the uploaded pictures but may with the risk to commit other people's modification
            msg = i.message.encode('utf8') #encode the message for mercurial
            client.commit(message=msg, addremove=True, user="%s" % current_user()) #include
        client.close()
        raise web.seeother("%s/%s" % (config.baseurl, path))

def connect_repo(path):
    """
    find and connect to the hg repo path
    TODO maintain multi repo connections
    """
    file_path = get_file_path(path)
    dirname = os.path.dirname(file_path)
    #find until reach the root dir
    while not dirname == '/':
        hgdir = os.path.join(dirname, '.hg')
        if os.path.exists(hgdir):
            logger.info("connected to data dir %s " % dirname)
            return hglib.open(dirname, 'utf-8')
        dirname = os.path.dirname(dirname)

    default_client = hglib.open(config.datadir, 'utf-8')
    return default_client

