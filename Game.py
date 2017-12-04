import sys
import socket
import cocos
import pyglet
from GameClient import ClientLayer
from GameServer import ServerLayer
from cocos.scenes.transitions import FadeTRTransition
        

##########################################################################################
class IntroMenu(cocos.menu.Menu):
    """
    """
    def __init__( self, game ):
        """ """
        super( IntroMenu, self ).__init__()
        self.game = game
        self.font_item = {
            'font_name': 'Arial',
            'font_size': 32,
            'bold': True,
            'color': (220, 200, 220, 100),
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 42,
            'bold': True,
            'color': (255, 255, 255, 255),
        }

        l = []
        l.append( cocos.menu.MenuItem('Join Game',
            self.game.on_join_game ) )
        l.append( cocos.menu.MenuItem('Host Game',
            self.game.on_host_game ) )
        l.append( cocos.menu.EntryMenuItem('Name:',
            self.game.on_name,
            self.game.host) )
        l.append( cocos.menu.MenuItem('Quit', self.game.on_quit ) )

        self.create_menu( l )
  

##########################################################################################
class Game(object):
    """ """

    def makeClientLayer(self):
        return ClientLayer()
        
    def makeServerLayer(self):
        return ServerLayer()
        
    def run(self, window, nickname, host, port):
        self.nickname = nickname
        self.host = host
        self.port = port
        print "starting", self.host, ":", self.port
        menuBackgroundLayer = cocos.layer.ColorLayer(0, 100, 0, 255,
            width=window.width, height=window.height)
        menuLayer = IntroMenu(self)
        menuBackgroundLayer.add(menuLayer)
        scene = cocos.scene.Scene(menuBackgroundLayer)
        cocos.director.director.set_show_FPS(True)
        cocos.director.director.run(scene)

    def on_join_game(self):
        """ """
        self.clientLayer = self.makeClientLayer()
        scene = cocos.scene.Scene(self.clientLayer)
        cocos.director.director.replace(FadeTRTransition(scene, 2))
        self.clientLayer.start(host, port)
        self.clientLayer.setNickname(self.nickname)

    def on_host_game(self):
        """ """
        self.serverLayer = self.makeServerLayer()
        scene = cocos.scene.Scene(self.serverLayer)
        cocos.director.director.replace(FadeTRTransition(scene, 2))
        self.serverLayer.start(host, port)

    def on_name(self, value):
        """ """
        self.nickname = value
        
    def on_quit(self):
        """ """
        pyglet.app.exit()
    
##########################################################################################
if __name__ == "__main__":
    host = 'localhost'
    port = '8081'
    if (len(sys.argv) != 2) and (len(sys.argv) != 0):
        print "Usage:", sys.argv[0], "host:port"
        print "e.g.", sys.argv[0], "localhost:31425"
    else:
        host, port = sys.argv[1].split(":")
      
    ownID = socket.gethostbyname(socket.gethostname())
    caption = 'Wormageddon' + ' ' + str(ownID) + ':' + str(port)
    window = cocos.director.director.init(1024, 760, caption = caption, fullscreen=False)
    game = Game()
    game.run(window, ownID, host, port)
