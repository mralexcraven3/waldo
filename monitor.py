import tornado.websocket
import tornado.gen
import tornadoredis
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornadoredis
import os

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("app/templates/index.html")

class MessageHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, 'waldo')
        self.client.listen(self.on_message)

    def on_message(self, msg):
        if type(msg) == unicode:
            import pdb; pdb.set_trace()
        if msg.kind == 'message':
            self.write_message(str(msg.body))
        if msg.kind == 'disconnect':
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    def on_close(self):
        if self.client.subscribed:
            self.client.unsubscribe('test_channel')
            self.client.disconnect()

settings = {
    'debug': True,
}

static_path = os.path.join(os.path.dirname(__file__), 'app/assets')

application = tornado.web.Application([
    (r'/websocket', MessageHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
    (r'/', MainHandler)
], **settings)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(1235)
    tornado.ioloop.IOLoop.instance().start()
