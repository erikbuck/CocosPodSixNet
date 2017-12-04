import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
import cocos
import pyglet

##########################################################################################
class GameClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, *args, **kwargs):
        self.nickname = str(self.addr)
        self.commands = []
        Channel.__init__(self, *args, **kwargs)
    
    def Close(self):
        self._server.DelPlayer(self)
    
    ##################################
    ### Network specific callbacks ###
    ##################################
        
    def Network_update(self, data):
        print data
        self.commands.append(data)
        
    def Network_message(self, data):
        #print 'received', data['message'], 'from', self.nickname
        sys.stdout.flush()
        self._server.SendToAll({"action": "message", "message": data['message'], "who": self.nickname})
    
    def Network_nickname(self, data):
        self.nickname = data['nickname']
        self._server.SendPlayers()

##########################################################################################
class GameServer(Server):
    """
    This class keeps track of player clients and provides methods for sending messages 
    to player clients.
    """

    channelClass = GameClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.playerChannels = WeakKeyDictionary()
        print 'Server launched'
    
    def Connected(self, channel, addr):
        """ This method is called automatically when a player client connects. """
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        """ This method stores a channel to player client in self.playerChannels keyed
        by channel. """
        print "New Player" + str(player.addr)
        self.playerChannels[player] = True
        self.SendPlayers()
        print "playerChannels", [p for p in self.playerChannels]
    
    def DelPlayer(self, player):
        """ This method deletes a channel to player client in self.playerChannels keyed
        by channel. """
        print "Deleting Player" + str(player.addr)
        del self.playerChannels[player]
        self.SendPlayers()
    
    def SendPlayers(self):
        """ This method sends a list of player nicknames to every connected client 
        player. """
        self.SendToAll({"action": "players", 
                "players": [p.nickname for p in self.playerChannels]})
    
    def SendToAll(self, data):
        """ This method sends data to every connected client player. """
        [p.Send(data) for p in self.playerChannels]
    
##########################################################################################
class ServerAction(cocos.actions.Action):
    """ This Cocos2D Action calls it target's step() method."""
    
    def step(self, dt):
        """ """
        self.target.step(dt)

##########################################################################################
class ServerLayer(cocos.layer.Layer):
    """ This is a base class that starts a PodSixNet server and pumps data to connected 
    player clients """
    def start(self, game, host, port):
        """ """
        self.game = game
        self.server = GameServer(localaddr=('', int(port)))
        self.do(ServerAction())
        
    def step(self, dt):
        """ """
        for channel in self.server.playerChannels: # Is this thread safe?!?
            if not channel.addr[0] in self.game.players:
                self.game.addPlayer(channel.addr[0])
            
            commands = channel.commands # Is this thread sage?!?
            for command in commands:
                if command['action'] == 'update':
                    print 'command', command
                else:
                    print 'Error: Unknown command,', command,\
                        'from client,', channel

            channel.commands = [] # Is this thread safe?!?
            
        sys.stdout.flush()
        self.server.Pump()     
      
##########################################################################################
if __name__ == "__main__":
    """ Setup both PodSixNet and Cocos2D. """
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
    serverLayer.start(None, host, port)
    #print 'GameServer'
    cocos.director.director.run(scene)
