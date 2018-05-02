from texture import TexturedMesh
from texture import Texture
from PIL import Image
import numpy as np
from math import floor
import operator

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
        #To access heights for the dinosaur.
        self.heights = {}

        #Creating the vertices
        sizeX = self.heightMap.size[0]
        sizeZ = self.heightMap.size[1]
        self.vertices, self.texels, self.faces = [], [], []
        for z in range(sizeZ):
            for x in range(sizeX):
                self.vertices.append(
                    ((self.origin[0]+x)*self.widthScale,
                    self.origin[1] + self.heightMap.getpixel((x, z))[0]*self.heightScale,
                    (self.origin[2]+z)*self.widthScale)
                )
                self.heights[(x, z)] = self.heightMap.getpixel((x, z))[0]*self.heightScale
                self.texels.append((x%2, z%2))

        #Creating the mesh
        for z in range(sizeZ-1):
            for x in range(sizeX-1):
                self.faces.append(
                    (x + z*sizeX, x + (z+1)*sizeX, (x+1) + z*sizeX)
                )
                self.faces.append(
                    (x + (z+1)*sizeX, (x+1) + (z+1)*sizeX, (x+1) + z*sizeX)
                )

        self.mesh = TexturedMesh(self.texture, [np.array(self.vertices), np.array(self.texels)], np.array(self.faces, dtype=np.uint32))
