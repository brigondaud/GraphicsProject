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
    def __init__(self, ground, *keys, **kwargs):
        self.mesh = load_textured_skinned("dino/Dinosaurus_walk.dae")[0]
        self.xyz = np.array([0,ground.getHeight(0, 0),0])
        self.dir = 0
        self.slope = 0
        self.model = identity()
        self.ground = ground


    def draw(self, projection, view, model, **param):
        """ When redraw requested, interpolate our node transform from keys """
        self.mesh.draw(projection, view, model @ self.model, **param)
    def move(self,key):
        angle = [0, 270, 180, 90][self.dir]

        if key == glfw.KEY_LEFT:
            self.dir = (self.dir - 1 + 4) % 4
        elif key == glfw.KEY_RIGHT:
            self.dir = (self.dir + 1) % 4

        dir = np.array([[0, 0, -1], [1, 0, 0], [0, 0, 1], [-1, 0, 0]])[self.dir]
        old_slope = self.slope

        start = vec(self.xyz)
        self.xyz += dir*3
        self.xyz[1] = self.ground.getHeight(self.xyz[0]/3, self.xyz[2]/3)

        self.slope = self.ground.getSlope(start[0]/3, start[2]/3, self.xyz[0]/3, self.xyz[2]/3)

        if key == glfw.KEY_LEFT:
            rotate_keys = {0: quaternion_from_euler(0, angle, old_slope), 1: quaternion_from_euler(0, angle + 90, self.slope)}
        elif key == glfw.KEY_RIGHT:
            rotate_keys = {0: quaternion_from_euler(0, angle, old_slope), 1: quaternion_from_euler(0, angle - 90, self.slope)}
        elif key == glfw.KEY_UP:
            rotate_keys = {0: quaternion_from_euler(0, angle, old_slope), 1: quaternion_from_euler(0, angle, self.slope)}
        # rotate_keys = {0: quaternion(), 1: quaternion()}

        translate_keys = {0: start, 1: vec(self.xyz)}
        scale_keys = {0: .01, 1: .01}
        self.mesh.reset_time()
        self.mesh.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)
        # self.model = translate(z = 1) @ self.model

    def on_key(self, _win, key, _scancode, action, _mods):
        if (action == glfw.PRESS or action == glfw.REPEAT) and (glfw.get_time() - self.mesh.time >= 1):
            if key == glfw.KEY_LEFT or key == glfw.KEY_RIGHT or key == glfw.KEY_UP:
                self.move(key)

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()

    ground = Ground((-100,-120 , -100), 3, 0.8)
    viewer.add(ground.mesh)

    dino = Dino(ground)
    viewer.add(dino)

    ground = Ground((0, 0), 5, 0.8)
    viewer.add(ground)
    viewer.run(dino)

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()
