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
from tree import Tree

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()

    origin = (-100,-120, -100)

    ground = Ground(origin, 3, 0.8)
    viewer.add(ground)

    tree = Tree(0, 0, 0)
    viewer.add(tree.node)
    
    dino = Dino(ground)
    viewer.add(dino)

    viewer.run(dino)

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()
