from TexturedMesh import TexturedMesh
from Texture import Texture

class Skybox:
    """
    Skybox for the scene.
    """
    def __init__(self):
        """
        The skybox is made of a cube without depth effect.
        """
        self.texture = Texture("skyboxTexture/")