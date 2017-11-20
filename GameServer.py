import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
import cocos

##########################################################################################
class GameClientChannel(Channel):
	"""
	This is the server representation of a single connected client.
	"""
	def __init__(self, *args, **kwargs):
		self.nickname = "anonymous"
		Channel.__init__(self, *args, **kwargs)
	
	def Close(self):
		self._server.DelPlayer(self)
	
	##################################
	### Network specific callbacks ###
	##################################
	
	def Network_message(self, data):
		self._server.SendToAll({"action": "message", "message": data['message'], "who": self.nickname})
	
	def Network_nickname(self, data):
		self.nickname = data['nickname']
		self._server.SendPlayers()

##########################################################################################
class GameServer(Server):
	channelClass = GameClientChannel
	
	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)
		self.players = WeakKeyDictionary()
		print 'Server launched'
	
	def Connected(self, channel, addr):
		self.AddPlayer(channel)
	
	def AddPlayer(self, player):
		print "New Player" + str(player.addr)
		self.players[player] = True
		self.SendPlayers()
		print "players", [p for p in self.players]
	
	def DelPlayer(self, player):
		print "Deleting Player" + str(player.addr)
		del self.players[player]
		self.SendPlayers()
	
	def SendPlayers(self):
		self.SendToAll({"action": "players", "players": [p.nickname for p in self.players]})
	
	def SendToAll(self, data):
		[p.Send(data) for p in self.players]
	
        


##########################################################################################
class ServerAction(cocos.actions.Action):
    """ """
    
    def step(self, dt):
        """ """
        self.target.step(dt)


##########################################################################################
class ServerLayer(cocos.layer.Layer):
    """ """
    def start(self, host, port):
        """ """
        self.server = GameServer(localaddr=('', int(port)))
        self.do(ServerAction())
        
    def step(self, dt):
        """ """
        self.server.Pump()


##########################################################################################
if __name__ == "__main__":
    host = 'localhost'
    port = '8081'
    if (len(sys.argv) != 2) and (len(sys.argv) != 0):
        print "Usage:", sys.argv[0], "host:port"
        print "e.g.", sys.argv[0], "localhost:31425"
    else:
        host, port = sys.argv[1].split(":")
      
    print "starting", host, ":", port
    window = cocos.director.director.init(1024, 760)
    serverLayer = ServerLayer()
    scene = cocos.scene.Scene(serverLayer)
    serverLayer.start(host, port)
    cocos.director.director.run(scene)
