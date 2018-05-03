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
uniform mat4 modelView;

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 tex_uv;
layout(location = 2) in vec3 normal;
layout(location = 3) in vec3 tangent;
layout(location = 4) in vec3 bitangent;

out vec2 uvCoords;
out vec3 light;

void main() {
    gl_Position = modelviewprojection * vec4(position, 1);
    uvCoords = tex_uv;

    //Creating the TBN matrix
    mat3 modelView3 = mat3(modelView);
    vec3 normalCameraSpace = modelView3 * normalize(normal);
    vec3 tangentCameraSpace = modelView3 * normalize(tangent);
    vec3 bitangentCameraSpace = modelView3 * normalize(bitangent);

    mat3 TBN = transpose(mat3(
        tangentCameraSpace,
        bitangentCameraSpace,
        normalCameraSpace
    ));

    //Compute the light direction in the tangent space
    light = TBN * vec3(0.5, 1, 0.5);

}"""

G_FRAG = """#version 330 core

uniform sampler2D diffuseMap;
uniform sampler2D normalMap;

in vec2 uvCoords;
in vec3 light;

out vec4 outColor;

void main() {
    
    // Get the normal in the normal map and normalize to have it between 0 and 1
    vec3 normal = normalize((texture(normalMap, uvCoords).rgb)*2.0-1.0);

    float p = clamp(dot(normalize(normal), normalize(light)), 0, 1);
    outColor = texture(diffuseMap, uvCoords) * p;
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

        #Creating the vertices and attributes
        self.sizeX = self.heightMap.size[0]
        self.sizeZ = self.heightMap.size[1]

        self.vertices, self.texels, self.faces = [], [], []
        self.normals = [np.array((0, 0, 0), dtype=float)]*self.sizeX*self.sizeZ
        self.tangents = [np.array((0, 0, 0), dtype=float)]*self.sizeX*self.sizeZ
        self.bitangents = [np.array((0, 0, 0), dtype=float)]*self.sizeX*self.sizeZ
        
        for z in range(self.sizeZ):
            for x in range(self.sizeX):
                
                #Vertex
                vertex = ((self.origin[0]+x)*self.widthScale,
                    self.origin[1] + self.heightMap.getpixel((x, z))[0]*self.heightScale,
                    (self.origin[2]+z)*self.widthScale)
                self.vertices.append(vertex)

                #Updating height info
                self.heights[(x, z)] = self.origin[1] + self.heightMap.getpixel((x, z))[0]*self.heightScale
                
                #Texel
                self.texels.append((x%2, z%2))


        #Creating the faces
        for z in range(self.sizeZ-1):
            for x in range(self.sizeX-1):
                self.faces.append(
                    (x + z*self.sizeX, x + (z+1)*self.sizeX, (x+1) + z*self.sizeX)
                )
                self.faces.append(
                    (x + (z+1)*self.sizeX, (x+1) + (z+1)*self.sizeX, (x+1) + z*self.sizeX)
                )

        #Computing normals, tangent and bitangents for normal mapping purpose.
        for triangle in self.faces:

            uFace = np.array(self.vertices[triangle[1]]) - np.array(self.vertices[triangle[0]])
            vFace = np.array(self.vertices[triangle[2]]) - np.array(self.vertices[triangle[0]])

            normal = (uFace[1]*vFace[2]-uFace[2]*vFace[1],
                      uFace[2]*vFace[0]-uFace[0]*vFace[2],
                      uFace[0]*vFace[1]-uFace[1]*vFace[0])

            #UV delta for tangent and bitangent
            deltaUV1 = np.array(self.texels[triangle[1]]) - np.array(self.texels[triangle[0]])
            deltaUV2 = np.array(self.texels[triangle[2]]) - np.array(self.texels[triangle[0]])

            #Computing tangents and bitangent
            diff = deltaUV1[0] * deltaUV2[1] - deltaUV1[0] * deltaUV2[0]
            if(diff==0):
                r = 1
            else:
                r = 1/diff;
            tangent = (uFace * deltaUV2[1] - vFace * deltaUV1[1])*r;
            bitangent = (vFace * deltaUV1[0] - uFace * deltaUV2[0])*r;

            #Put the mean for normal, tangent and bitangent for each vertex. Will be normalized in the shader.
            for index in triangle:
                self.normals[index] += normal
                self.tangents[index] += tangent
                self.bitangents[index] += bitangent
        
        self.array = VertexArray([np.array(self.vertices), np.array(self.texels), self.normals, self.tangents, self.bitangents],
            np.array(self.faces, dtype=np.uint32)
            )

    def draw(self, projection, view, model, win=None, **_kwargs):
        """
        draws the ground using a normal map
        """
        GL.glUseProgram(self.shader.glid)

        # projection geometry
        loc = GL.glGetUniformLocation(self.shader.glid, 'modelviewprojection')
        GL.glUniformMatrix4fv(loc, 1, True, projection @ view @ model)

        #modelview matrix
        loc = GL.glGetUniformLocation(self.shader.glid, 'modelView')
        GL.glUniformMatrix4fv(loc, 1, True, view @ model)

        # Texture and normal mapping
        loc = GL.glGetUniformLocation(self.shader.glid, 'diffuseMap')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc, 0)

        loc = GL.glGetUniformLocation(self.shader.glid, 'normalMap')
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.normalMap.glid)
        GL.glUniform1i(loc, 1)

        #Draw the vertex array
        self.array.draw(GL.GL_TRIANGLES)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)

    def on_key(self, _win, key, _scancode, action, _mods):
        """
        catch no event
        """
        pass
        

    def getHeight(self, x, z):
        return self.heights[(x - self.origin[0], z - self.origin[2])]

    def getSlope(self, x0, z0, x1, z1):
        return - np.arcsin((self.getHeight(x1, z1) - self.getHeight(x0, z0))/(255*self.heightScale))/np.pi * 180

    def iterPos(self):
        """
        iterates on all the position of the map (int, int)
        """
        for z in range(self.sizeZ):
            for x in range(self.sizeX):
                yield self.origin[0] + x, self.origin[2] + z