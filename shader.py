# Python built-in modules
import os                           # os function, i.e. checking file status

import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args


# ------------  Simple color shaders ------------------------------------------
COLOR_VERT = """#version 330 core
uniform vec3 inColor;
uniform mat4 Mat;
layout(location = 0) in vec3 position;
out vec3 color;
void main() {
    gl_Position = Mat * vec4(position, 1);
    color = inColor;
}"""

COLOR_FRAG = """#version 330 core
in vec3 color;
out vec4 outColor;
void main() {
    outColor = vec4(color, 1);

}"""


LAMBERTIAN_VERT = """#version 330 core
uniform vec3 inColor;
uniform mat4 Mat;
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 inNormal;
out vec3 color;
out vec3 normal;
void main() {
    gl_Position = Mat * vec4(position, 1);
    color = inColor;
    normal = mat3(transpose(inverse(Mat))) * inNormal;
}"""

LAMBERTIAN_FRAG = """#version 330 core
in vec3 color;
in vec3 normal;
out vec4 outColor;
void main() {
    outColor = vec4(color * dot(normalize(normal), vec3(0, -1, -0.25)), 1);

}"""


# ------------ low level OpenGL object wrappers ----------------------------
class Shader:
    """ Helper class to create and automatically destroy shader program """
    @staticmethod
    def _compile_shader(src, shader_type):
        src = open(src, 'r').read() if os.path.exists(src) else src
        src = src.decode('ascii') if isinstance(src, bytes) else src
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, src)
        GL.glCompileShader(shader)
        status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
        src = ('%3d: %s' % (i+1, l) for i, l in enumerate(src.splitlines()))
        if not status:
            log = GL.glGetShaderInfoLog(shader).decode('ascii')
            GL.glDeleteShader(shader)
            src = '\n'.join(src)
            print('Compile failed for %s\n%s\n%s' % (shader_type, log, src))
            return None
        return shader

    def __init__(self, vertex_source, fragment_source):
        """ Shader can be initialized with raw strings or source file names """
        self.glid = None
        vert = self._compile_shader(vertex_source, GL.GL_VERTEX_SHADER)
        frag = self._compile_shader(fragment_source, GL.GL_FRAGMENT_SHADER)
        if vert and frag:
            self.glid = GL.glCreateProgram()  # pylint: disable=E1111
            GL.glAttachShader(self.glid, vert)
            GL.glAttachShader(self.glid, frag)
            GL.glLinkProgram(self.glid)
            GL.glDeleteShader(vert)
            GL.glDeleteShader(frag)
            status = GL.glGetProgramiv(self.glid, GL.GL_LINK_STATUS)
            if not status:
                print(GL.glGetProgramInfoLog(self.glid).decode('ascii'))
                GL.glDeleteProgram(self.glid)
                self.glid = None
    def __del__(self):
        GL.glUseProgram(0)
        if self.glid:                      # if this is a valid shader object
            GL.glDeleteProgram(self.glid)  # object dies => destroy GL object
