import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for

import numpy as np

class VertexArray:
    """
    An object represented as a vertex
    """
    def __init__(self, attributes, index=None):
        """
        The object is created with a set of atributes for each vertex and an
        optional index array
        """
        self.glid = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.glid)

        self.buffer_size = len(attributes)
        self.index_size = 0
        if index is not None:
            self.buffer_size += 1
            self.index_size = index.size

        self.buffers = GL.glGenBuffers(self.buffer_size)

        for layout_index, buffer_data in enumerate(attributes):
            buffer_data = np.array(buffer_data, np.float32, copy=False)
            GL.glEnableVertexAttribArray(layout_index)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[layout_index])
            GL.glBufferData(GL.GL_ARRAY_BUFFER, buffer_data, GL.GL_STATIC_DRAW)
            GL.glVertexAttribPointer(layout_index, buffer_data.shape[1], GL.GL_FLOAT, False, 0, None)

        if index is not None:
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffers[-1])
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, index, GL.GL_STATIC_DRAW)

        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def draw(self, primitive):
        """
        Draws the object
        """
        GL.glBindVertexArray(self.glid)
        GL.glDrawElements(primitive, self.index_size, GL.GL_UNSIGNED_INT, None)
        GL.glBindVertexArray(0)

    def __del__(self):
        """
        Destroy the object
        """
        GL.glDeleteVertexArrays(1, [self.glid])
        GL.glDeleteBuffers(self.buffer_size, self.buffers)