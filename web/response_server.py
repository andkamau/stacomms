from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from stacomms.web.user_responses import User
from stacomms.web.html_templates import responses_template, _responses_template

class UserResponse(Resource):

    def __init__(self, user_id):
        Resource.__init__(self)
        self.user_id = user_id

    def render_GET(self, request):
        user = User(self.user_id)
        user_history = user.get_user_history()
        resp = ""
        for each in user_history:
            username = user_history[each]['leadersname']
            resp += responses_template.format(**user_history[each]) % "TL"


            print each
            resp += str(each) + "<hr><br/>"
        return _responses_template.format(username, resp)
        #return "<html><body><pre>%s, %s</pre></body></html>" % ("Hey there...", self.user_id)

class Server(Resource):
  def getChild(self, user_id, request):
      return UserResponse(int(user_id))

root = Server()
factory = Site(root)
reactor.listenTCP(6091, factory)
reactor.run()
