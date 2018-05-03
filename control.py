import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
from texture import TexturedMesh
from texture import Texture
from PIL import Image
import numpy as np
from math import floor
import operator
from mesh import VertexArray
from transform import *
from shader import Shader
from itertools import cycle


TEXTURE_VERT = """#version 330 core
uniform mat4 modelviewprojection;
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 lilala;
out vec2 fragTexCoord;
void main() {
    gl_Position = vec4(position/10., 1);
    fragTexCoord = lilala;
}"""

TEXTURE_FRAG = """#version 330 core
uniform sampler2D diffuseMap;
in vec2 fragTexCoord;
out vec4 outColor;
void main() {
    outColor = texture(diffuseMap, fragTexCoord);
}"""


class Control:

    def __init__(self):
        # feel free to move this up in the viewer as per other practicals
        self.shader = Shader(TEXTURE_VERT, TEXTURE_FRAG)

        # triangle and face buffers
        vertices = np.array(((7, 9, 0), (10, 9, 0), (10, 10, 0), (7 , 10, 0)), np.float32)
        faces = np.array(((0, 1, 2), (0, 2, 3)), np.uint32)
        self.vertex_array = VertexArray([vertices, [(0,0), (-1,0), (-1,-1), (0,-1)]], faces)

        # interactive toggles
        self.wrap = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                           GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
        self.filter = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                             (GL.GL_LINEAR, GL.GL_LINEAR),
                             (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])
        self.wrap_mode, self.filter_mode = next(self.wrap), next(self.filter)

        # setup texture and upload it to GPU
        self.textures = {"CLEAR": Texture("control/arrows.png", self.wrap_mode, *self.filter_mode),
                         "UP" : Texture("control/arrowsUP.png", self.wrap_mode, *self.filter_mode),
                         "LEFT" : Texture("control/arrowsRIGHT.png", self.wrap_mode, *self.filter_mode),
                         "RIGHT" : Texture("control/arrowsLEFT.png", self.wrap_mode, *self.filter_mode)
                            }
        self.texture = self.textures["CLEAR"]

    def draw(self, projection, view, model, win=None, **_kwargs):

        GL.glUseProgram(self.shader.glid)

        # projection geometry
        loc = GL.glGetUniformLocation(self.shader.glid, 'modelviewprojection')
        GL.glUniformMatrix4fv(loc, 1, True, projection @ view @ model)

        # texture access setups
        loc = GL.glGetUniformLocation(self.shader.glid, 'diffuseMap')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc, 0)
        self.vertex_array.draw(GL.GL_TRIANGLES)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """

        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_UP:
                self.texture = self.textures["UP"]
            if key == glfw.KEY_LEFT:
                self.texture = self.textures["LEFT"]
            if key == glfw.KEY_RIGHT:
                self.texture = self.textures["RIGHT"]
        else :
            self.texture = self.textures["CLEAR"]

def load_textured(file):
    """ load resources using pyassimp, return list of TexturedMeshes """
    try:
        option = pyassimp.postprocess.aiProcessPreset_TargetRealtime_MaxQuality
        scene = pyassimp.load(file, option)
    except pyassimp.errors.AssimpError:
        print('ERROR: pyassimp unable to load', file)
        return []  # error reading => return empty list

    # Note: embedded textures not supported at the moment
    path = os.path.dirname(file)
    for mat in scene.materials:
        mat.tokens = dict(reversed(list(mat.properties.items())))
        if 'file' in mat.tokens:  # texture file token
            tname = mat.tokens['file'].split('/')[-1].split('\\')[-1]
            # search texture in file's whole subdir since path often screwed up
            tname = [os.path.join(d[0], f) for d in os.walk(path) for f in d[2]
                     if tname.startswith(f) or f.startswith(tname)]
            if tname:
                mat.texture = Texture(tname[0])
            else:
                print('Failed to find texture:', tname)

    # prepare textured mesh
    meshes = []
    for mesh in scene.meshes:
        texture = scene.materials[mesh.materialindex].texture

        # tex coords in raster order: compute 1 - y to follow OpenGL convention
        tex_uv = ((0, 1) + mesh.texturecoords[0][:, :2] * (1, -1)
                  if mesh.texturecoords.size else None)

        # create the textured mesh object from texture, attributes, and indices
        meshes.append(TexturedMesh(texture, [mesh.vertices, tex_uv], index=mesh.faces))

    size = sum((mesh.faces.shape[0] for mesh in scene.meshes))

    pyassimp.release(scene)
    return meshes
