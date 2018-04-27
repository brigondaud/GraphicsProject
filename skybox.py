from TexturedMesh import TexturedMesh
from Texture import Texture
from load import load_textured

class Skybox:
    """
    Skybox for the scene.
    """
    def __init__(self):
        """
        The skybox is made of a cube without depth effect.
        """
        self.meshes = load_textured("skybox/skybox.obj")

    def getMeshes(self):
        """
        return the meshes for viewer
        """
        return self.meshes