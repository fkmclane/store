import logging
import time

import cron

from store import config, storage


log = logging.getLogger('store')

scheduler = None


def prune():
    date = time.time()

    log.info('Pruning...')

    todo = []

    for namespace in storage.namespaces():
        for entry in storage.values(namespace):
            if entry.expire <= date:
                # queue alias for removal
                todo.append((namespace, entry.alias))

    for (namespace, alias) in todo:
        # remove everything ignoring errors
        try:
            storage.remove(namespace, alias)
        except:
            pass

    log.info('Done. Removed ' + str(len(todo)) + ' items.')


def start():
    global scheduler

    scheduler = cron.Scheduler()
    scheduler.add(cron.Job(prune, minute=config.minute))
    scheduler.start()


def stop():
    global scheduler

    scheduler.stop()
    scheduler = None
