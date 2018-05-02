from mesh import *

class SimpleTriangle (ColorMesh):
    """Hello triangle object"""

    def __init__(self):
        # triangle position buffer
        position = np.array(((0, .5, 0), (.5, -.5, 0), (-.5, -.5, 0)), 'f')
        color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'f')
        super().__init__([position, color])


class PyramideIndex(ColorMesh):

    def __init__(self):
        # triangle position buffer
        position = np.array(((0.5, 0, 0.5), (-0.5, 0, 0.5), (-0.5, 0, -0.5), (0.5, 0, -0.5), (0, 1, 0)), np.float32)
        color = np.array(((245, 51, 255), (69, 51, 255), (255, 238, 51), (255, 147, 51), (51, 255, 121)), np.float32)/255
        index = np.array((0, 4, 1, 1, 4, 2, 2, 4, 3, 3, 4, 0, 0, 1, 3, 1, 2, 3), np.uint32)
        position -= (0, 0, 1)
        super().__init__([position, color], index)


class PyramideVertex(ColorMesh):

    def __init__(self):
        # triangle position buffer
        position = np.array(((0.5, 0, 0.5), (-0.5, 0, 0.5), (-0.5, 0, -0.5), (0.5, 0, -0.5), (0, 1, 0)), np.float32)
        color = np.repeat(np.array(((245, 51, 255), (69, 51, 255), (255, 238, 51), (255, 147, 51), (51, 255, 121), (51, 255, 121)), np.float32)/255, 3, axis=0)
        index = np.array((0, 4, 1, 1, 4, 2, 2, 4, 3, 3, 4, 0, 0, 1, 3, 1, 2, 3), np.uint32)
        position = position[index]
        position += (0, 0, 1)
        super().__init__([position, color])

class Cylinder(PhongMesh):

    def __init__(self, nb_division=20):
        # triangle position buffer
        position = [[0, 0, 0], [0, 0, 1]]
        normals = [[0.5, 0.5, 0], [0.5, 0.5, 1]]
        index = []
        angle = np.linspace(0, np.pi*2, nb_division + 1)
        for i in range(nb_division):
            x, y = np.cos(angle[i]), np.sin(angle[i])
            xp, yp = (x+1)/2, (y+1)/2
            position.append([x, y, 1]) # Point of the lower base
            position.append([x, y, 1]) # Point of the lower base
            position.append([x, y, 0])  # Point of the upper base
            position.append([x, y, 0])  # Point of the upper base
            normals.append([x, y, 0.5])
            normals.append([0.5, 0.5, 1])
            normals.append([x, y, 0.5])
            normals.append([0.5, 0.5, 0])
            x0 = i*4 + 2
            x0p = i*4 + 3
            x1 = ((i + 1)%nb_division)*4 + 2
            x1p = ((i + 1)%nb_division)*4 + 3
            x2 = i*4 + 4
            x2p = i*4 + 5
            x3 = ((i + 1)%nb_division)*4 + 4
            x3p = ((i + 1)%nb_division)*4 + 5
            index.extend([x0p, x1p, 1]) # Triangle of upper base
            index.extend([x0, x2, x1]) # First side triangle
            index.extend([x1, x2, x3]) # Second side triangle
            index.extend([0, x3p, x2p]) # Triangle of lower base

        positions = np.array(position, np.float32)
        normals = np.array(normals, np.float32)
        index = np.array(index, np.uint32)
        super().__init__([positions, normals], index)

        #self.shader = Shader(COLOR_VERT,COLOR_FRAG)
