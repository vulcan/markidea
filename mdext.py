#-*- coding: utf-8 -*-
"""
markdown extension for auto index
"""
import os
import codecs
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree #keep compitible with markdown
from util import *

class MarkerProcessor(Treeprocessor):
    """
    base processor for marker replacement processor
    """
    def __init__(self, marker):
        self.marker = marker

    def itertext(self, elem):
        if elem.text:
            yield elem.text
        for e in elem:
            for s in self.itertext(e):
                yield s
            if e.tail:
                yield e.tail

    def iterparent(self, root):
        for parent in root.getiterator():
            for child in parent:
                yield parent, child

    def replace_marker(self, root, elem):
        """
        replace the marker with generated file list
        """
        for (p, c) in self.iterparent(root):
            text = ''.join(self.itertext(c)).strip()
            if not text:
                continue
            """
            extactly match [Index] marker
            """
            if c.text and c.text.strip() == self.marker and c.tag not in ['pre', 'code']:
                for i in range(len(p)):
                    if p[i] == c:
                        p[i] = elem
                        break

class AutoIndexProcessor(MarkerProcessor):
    def __init__(self, dirpath, marker='[Index]'):
        """
        the dir path
        dirpath: the absolute the auto index run
        """
        self.path = dirpath
        super(AutoIndexProcessor, self).__init__(marker)

    def procfile(self, fname):
        fullpath = os.path.join(self.path, fname)
        if not os.path.exists(fullpath):
            return None #file not exists

        fsock = codecs.open(fullpath, 'r', 'utf-8')
        line = fsock.readline() #read the first line
        #strip blank lines
        while line == '\n':
            line = fsock.readline()

        result = fname #fallback to file name
        if line.startswith('#'):
            result = line[1:].strip()
        else:
            #try next line check if line ==========
            nextline = fsock.readline()
            if nextline.startswith('====='):
                result = line
        fsock.close()
        return result

    def run(self, root):
        """
        list the directory and generate a list of links
        1. list .txt or .md files in current directory, and get the first title item
        2. if subdirectory exists try to find index.md or index.txt and get the title
        """
        if not os.path.exists(self.path):
            p = etree.Element('p')
            p.text = u"Directory doesn't exist"
            self.replace_marker(root, p)
            return

        items = os.listdir(self.path)
        result = []
        for item in items:
            if item.startswith('.'):
                continue #ignore hidden files
            if os.path.isdir(os.path.join(self.path, item)):
                #read try read index.md or index.txt
                idx = os.path.join(item, 'index.md')
                t = self.procfile(idx)
                if t:
                    result.append((idx, t))
                else:
                    idx = os.path.join(item, 'index.txt')
                    t = self.procfile(idx)
                    if t:
                        result.append((idx, t))
                    else:
                        result.append((item+'/', item)) #auto index
            elif item.endswith('.txt') or item.endswith('.md'):
                if item in ['index.md', 'index.txt']:
                    continue #ignore the default page to avoid include self in the index.md
                #read the content of the file
                t = self.procfile(item)
                if t:
                    result.append((item, t))
        #generate links to files and insert to the marked place
        div = etree.Element('div')
        div.attrib['class'] = 'autoindex'
        ul = etree.SubElement(div, 'ul')
        site_path = get_site_path(self.path)
        for i in result:
            li = etree.SubElement(ul, 'li')
            alink = etree.SubElement(li, 'a')
            alink.attrib['href'] = "%s/%s" % (site_path, i[0])
            alink.text = i[1]
        #replace the marker with generated dir index
        self.replace_marker(root, div)

class AutoIndexExtension(Extension):
    def __init__(self, dirpath, marker='[Index]'):
        """
        the absolute dir path of the file
        """
        self.dirpath = dirpath
        self.marker = marker

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        idxext = AutoIndexProcessor(self.dirpath, self.marker)
        md.treeprocessors.add("autoindex", idxext, "_end")

class HgLogProcessor(MarkerProcessor):
    def __init__(self, path, marker='[Log]', length=5, sitelog=False):
        """
        list dir or page dir
        sitelog: True if require all logs of data repo
        """
        self.path = path
        self.marker = marker
        self.length = length
        self.sitelog = sitelog

    def run(self, root):
        """
        list the mercurial log and list the link
        """
        from repo import connect_repo, get_hglog_url
        try:
            cli = connect_repo(self.path) #connect the path
            if self.sitelog:
                logs = cli.log() #TODO get the log about this file
            else:
                logs = cli.log(include=get_file_path(self.path))
            div = etree.Element('div')
            div.attrib['class'] = 'logdiv'
            ul = etree.SubElement(div, 'ul')
            maxlen = self.length < len(logs) and self.length or len(logs)
            for i in range(maxlen):
                log = logs[i]
                li = etree.SubElement(ul, 'li')
                alink = etree.SubElement(li, 'a')
                logdata = "%s/rev/%s" % (config.hgwebpath, log[0])
                alink.attrib['href'] = logdata #make link
                text = '%s, %s, %s' % (log[4:])
                alink.text = text.decode('utf8')
            cli.close()
            self.replace_marker(root, div)
        except:
            pass #do nothing because log retrieve may fail

class HgLogExtension(Extension):
    def __init__(self, path, length=5):
        self.path = path
        self.length = length

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        ext = HgLogProcessor(self.path, '[Log]', self.length)
        md.treeprocessors.add('hglog', ext, "_end")
        site_ext = HgLogProcessor(self.path, '[SiteLog]', self.length, True)
        md.treeprocessors.add('sitelog', site_ext, "_end")


if __name__ == '__main__':
    import config
    from pprint import pprint
    import markdown
    html = markdown.markdown('#test\n[Index]\n\n[Log]', extensions=[AutoIndexExtension(config.datadir), HgLogExtension('index.md')])
    print html.encode('utf8')
