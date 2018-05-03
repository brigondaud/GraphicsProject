#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""
# Python built-in modules
import os                           # os function, i.e. checking file status

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from transform import translate, rotate, scale, frustum, perspective, GLFWTrackball, identity, lerp, vec
from transform import vec as vect
import pyassimp                     # 3D ressource loader
import pyassimp.errors              # assimp error management + exceptions
from PIL import Image
from transform import (quaternion_slerp, quaternion_matrix, quaternion,
                       quaternion_from_euler, lookat)
from loader import *
from node import*
from skybox import Skybox

# ------------  Viewer class & window management ------------------------------
class Viewer:
    """ GLFW viewer window, with classic initialization & graphics loop """

    def __init__(self, width=1000, height=1000, skybox=None):
        self.y_angle = 0
        self.x_angle = 0
        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])

        # version hints: create GL window with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # register event handl  ers
        glfw.set_key_callback(self.win, self.on_key)
        self.trackball = GLFWTrackball(self.win)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.1, 0.1, 0.1, 0.1)

        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.skybox =  Skybox("skybox2.jpg")
        # initially empty list of object to draw
        self.drawables = []

    def run(self, observable):
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):
            # clear draw buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # draw our scene objects

            winsize = glfw.get_window_size(self.win)
            view =  self.trackball.view_matrix()
            # view = lookat(np.array((0, 0, 0)), observable.mesh.)
            projection = self.trackball.projection_matrix(winsize)
            model =  np.linalg.inv(observable.mesh.transform) @ translate(0, -4, -6)

            if self.skybox is not None:
                self.skybox.drawskybox(projection, view)

            for drawable in self.drawables:
                drawable.draw(projection, view, model, win=self.win)

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

    def add(self, *drawables):
        """ add objects to draw in this window """
        self.drawables.extend(drawables)

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        rotation_step = 5
        for drawable in self.drawables:
            drawable.on_key(_win, key, _scancode, action, _mods)

        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)
            if key == glfw.KEY_W:
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.fill_modes))
            if key == glfw.KEY_SPACE:
                pass
                # glfw.set_time(0)



# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    # place instances of our basic objects
#

    phi, theta, psi = 30, 20, 40
#    # construct our robot arm hierarchy for drawing in viewer
    cylinder = Cylinder(40)             # re-use same cylinder instance

    limb_shape = Node(transform=scale(1/4, 1/4, 5))  # make a thin cylinder
    limb_shape.add(cylinder)          # common shape of arm and forearm

    rotate2 = RotationControlNode(glfw.KEY_E, glfw.KEY_D, (1, 0, 0))
    rotate2.add(limb_shape)

    forearm_node = Node(transform=translate(0, 0, 5 - 1/4) @ rotate((1, 0, 0), psi))    # robot arm rotation with phi angle
    forearm_node.add(rotate2)


    arm_node = Node(transform=translate(0, 0, 0.5) @ rotate((1, 0, 0), phi))    # robot arm rotation with phi angle
    arm_node.add(limb_shape, forearm_node)

    rotate1 = RotationControlNode(glfw.KEY_F, glfw.KEY_S, (1, 0, 0))
    rotate1.add(arm_node)

    # make a flat cylinder
    base_shape = Node(transform=identity(), children=[cylinder])
    # viewer.add(base_node)

    #viewer.add(TexturedPlane("grass.png"))

    # viewer.add(Cylinder(200))


    translate_keys = {0: vec(0, 0, 0), 2: vec(1, 1, 0), 4: vec(0, 0, 0)}
    rotate_keys = {0: quaternion(), 2: quaternion_from_euler(180, 45, 90),
                   3: quaternion_from_euler(180, 0, 180), 4: quaternion()}
    scale_keys = {0: 1, 2: 0.5, 4: 1}
    # keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys)

    base_node = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys)
    base_node.add(base_shape, rotate1)
    viewer.add(base_node)

#    meshes = load_textured("cube/cube/cube.obj")

    # meshes = load("suzanne.obj")
    # for m in meshes:
    #     keynode.add(m)
    # viewer.add(keynode)



    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    glfw.set_time(0)
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
