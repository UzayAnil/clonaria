#!/usr/bin/env python

from __future__ import division
import getopt, pyglet, sys, time
from pyglet.window import key, mouse

from const import Const
from entity import Entity
from model import Model
from player import Player
from util import Util
from world import World

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d")
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)

    for o, a in opts:
        if o == "-d":
            Util().debug += 1

    Util().window = window = pyglet.window.Window(resizable=True)

    Util().world = world = World("world1", (400, 400))
    world.generate()

    Util().player = player = Player(Util().entityModels['player'], world, (world.width / 2, world.height / 2 + 5))

    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    # Implement mouse state like the keyboard has because pyglet lacks one
    buttons = []
    Util().mouseLoc = 0, 0

    # Set window background color
    pyglet.gl.glClearColor(0, 40, 200, 0)

    batch = Util().batch

    if Util().debug:
        debugStats = [  '"FPS: {}".format(pyglet.clock.get_fps())',
                        '"player.x: {}".format(self.player.x)',
                        '"player.y: {}".format(self.player.y)',
                        '"player.vx: {}".format(self.player.vx)',
                        '"player.vy: {}".format(self.player.vy)',
                        '"player.stillJumping: {}".format(self.player.stillJumping)',
                        '"player.againstBlockDown: {}".format(self.player.againstBlockDown)',
                        '"player.againstBlockLeft: {}".format(self.player.againstBlockLeft)']
        Util().addDebugStats(debugStats)

        Util().debugTarget = pyglet.sprite.Sprite(pyglet.image.SolidColorImagePattern(color=(255,0,0,128)).create_image(16, 16), batch=Util().batch, group=Util().group['debug'])

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        buttons.append(button)

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        buttons.remove(button)

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        Util().mouseLoc = x, y

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        Util().mouseLoc = x, y

    @window.event
    def on_draw():
        window.clear()
        world.prepareDraw()
        player.prepareDraw()
        if Util().debug:
            Util().prepareDrawDebugStats()
            Util().prepareDrawDebugBlocks()
            Util().prepareDrawDebugTarget()

        batch.draw()

    def update(self):
        playerJumping = False

        # Handle keyboard input
        if keys[key.LEFT] or keys[key.A]:
            player.walkLeft()
        if keys[key.RIGHT] or keys[key.D]:
            player.walkRight()
        if keys[key.SPACE]:
            playerJumping = True
            player.jump()
        if keys[key.PLUS] or keys[key.NUM_ADD]:
            Const.ZOOM += 1. / Const.PPB
        if keys[key.MINUS] or keys[key.NUM_SUBTRACT]:
            Const.ZOOM -= 1. / Const.PPB
        if keys[key.EQUAL]:
            Const.ZOOM = 1
        
        # Handle mouse input
        if mouse.LEFT in buttons:
            loc = Util().pixelsToBlocks(Util().mouseLoc)
            world.setBlockAt(*loc)
        if mouse.MIDDLE in buttons:
            loc = Util().pixelsToBlocks(Util().mouseLoc)
            world.setBlockAt(*loc, blockType=Util().blockModels['platform'])
        if mouse.RIGHT in buttons:
            loc = Util().pixelsToBlocks(Util().mouseLoc)
            world.setBlockAt(*loc, blockType=Util().blockModels['cone'])

        if not playerJumping or player.curJumpTicks < 1:
            player.stillJumping = False

        player.applyGravity()
        #player.applyFriction()
        player.move()

    pyglet.clock.schedule_interval(update, 1/Const.TPS)
    pyglet.app.run()
