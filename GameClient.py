from PodSixNet.Connection import connection, ConnectionListener
import sys
import cocos

##########################################################################################
class Client(ConnectionListener):
    """ """
    
    def __init__(self, host, port):
        self.Connect((host, port))
     
    def Loop(self):
        connection.Pump()
        self.Pump()

    def setNickname(self, name):
        connection.Send({"action": "nickname", "nickname": name})

    #######################################
    ### Network event/message callbacks ###
    #######################################
    
    def Network_players(self, data):
        print "*** players: " + ", ".join([p for p in data['players']])
    
    def Network_message(self, data):
        print data['who'] + ": " + data['message']
    
    # built in stuff

    def Network_connected(self, data):
        print "You are now connected to the server"
    
    def Network_error(self, data):
        print 'error:', data['error'][1]
        connection.Close()
    
    def Network_disconnected(self, data):
        print 'Server disconnected'
        exit()


##########################################################################################
class ClentAction(cocos.actions.Action):
    """ """
    
    def step(self, dt):
        """ """
        self.target.step(dt)


##########################################################################################
class ClientLayer(cocos.layer.Layer):
    """ """
    def start(self, host, port):
        """ """
        self.client = Client(host, int(port))
        self.do(ClentAction())
        
    def step(self, dt):
        """ """
        self.client.Loop()

    def setNickname(self, name):
        self.client.setNickname(name)
        
        
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
    clientLayer = ClientLayer()
    scene = cocos.scene.Scene(clientLayer)
    clientLayer.start(host, port)
    cocos.director.director.run(scene)

