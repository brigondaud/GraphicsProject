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
import numpy as np

def main():
    """ Run the rendering loop for the scene. """
    viewer = Viewer()

    origin = (-100,-120, -100)
    widthScale = 3

    ground = Ground(origin, widthScale, 0.8)
    viewer.add(ground)

    #Generate trees according to a uniform law for appearance
    trees = []
    for x, z in ground.iterPos():
        if(not(x%10) and not(z%10)): #generating
            if(np.random.uniform() > 0.5):
                tree = Tree(x*widthScale, ground.getHeight(x, z)+2, z*widthScale)
                trees.append(tree)
                viewer.add(tree.node)
    
    dino = Dino(ground)
    viewer.add(dino)

    viewer.run(dino)

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()
