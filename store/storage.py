import os
import random
import string

import db

from store import config, log


trunk = config.dir
path = trunk + 'upload'
lib = trunk + 'db'

max_tries = 10

ns_db = None

namespace_dbs = {}


def nsfile(namespace):
    if namespace == '/':
        return trunk + 'root.db'
    else:
        return lib + namespace + '.db'


def open(namespace):
    return db.Database(nsfile(namespace), ['alias', 'filename', 'type', 'size', 'date', 'expire'])


def namespaces():
    return iter(namespace_dbs)


def values(namespace):
    return iter(namespace_dbs[namespace])


def create(namespace, alias=None):
    if namespace not in namespace_dbs:
        ns_db.add(namespace)
        namespace_dbs[namespace] = open(namespace)

    rand = lambda: ''.join(random.choice(string.ascii_lowercase) for _ in range(config.random))

    if alias is None:
        alias = rand()
        count = 1
        while alias in namespace_dbs[namespace]:
            alias = rand()
            count += 1

            if count > max_tries:
                raise RuntimeError('max tries for random alias generation exceeded')

    return namespace_dbs[namespace].add(alias, '', '', 0, 0, 0)


def retrieve(namespace, alias):
    return namespace_dbs[namespace][alias]


def remove(namespace, alias):
    if namespace == '/':
        storepath = path + namespace
    else:
        storepath = path + namespace + '/'

    try:
        os.remove(storepath + alias)
    except:
        log.storelog.exception()

    del namespace_dbs[namespace][alias]

    if len(namespace_dbs[namespace]) == 0:
        try:
            os.removedirs(storepath)
        except:
            log.storelog.exception()

        del namespace_dbs[namespace]
        del ns_db[namespace]

        dbfile = nsfile(namespace)

        os.remove(dbfile)

        try:
            os.removedirs(os.path.dirname(dbfile))
        except:
            log.storelog.exception()


ns_db = db.Database(trunk + 'ns.db', ['namespace'])

for entry in ns_db:
    namespace_dbs[entry.namespace] = open(entry.namespace)
