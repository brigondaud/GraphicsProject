#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
from viewer import Viewer
from load import load_textured

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()

    for mesh in load_textured("skybox/skybox.obj"):
        viewer.add(mesh)

    viewer.run()

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()