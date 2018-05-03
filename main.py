#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
from viewer import Viewer
from skybox import Skybox
from texture import *
from skinning import *
from texture_skin import *
from Ground import Ground
from dino import Dino

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()

    ground = Ground((-100,-120, -100), 3, 0.8)
    viewer.add(ground)
    
    dino = Dino(ground)
    viewer.add(dino)

    viewer.run(dino)

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()
