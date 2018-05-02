#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
from viewer import Viewer
from skybox import Skybox
from texture import *
from skinning import *
from texture_skin import *
from Ground import Ground

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()
    meshes = load_textured("cube/cube/cube.obj")
    for mesh in meshes:
        viewer.add(mesh)


    ground = Ground((0, 0), 1, 1)
    # viewer.add(ground.mesh)

    viewer.run()

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()
