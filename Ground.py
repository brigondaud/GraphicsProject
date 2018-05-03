import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
from texture import TexturedMesh
from texture import Texture
from PIL import Image
import numpy as np
from math import floor
import operator
from mesh import VertexArray
from shader import Shader

G_VERT = """#version 330 core
uniform mat4 modelviewprojection;
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 tex_uv;
out vec2 uvCoords;
void main() {
    gl_Position = modelviewprojection * vec4(position, 1);
    uvCoords = tex_uv;
}"""

G_FRAG = """#version 330 core
uniform sampler2D diffuseMap;
uniform sampler2D normalMap;

in vec2 uvCoords;
out vec4 outColor;
void main() {
    
    // Get the normal in the normal map and normalize to have it between 0 and 1
    vec3 normal = normalize((texture(normalMap, uvCoords).rgb)*2.0-1.0);

    outColor = vec4(texture(diffuseMap, uvCoords).rgb * dot(normal, vec3(0, 1, 0.5)), 1);
}"""

class Ground:
    """
    non flat ground in the scene
    """

    def __init__(self, origin, widthScale, heightScale):
        """
        init the mesh that represents the ground
        """

        #Textures and height map
        self.texture = Texture("ground/ground.jpg")
        self.normalMap = Texture("ground/normal.jpg")
        self.heightMap = Image.open("ground/heightMap.png")
        
        self.shader = Shader(G_VERT, G_FRAG)
        
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

    def getHeight(self, x, z):
        return self.origin[1] + self.heights[(x - self.origin[0], z - self.origin[2])]

    def getSlope(self, x0, z0, x1, z1):
        return - np.arcsin((self.getHeight(x1, z1) - self.getHeight(x0, z0))/(255*self.heightScale))/np.pi * 180


                #Creating the normals for each triangle
                
        
        
        self.vertexArray = VertexArray([np.array(self.vertices), np.array(self.texels)], np.array(self.faces, dtype=np.uint32))

    def draw(self, projection, view, model, win=None, **_kwargs):
        """
        draws the ground using a normal map
        """
        GL.glUseProgram(self.shader.glid)

        # projection geometry
        loc = GL.glGetUniformLocation(self.shader.glid, 'modelviewprojection')
        GL.glUniformMatrix4fv(loc, 1, True, projection @ view @ model)

        # Texture and normal mapping
        loc = GL.glGetUniformLocation(self.shader.glid, 'diffuseMap')
        GL.glUniform1i(loc, 0)

        loc = GL.glGetUniformLocation(self.shader.glid, 'normalMap')
        GL.glUniform1i(loc, 1)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)

        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.normalMap.glid)


        #Draw the vertex array
        self.vertexArray.draw(GL.GL_TRIANGLES)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)