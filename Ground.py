from TexturedMesh import TexturedMesh
from Texture import Texture
from PIL import Image
import numpy as np
from math import floor

G_VERT = """#version 330 core
uniform mat4 modelviewprojection;
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
out vec3 uv_pos;
void main() {
    gl_Position = modelviewprojection * vec4(position, 1);
    uv_pos = color;
}"""

G_FRAG = """#version 330 core
uniform sampler2D diffuseMap;
in vec3 uv_pos;
out vec4 outColor;
void main() {
    outColor = vec4(uv_pos, 1);
}"""


class Ground:
    """
    non flat ground in the scene
    """

    def __init__(self, origin, widthScale, heightScale):
        """
        init the mesh that represents the ground
        """
        self.texture = Texture("ground/ground.jpg")
        self.heightMap = Image.open("ground/heightMap.png")
        self.origin = origin
        self.widthScale = widthScale
        self.heightScale = heightScale

        self.terrainHeights = []

        self.vertexPool = self.initVertexPool()
        
        # self.groundAttributes, self.groundIndexes = self.generateGroundMesh()

        # self.mesh = TexturedMesh(self.texture, self.groundAttributes, self.groundIndexes)

    def initVertexPool(self):
        """
        inits the vertex pool
        """
        pool = {}
        for x in range(self.heightMap.size[0]):
            for z in range(self.heightMap.size[1]):
                xV = (self.origin[0] + x)*self.widthScale
                yV = self.heightMap.getpixel((x, z))*self.heightScale
                zV = (self.origin[1] + z)*self.widthScale
                pool[(x, z)] = (GroundVertex(xV, yV, zV))
        return pool

    def generateTile(self, bottomRight, image):
        """
        generates a tile for the ground, giving the bottom right index
        """
        mesh, texels, faces = [], [], []
        #Generates the four

    def generateGroundMesh(self):
        """
        generates the ground mesh
        """
        # xStep = (self.xmax - self.xmin)/self.resolution
        # zStep = (self.zmax - self.zmin)/self.resolution

        # xMapStep = self.heightMap.size[0]/self.resolution
        # yMapStep = self.heightMap.size[1]/self.resolution

        texels, faces = [], []

        # #Creating the ground mesh and the texels
        # for i in range(self.resolution):
        #     for j in range(self.resolution):
        #         heightValue = self.heightMap.getpixel((floor(i*xMapStep), floor(j*yMapStep)))
        #         heightValue *= self.scale
        #         self.terrainHeights.append((self.xmin + i*xStep, heightValue, self.zmin + j*zStep))
        #         texels.append((i%2, j%2))

        #Creating the faces
        # for i in range(self.resolution-1):
        #     for j in range(self.resolution-1):
        #         faces.append((self.resolution*i, self.resolution*(i+1), self.resolution*i+1))



        attributes = [np.array(self.terrainHeights), np.array(texels)]
        faces = np.array(faces)

        return attributes, faces

class GroundVertex:
    """
    utility class to compute the ground mesh
    """
    Count = 0
    def __init__(self, x, y, z):
        """
        each vertex is init with it's coordinates and the current vertex count
        in order to use faces in the ground mesh.
        """
        self.x, self.y, self.z, self.vertexNumber = x, y, z, GroundVertex.Count
        # update the vertex count
        GroundVertex.Count += 1
        # corresponding texel
        self.texel = (x%2, z%2)