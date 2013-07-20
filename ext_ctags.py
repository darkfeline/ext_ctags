# -*- coding: utf-8 -*-
import os


def doctree_resolved(app, doctree, docname):

    filename = os.path.join(app.confdir, app.config.ctags_filename)

    # load existent ctag
    ctags = load_ctag(filename)

    # purge old ctag entries
    #TODO: remove entries by using 'docname'

    # build domain related references
    domains_db = get_current_doc_references(app, docname)

    # process reference targets
    ctags = update_ctags(app, doctree, docname, ctags, domains_db)

    # write to tags file
    save_ctags(filename, ctags)

    #app.info('updating ctag file: {filename}.'.format(filename=filename))


def load_ctag(filename):
    ctags = {}
    if os.path.exists(filename):
        for line in open(filename, 'rt'):
            try:
                idx, src, line = line.strip().split('\t')
                ctags[idx] = (src, line)
            except ValueError:
                pass  #skip broken line

    return ctags


def get_current_doc_references(app, current_docname):
    refs = {}
    for domainname, domain in app.env.domains.items():
        for name, dispname, type, docname, anch, prio in domain.get_objects():
            if docname == current_docname:
                # overwrite if name already exist by another domain...
                refs[name] = [domainname, type, dispname, anch, prio]
    return refs


def update_ctags(app, doctree, docname, ctags, domains_db):
    def node_filter(node):
        try:
            return bool(node['ids'])
        except:
            return False

    for node in doctree.traverse(node_filter):
        for id in node['ids']:
            if id in domains_db:
                try:
                    ctags[id] = node_to_db_entry(
                        node, app.srcdir, app.config.ctags_relpath)
                except NodeSourceError:
                    pass

    # document xref
    idx = '/' + docname
    try:
        ctags[idx] = node_to_db_entry(
            doctree.next_node(), app.srcdir, app.config.ctags_relpath)
    except NodeSourceError:
        pass

    return ctags


def node_to_db_entry(node, basedir, use_relpath=True):
    path = node.source
    if path is None:
        raise NodeSourceError
    if use_relpath:
        path = os.path.relpath(path, basedir)

    return (path, str(node.line))


def save_ctags(filename, ctags):
    with open(filename, 'wt') as f:
        for idx in sorted(ctags.keys()):
            f.write(idx + '\t')
            f.write('\t'.join(ctags[idx]))
            f.write('\n')


def setup(app):
    app.add_config_value('ctags_filename', 'tags', False)
    app.add_config_value('ctags_relpath', True, False)
    app.connect('doctree-resolved', doctree_resolved)


class NodeSourceError(Exception): pass
