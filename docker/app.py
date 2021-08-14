import falcon

class HelloResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ("Here you go!!!!!!")

class Page2Resource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ("You're almost there :)")

app = falcon.API()

hey = HelloResource()

there = Page2Resource()

app.add_route('/', hey)
app.add_route('/page2', there)