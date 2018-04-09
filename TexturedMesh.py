import OpenGL.GL as GL              # standard Python OpenGL wrapper

import numpy as np
from Shader import Shader
from VertexArray import VertexArray

UV_VERT = """#version 330 core
uniform mat4 modelviewprojection;
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 tex_uv;
out vec2 uv_pos;
void main() {
    gl_Position = modelviewprojection * vec4(position, 1);
    uv_pos = tex_uv;
}"""

UV_FRAG = """#version 330 core
uniform sampler2D diffuseMap;
in vec2 uv_pos;
out vec4 outColor;
void main() {
    outColor = texture(diffuseMap, uv_pos);
}"""


class TexturedMesh:
    """ Simple first textured object """

    #Case of use: TexturedMesh(texture, [mesh.vertices, tex_uv], mesh.faces))
    def __init__(self, texture, attributes, indexes):
        self.shader = Shader(UV_VERT, UV_FRAG)

        # triangle and face buffers
        self.vertex_array = VertexArray(attributes, indexes)

        self.texture = texture

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