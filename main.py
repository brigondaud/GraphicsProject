#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
from viewer import Viewer
from skybox import Skybox
from texture import *
from skinning import *
from texture_skin import *

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()
    meshes = load_textured_skinned("dino/Dinosaurus_walk.dae")

    for mesh in meshes:
        print(mesh)
        viewer.add(mesh)

    viewer.run()

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()
