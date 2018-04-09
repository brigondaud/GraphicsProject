from VertexArray import VertexArray
import OpenGL.GL as GL

import numpy as np

class ColorMesh:
    """
    Stores a mesh with color drawing
    """

    def __init__(self, attributes, faces):
        """
        The mesh is created with attributes and face attributes
        """
        self.attributes = attributes
        self.faces = faces
        self.vertexArray = VertexArray(attributes, faces)

    def draw(self, projection, view, model, color_shader=None, color=(1, 1, 1, 1), **param):
        """
        Draws the color mesh
        """
        GL.glUseProgram(color_shader.glid)

        #Passing rotation matrix as uniform
        projection_location = GL.glGetUniformLocation(color_shader.glid, "projection")
        view_location = GL.glGetUniformLocation(color_shader.glid, "view")
        model_location = GL.glGetUniformLocation(color_shader.glid, "model")

        GL.glUniformMatrix4fv(projection_location, 1, True, projection, 1)
        GL.glUniformMatrix4fv(view_location, 1, True, view, 1)
        GL.glUniformMatrix4fv(model_location, 1, True, model, 1)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        GL.glBindVertexArray(self.vertexArray.glid)
        GL.glDrawElements(GL.GL_TRIANGLES, self.vertexArray.index_size, GL.GL_UNSIGNED_INT, None)
        GL.glBindVertexArray(0)

    def __del__(self):
        """
        Destroys the color mesh
        """
        #self.vertexArray.__del__()