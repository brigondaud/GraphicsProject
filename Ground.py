from texture import TexturedMesh
from texture import Texture
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

        #Init all the vertices for the ground
        self.vertexPool = self.initVertexPool()

        #Transform into a mesh
        self.vertices, self.texels = [], []
        for vertex, texel in self.iterVertices():
            self.vertices.append(vertex)
            self.texels.append(texel)

        #Init the faces
        self.faces = []
        for x in range(self.heightMap.size[0]-1):
            for z in range(self.heightMap.size[1]-1):
                for triangle in self.generateTile((x, z)):
                    self.faces.append(triangle)
        
        self.mesh = TexturedMesh(self.texture, [np.array(self.vertices), np.array(self.texels)], np.array(self.faces))

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

    def generateTile(self, bottomRight):
        """
        generates a tile for the ground, giving the bottom right index
        it is supposed that the bottomRight is correctly given, i.e. that corresponds
        to a correct bottomRight
        """
        bottomTriangle = (self.vertexPool[bottomRight].vertexNumber,
                          self.vertexPool[bottomRight[0]+1, bottomRight[1]].vertexNumber,
                          self.vertexPool[bottomRight[0], bottomRight[1]+1].vertexNumber)

        upperTriangle = (self.vertexPool[bottomRight[0]+1, bottomRight[1]].vertexNumber,
                         self.vertexPool[bottomRight[0]+1, bottomRight[1]+1].vertexNumber,
                         self.vertexPool[bottomRight[0], bottomRight[1]+1].vertexNumber)
        
        return bottomTriangle, upperTriangle

    def iterVertices(self):
        """
        iterates over all the vertices of the vertex pool
        """ 
        for _, vertex in self.vertexPool.items():
            yield vertex.getVertex()


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

    def getVertex(self):
        """
        returns the vertex
        """
        return (self.x, self.y, self.z), self.texel