#!/usr/bin/python
#-*- coding:utf8 -*-
import web
import markdown
import os
import ConfigParser
import codecs
import config
import hglib
from util import *
import repo
import cas
import upload
from mdext import AutoIndexExtension, HgLogExtension

class reindex:
    def GET(self):
        raise web.seeother(config.baseurl+'/')

class index:
    def GET(self, path):
        _page = path
        if path == '' or path.endswith('/'):
            _page = path+'index.md'
        if ext_name(_page) in ['md','txt']: #only render md or txt file
            html = render(_page)
            if html is None:
                if _page.endswith('index.md'):
                    #auto generated index page
                    return autoindex(_page)
                return web.notfound()
            return html
        else:
            if not path == 'favicon.ico':
                file_path = get_file_path(path)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    return open(file_path, 'rb') #serve the direct file
                else:
                    return web.notfound()

class printpage:
    def GET(self, path):
        """
        display a simple page for print
        """
        return render(path, True)

class input:
    def GET(self, path):
        tinput = web.template.frender('template_input.html', globals={'session': config.session, 'config':config})
        files = upload.listfile(path)
        return tinput(path, '# %s' % "Title", files)

class edit:
    """
    load the given page for editing
    TODO verify if current user has permission to do so
    """
    def GET(self, path):
        tinput = web.template.frender('template_input.html', globals={'session': config.session, 'config':config})
        filepath = get_file_path(path)
        #try to read the file path
        files = upload.listfile(path)
        try:
            input_file = codecs.open(filepath, mode='r', encoding='utf-8')
            text = input_file.read()
            input_file.close()
            return tinput(path, text, files)
        except IOError:
            return tinput(path, '# %s' % "Title", files)

class preview:
    """
    preview the posted source
    TODO: draft saving
    """
    def POST(self, path):
        i = web.input()
        if i.has_key('src'):
            return _render(i.src, path)
        else:
            return ""

class query:
    """
    search by keyword
    """
    def GET(self):
        from search import TextSearchEngine
        engine = TextSearchEngine(config.datadir)
        i = web.input()
        result = engine.search(i.q)
        tmpl = web.template.render('templates/', base="layout", globals={'session': config.session, 'config':config})
        return tmpl.search(result)


def render(path, simple=False):
    try:
        filepath = get_file_path(path)
        input_file = codecs.open(filepath, mode='r', encoding='utf-8')
        text = input_file.read()
        i = web.input()
        if simple:
            html = web.template.frender('template_simple.html', globals={'session': config.session, 'config':config})
        else:
            html = web.template.frender('template.html', globals={'session': config.session, 'config':config})
        #show the rendered or raw text
        if i.has_key('t') and i.t == 'raw':
            return text
        else:
            body = _render(text, path)
            return html(path, body)
    except IOError:
        return None

def autoindex(path):
    html = web.template.frender('template.html', globals={'session': config.session, 'config':config})
    src = u"#%s\n[Index]" % "Auto Index"
    body = _render(src, path)
    return html(path, body)

def _render(text, path):
    """
    use markdown to render the given source text
    """
    filepath = get_file_path(path)
    dirpath = os.path.dirname(filepath)
    extensions=['markdown.extensions.tables',\
            AutoIndexExtension(dirpath),\
            HgLogExtension(path)] #the custom extension
    body = markdown.markdown(text, extensions=extensions )
    return body

def setup():
    import sesstore
    web.config.debug = False
    urls = (
            config.baseurl+'','reindex',
            config.baseurl+'/logout', cas.logout,
            config.baseurl+'/search', 'query',
            config.baseurl+'/(.*)/preview', 'preview',
            config.baseurl+'/(.*)/new', 'input',
            config.baseurl+'/(.*)/edit', 'edit',
            config.baseurl+'/(.*)/print', 'printpage',
            config.baseurl+'/(.*)/log', repo.showlog,
            config.baseurl+'/(.*)/save', repo.save,
            config.baseurl+'/(.*)/delete', repo.remove,
            config.baseurl+'/(.*)/upload', upload.upload,
            config.baseurl+'/(.*)/delfile', upload.delfile,
            config.baseurl+'/(.*)', 'index'
            )

    app = web.application(urls, globals())
    session = web.session.Session(app, web.session.DiskStore(config.session_dir))
    #session = web.session.Session(app, sesstore.BSDStore(config.session_dir))
    #session = web.session.Session(app, sesstore.MemStore())
    config.session = session
    app.add_processor(cas.interceptor)
    return app

def main():
    """ the main entry"""
    #work the data dir and try to locate the index page
    app = setup()
    app.run()

if __name__ == '__main__':
    main()
