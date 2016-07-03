import os
import time

from store.lib import web, file, json, page

from store import config, log, storage


alias = '([a-zA-Z0-9._-]+)'
namespace = '([a-zA-Z0-9._/-]*)/'

http = None

routes = {}
error_routes = {}


def create(entry, body, date):
    entry.filename = body['filename']
    entry.type = body['type']

    try:
        entry.size = int(body['size'])
    except ValueError:
        raise web.HTTPError(400, status_message='Size Must Be In Bytes')

    entry.date = date

    update(entry, body)

    return entry


def update(entry, body):
    try:
        entry.expire = float(body['expire'])
    except ValueError:
        raise web.HTTPError(400, status_message='Time Must Be In Seconds Since The Epoch')


def output(entry):
    return {'alias': entry.alias, 'filename': entry.filename, 'type': entry.type, 'size': entry.size, 'date': entry.date, 'expire': entry.expire}


class Page(page.PageHandler):
    directory = os.path.dirname(__file__) + '/html'
    page = 'index.html'


class Namespace(json.JSONHandler):
    def do_get(self):
        if not self.request.resource.endswith('/'):
            self.response.headers['Location'] = self.request.resource + '/'

            return 307, ''

        try:
            return 200, list(output(value) for value in storage.values(self.groups[0]))
        except KeyError:
            raise web.HTTPError(404)

    def do_post(self):
        if self.request.headers.get('Content-Type') != 'application/json':
            raise web.HTTPError(400, status_message='Body Must Be JSON')

        entry = storage.create(self.groups[0])
        create(entry, self.request.body, time.time())

        self.response.headers['Location'] = self.request.resource + entry.alias

        return 201, output(entry)


class Interface(json.JSONHandler):
    def do_get(self):
        try:
            return 200, output(storage.retrieve(self.groups[0], self.groups[1]))
        except KeyError:
            raise web.HTTPError(404)

    def do_put(self):
        if self.request.headers.get('Content-Type') != 'application/json':
            raise web.HTTPError(400, status_message='Body Must Be JSON')

        try:
            entry = storage.retrieve(self.groups[0], self.groups[1])

            update(entry, self.request.body)

            return 204, ''
        except KeyError:
            entry = storage.create(self.groups[0], self.groups[1])
            create(entry, self.request.body, time.time())

            return 201, output(entry)

    def do_delete(self):
        try:
            storage.remove(self.groups[0])

            return 204, ''
        except KeyError:
            raise web.HTTPError(404)


class Store(web.HTTPHandler):
    def respond(self):
        self.filename = storage.path + self.groups[0] + '/' + self.groups[1]

        return super().respond()

    def do_get(self):
        try:
            entry = storage.retrieve(self.groups[0], self.groups[1])
        except KeyError:
            raise web.HTTPError(404)

        self.response.headers['Content-Type'] = entry.type
        self.response.headers['Content-Filename'] = entry.filename
        self.response.headers['Last-Modified'] = web.mktime(time.gmtime(entry.date))
        self.response.headers['Expires'] = web.mktime(time.gmtime(entry.expire))

        return file.ModifyFileHandler.do_get(self)

    def do_put(self):
        try:
            entry = storage.retrieve(self.groups[0], self.groups[1])
        except KeyError:
            raise web.HTTPError(404)

        if self.request.headers['Content-Length'] != str(entry.size):
            raise web.HTTPError(400, status_message='Content-Length Does Not Match Database Size')

        if 'Content-Type' in self.request.headers and self.request.headers['Content-Type'] != entry.type:
            raise web.HTTPError(400, status_message='Content-Type Does Not Match Database Type')

        return file.ModifyFileHandler.do_put(self)


routes.update({'/': Page, '/api': Namespace, '/api' + namespace: Namespace, '/api' + namespace + alias: Interface, '/store': Store, '/store' + namespace + alias: Store})
error_routes.update(json.new_error())


def start():
    global http

    http = web.HTTPServer(config.addr, routes, error_routes, log=log.httplog)
    http.start()


def stop():
    global http

    http.stop()
    http = None
