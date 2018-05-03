import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from shader import Shader


class VertexArray:
    def __init__(self, attributes, index=None):
        # attributes is a list of np.float32 arrays, index an optional np.uint32 array
        self.glid = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.glid)
        self.buffers = GL.glGenBuffers(len(attributes) + (index is not None))
        for layout_index, buffer_data in enumerate(attributes):
            buffer_data = np.array(buffer_data, np.float32, copy=False)
            GL.glEnableVertexAttribArray(layout_index)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[layout_index])
            GL.glBufferData(GL.GL_ARRAY_BUFFER, buffer_data, GL.GL_STATIC_DRAW)
            GL.glVertexAttribPointer(layout_index, buffer_data.shape[1], GL.GL_FLOAT, False, 0, None)

        self.size = self.shape = None
        if index is not None :
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffers[-1])
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, index, GL.GL_STATIC_DRAW)
            self.size = index.size
        else :
            self.shape = attributes[0].shape[0]

        # cleanup and unbind so no accidental subsequent state update
        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def draw(self, primitive=GL.GL_TRIANGLES):
        GL.glBindVertexArray(self.glid)  # activate our vertex array
        if self.size is not None:
            GL.glDrawElements(primitive, self.size, GL.GL_UNSIGNED_INT, None)
        else:
            GL.glDrawArrays(primitive, 0, self.shape)

    def __del__(self):
        GL.glDeleteVertexArrays(1, [self.glid])
        GL.glDeleteBuffers(1, self.buffers)


COLOR_VERT = """#version 330 core
uniform mat4 Mat;
uniform vec3 inColor;

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

class ColorMesh (VertexArray):
    
    def __init__(self, attributes, color, index=None):
        super().__init__(attributes, index)
        self.shader = Shader(COLOR_VERT, COLOR_FRAG)
        self.color = color

    def draw(self, projection, view, model, **param):
        GL.glUseProgram(self.shader.glid)
        matrix_location = GL.glGetUniformLocation(self.shader.glid, 'Mat')
        GL.glUniformMatrix4fv(matrix_location, 1, True, projection @ view @ model)
        loc = GL.glGetUniformLocation(self.shader.glid, 'inColor')
        GL.glUniform3fv(loc, 1, self.color)
        super().draw()

class PhongMesh (ColorMesh):
    def __init__(self, attributes, index=None):
        super().__init__(attributes, index)
        self.shader = Shader(LAMBERTIAN_VERT, LAMBERTIAN_FRAG)

    def draw(self, projection, view, model, color=(1, 1, 1), **param):
        super().draw(projection, view, model, self.shader, color, **param)
