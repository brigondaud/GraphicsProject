from TexturedMesh import TexturedMesh
from Texture import Texture
from PIL import Image
import numpy as np
from math import floor


class Ground:
    """
    non flat ground in the scene
    """

    def __init__(self, xmin, xmax, zmin, zmax, maxHeight, resolution, scale):
        """
        init the mesh that represents the ground
        """
        self.texture = Texture("ground/ground.jpg")
        self.heightMap = Image.open("ground/heightMap.png")
        self.xmin, self.xmax, self.zmin, self.zmax = xmin, xmax, zmin, zmax
        self.maxHeight = maxHeight
        self.scale = scale
        self.resolution = resolution        

        self.terrainHeights = []
        
        if(resolution > self.heightMap.size[0] or resolution > self.heightMap.size[1]):
            raise ValueError("Generation du terrain: résolution demandée trop grande pour la height map.")
        
        self.groundAttributes, self.groundIndexes = self.generateGroundMesh()
        self.mesh = TexturedMesh(self.texture, self.groundAttributes, self.groundIndexes)

    def generateGroundMesh(self):
        """
        generates the ground mesh
        """
        xStep = (self.xmax - self.xmin)/self.resolution
        zStep = (self.zmax - self.zmin)/self.resolution

        xMapStep = self.heightMap.size[0]/self.resolution
        yMapStep = self.heightMap.size[1]/self.resolution

        for i in range(self.resolution):
            for j in range(self.resolution):
                heightValue = self.heightMap.getpixel((floor(i*xMapStep), floor(j*yMapStep)))
                heightValue *= self.scale
                self.terrainHeights.append((i*xStep, heightValue, j*zStep))
        attributes = [np.array(self.terrainHeights), np.array((i%2, j%2))]

        faces = []
        faceNumber = 2*(self.resolution-1)**2
        for i in range(faceNumber):
            faces.append((0, 1, 2))

        faces = np.array(faces)

        return attributes, faces

