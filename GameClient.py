from PodSixNet.Connection import connection, ConnectionListener
import sys
import cocos
from cocos.menu import *
import pyglet

##########################################################################################
class Client(ConnectionListener):
    """ """
    
    def __init__(self, target, host, port):
        self.target = target
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
        #print data['who'] + ": " + data['message']
        self.target.showMessage( data['who'] + ": " + data['message'])
   
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
class ClientAction(cocos.actions.Action):
    """ """
    
    def step(self, dt):
        """ """
        self.target.step(dt)

##########################################################################################
class ChatMenu(Menu):
    def __init__( self, target ):
        super( ChatMenu, self ).__init__("")
        self.target = target
        
        self.font_item = {
            'font_name': 'Arial',
            'font_size': 14,
            'bold': True,
            'color': (220, 200, 220, 100),
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 14,
            'bold': True,
            'color': (255, 255, 255, 255),
        }
        self.menu_valign = BOTTOM
        self.menu_halign = LEFT
        l = []
        l.append( EntryMenuItem('Chat:', self.on_chat, '') )
        l.append( MenuItem('Send', self.on_send ) )

        windowSize = (cocos.director.director.window.width, 
                cocos.director.director.window.height)
        self.create_menu( l, layout_strategy=fixedPositionMenuLayout(
                [(7, 14), (windowSize[0] - 80, 14)]))

    def on_text( self, text ):
        super(ChatMenu, self).on_text(text)
        if '\r' in text:
            self.on_send()
        return True
        
    def on_chat( self, value ):
        self.target.on_chat(value)

    def on_send( self ):
        self.target.on_send()

class KeyboardInputLayer(cocos.layer.Layer):
   """
   """

   # You need to tell cocos that your layer is for handling input!
   # This is key (no pun intended)!
   # If you don't include this you'll be scratching your head wondering why your game isn't accepting input
   is_event_handler = True

   def __init__(self):
      """ """
      super(KeyboardInputLayer, self).__init__()
      self.keys_being_pressed = set()
      self.isInChatMode = False

   def on_key_press(self, key, modifiers):
      """ """
      if not self.isInChatMode:
        self.keys_being_pressed.add(key)

   def on_key_release(self, key, modifiers):
      """ """
      if not self.isInChatMode:
        if key in self.keys_being_pressed:
            self.keys_being_pressed.remove(key)

##########################################################################################
class ClientLayer(KeyboardInputLayer):
    """ """
    def start(self, host, port):
        """ """
        self.client = Client(self, host, int(port))
        self.chatMessage = ''
        self.messageLabel = None
        self.do(ClientAction())
        
    def step(self, dt):
        """ """
        connection.Pump()       
        self.client.Pump()
        sys.stderr.flush()
        sys.stdout.flush()

    def setNickname(self, name):
        self.client.setNickname(name)
        
    def on_key_press(self, key, modifiers):
        """ """
        super(ClientLayer, self).on_key_press(key, modifiers)
        if not self.isInChatMode:
            if pyglet.window.key.TAB == key:
                self.startChat()
 
    def startChat(self):
        self.isInChatMode = True
        self.chatMenu = ChatMenu(self)
        self.add(self.chatMenu, z=1000)

    def endChat(self):
        self.isInChatMode = False
        self.chatMenu.kill()
        self.chatMenu = None
        
    def on_chat( self, value ):
        self.chatMessage = value
        
    def on_send( self ):
        #print 'Sending:', self.chatMessage
        self.client.Send({"action": "message", "message":self.chatMessage})
        self.endChat()
    
    def showMessage(self, text):
         #print 'Showing:', self.chatMessage
         self.messageLabel = cocos.text.Label(text=text, color=(128, 200, 128, 255), 
                position=(7,28), font_size=14)
         self.add(self.messageLabel)
         self.messageLabel.do(cocos.actions.Delay(1) + cocos.actions.FadeOut(1) + \
                cocos.actions.CallFuncS(cocos.text.Label.kill))
       

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
    print 'GameClient'
    cocos.director.director.run(scene)

