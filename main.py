#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
from viewer import Viewer

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()
    viewer.run()

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()