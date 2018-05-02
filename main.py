#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
from viewer import Viewer
from skybox import Skybox
from texture import *
from skinning import *
from texture_skin import *
from Ground import Ground

class Dino:
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, *keys, **kwargs):
        self.mesh = load_textured_skinned("dino/Dinosaurus_walk.dae")[0]


    def draw(self, projection, view, model, **param):
        """ When redraw requested, interpolate our node transform from keys """
        self.mesh.draw(projection, view, model, **param)

    def on_key(self, _win, key, _scancode, action, _mods):
        print("out", _win, key, _scancode, action, _mods)
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_LEFT:
                self.y_angle -= rotation_step
                self.y_angle %= 360
            elif key == glfw.KEY_RIGHT:
                self.y_angle += rotation_step
                self.y_angle %= 360
            if key == glfw.KEY_UP:
                self.x_angle += rotation_step
                self.x_angle %= 360
            elif key == glfw.KEY_DOWN:
                self.x_angle -= rotation_step
                self.x_angle %= 360
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)
            if key == glfw.KEY_W:
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.fill_modes))
            if key == glfw.KEY_SPACE:
                print(3)
                # glfw.set_time(0)

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()

    dino = Dino()
    viewer.add(dino)

    ground = Ground((-100,-120 , -100), 5, 0.8)
    viewer.add(ground.mesh)

    viewer.run()

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()
