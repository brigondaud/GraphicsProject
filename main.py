#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
from viewer import Viewer
from skybox import Skybox
from Ground import Ground

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()
    sky = Skybox()
    ground = Ground(-1, 1, -1, 1, 10, 50, 0.2)
    for mesh in sky.getMeshes():
        viewer.add(mesh)

    viewer.run()

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()