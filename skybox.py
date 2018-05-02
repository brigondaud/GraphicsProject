import OpenGL.GL as GL
from PIL import Image

from texture import *
from shader import Shader
from loader import load

VERT = """#version 330 core
layout (location = 0) in vec3 aPos;

out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view;

void main()
{
    TexCoords = aPos;
    mat4 m = projection * view;
    m[3][0] = 0;
    m[3][1] = 0;
    m[3][2] = 0;
    m[3][3] = 1;

    gl_Position = m * vec4(aPos, 1);
}"""

FRAG = """#version 330 core
out vec4 FragColor;

in vec3 TexCoords;

uniform samplerCube skybox;

void main()
{
    FragColor = texture(skybox, TexCoords);
}"""


RESOLUTION = 512

# SKYBOX_VERT_SHADER = """#version 330 core
# varying vec4 position;
# uniform samplerCube skybox;
# void main()
# {
#     gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
#     position = gl_ModelViewMatrix * gl_Vertex;
#     position.y *= -1; // put sun at top
#     position.x *= -1; // keep coordinate frame right handed
# }
# """
# SKYBOX_FRAG_SHADER = """#version 330 core
# uniform samplerCube skybox;
# in vec4 position;
# out vec4 outColor;
# void main()
# {
#     vec4 box_color = vec4(textureCube(skybox, position.xyz), 1);
# }
# """
#
# TEXTURE_FRAG = """#version 330 core
# uniform sampler2D diffuseMap;
# in vec2 fragTexCoord;
# out vec4 outColor;
# void main() {
#     outColor = texture(diffuseMap, fragTexCoord);
# }"""
#
# TEXTMESH_VERT = """#version 330 core
# uniform mat4 modelviewprojection;
# layout(location = 0) in vec3 position;
# layout(location = 1) in vec2 tex_uv;
# out vec2 fragTexCoord;
# void main() {
#     gl_Position = modelviewprojection * vec4(position, 1);
#     fragTexCoord = tex_uv;
# }"""

class Skybox:
    """
    Skybox for the scene.
    """
    def __init__(self, file):
        """
        The skybox is made of a cube without depth effect.
        """

        self.shader = Shader(VERT, FRAG)
        
        self.vertexArray = load("skybox/skybox.obj")[0]

        original =  Image.open(file).resize((4*RESOLUTION,3*RESOLUTION))
        self.texture_id = GL.glGenTextures(1)

        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.texture_id)

        GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X, 0, GL.GL_RGB, RESOLUTION, RESOLUTION, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE,
        original.crop((RESOLUTION*2, RESOLUTION, RESOLUTION*3, RESOLUTION*2)).tobytes())
        GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_X, 0, GL.GL_RGB, RESOLUTION, RESOLUTION, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE,
        original.crop((0, RESOLUTION, RESOLUTION, RESOLUTION*2)).tobytes())
        GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_Y, 0, GL.GL_RGB, RESOLUTION, RESOLUTION, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE,
         original.crop((RESOLUTION, 0, RESOLUTION*2, RESOLUTION)).tobytes())
        GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, 0, GL.GL_RGB, RESOLUTION, RESOLUTION, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE,
         original.crop((RESOLUTION, RESOLUTION*2, RESOLUTION*2, RESOLUTION*3)).tobytes())
        GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_Z, 0, GL.GL_RGB, RESOLUTION, RESOLUTION, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE,
         original.crop((RESOLUTION, RESOLUTION, RESOLUTION*2, RESOLUTION*2)).tobytes())
        GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, 0, GL.GL_RGB, RESOLUTION, RESOLUTION, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE,
         original.crop((RESOLUTION*3, RESOLUTION, RESOLUTION*4, RESOLUTION*2)).tobytes())
        print (2)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)

    def drawskybox(self, projection, view):
        """
        Draws the skybow on the background
        """

        GL.glDepthMask(False)
        GL.glUseProgram(self.shader.glid)
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.shader.glid, 'projection'), 1, True, projection)
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.shader.glid, 'view'), 1, True, view)

        # texture access setups
        loc = GL.glGetUniformLocation(self.shader.glid, 'skybox')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.texture_id)
        GL.glUniform1i(loc, 0)

        self.vertexArray.draw()


        GL.glDepthMask(True)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, 0)
        GL.glUseProgram(0)



# import shader
# from OpenGL.GL import *
# import numpy
# from math import sqrt
#
# class SkyBoxShaderProgram(shader.ShaderProgram):
#     def __init__(self):
#         shader.ShaderProgram.__init__(self)
#         self.vertex_shader = """
# varying vec4 position;
# uniform samplerCube skybox;
# uniform float eye_shift;
# void main()
# {
#     gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
#     vec4 eye_position_in_camera = vec4(-eye_shift, 0, 0, 0); // compensate for parallax asymmetric frustum shift for stereo 3D
#     position = gl_ModelViewMatrix * gl_Vertex - eye_position_in_camera;
#     position.y *= -1; // put sun at top
#     position.x *= -1; // keep coordinate frame right handed
# }
# """
#         self.fragment_shader = """
# varying vec4 position;
# uniform samplerCube skybox;
# uniform float eye_shift;
# void main()
# {
#     vec4 box_color = textureCube(skybox, position.xyz);
#     gl_FragColor = box_color;
# }
# """
#
#     def __enter__(self):
#         shader.ShaderProgram.__enter__(self)
#         self.skybox = glGetUniformLocation(self.shader_program, "skybox")
#         self.eye_shift = glGetUniformLocation(self.shader_program, "eye_shift")
#
#
# def fname_to_tex(file_name):
#         return Image.open(file).rotate(180).transpose(Image.FLIP_LEFT_RIGHT).resize((4*RESOLUTION,3*RESOLUTION)).crop((RESOLUTION, RESOLUTION, RESOLUTION*2, RESOLUTION*2)).tobytes()
#
# class SkyBox:
#     def __init__(self):
#         self.is_initialized = False
#         self.shader = SkyBoxShaderProgram()
#
#     def init_gl(self):
#         if self.is_initialized:
#             return
#         self.texture_id = glGenTextures(1)
#         glEnable(GL_TEXTURE_CUBE_MAP)
#         glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_id)
#         # Define all 6 faces
#         glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
#         if True:
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X, 0, GL_RGBA8, img.width(), img.height(),
#                          0, GL_RGBA, GL_UNSIGNED_BYTE, fname_to_tex("skybox/miramar_ft.tif"))
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_X, 0, GL_RGBA8, img.width(), img.height(),
#                          0, GL_RGBA, GL_UNSIGNED_BYTE, fname_to_tex("skybox/miramar_bk.tif"))
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_Y, 0, GL_RGBA8, img.width(), img.height(),
#                          0, GL_RGBA, GL_UNSIGNED_BYTE, fname_to_tex("skybox/miramar_dn.tif"))
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, 0, GL_RGBA8, img.width(), img.height(),
#                          0, GL_RGBA, GL_UNSIGNED_BYTE, fname_to_tex("skybox/miramar_up.tif"))
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_Z, 0, GL_RGBA8, img.width(), img.height(),
#                          0, GL_RGBA, GL_UNSIGNED_BYTE, fname_to_tex("skybox/miramar_rt.tif"))
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, 0, GL_RGBA8, img.width(), img.height(),
#                          0, GL_RGBA, GL_UNSIGNED_BYTE, fname_to_tex("skybox/miramar_lf.tif"))
#         else:
#             test_img = numpy.array(256 * [50,50,128,255], 'uint8')
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X, 0, GL_RGBA8, 8, 8, 0, GL_RGBA, GL_UNSIGNED_BYTE, test_img)
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_X, 0, GL_RGBA8, 8, 8, 0, GL_RGBA, GL_UNSIGNED_BYTE, test_img)
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_Y, 0, GL_RGBA8, 8, 8, 0, GL_RGBA, GL_UNSIGNED_BYTE, test_img)
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, 0, GL_RGBA8, 8, 8, 0, GL_RGBA, GL_UNSIGNED_BYTE, test_img)
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_Z, 0, GL_RGBA8, 8, 8, 0, GL_RGBA, GL_UNSIGNED_BYTE, test_img)
#             glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, 0, GL_RGBA8, 8, 8, 0, GL_RGBA, GL_UNSIGNED_BYTE, test_img)
#         glDisable(GL_TEXTURE_CUBE_MAP)
#         self.shader.init_gl()
#         self.is_initialized = True
#
#     def paint_gl(self, camera):
#         if not self.is_initialized:
#             self.init_gl()
#         # print "painting skybox"
#         glPushAttrib(GL_TEXTURE_BIT | GL_ENABLE_BIT | GL_TRANSFORM_BIT | GL_DEPTH_BUFFER_BIT)
#         glDisable(GL_DEPTH_TEST)
#         glDepthMask(False)
#         glEnable(GL_TEXTURE_CUBE_MAP)
#         glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_id)
#         glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_REPEAT)
#         glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_REPEAT)
#         glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_REPEAT)
#         glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
#         glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
#         # Construct a giant cube, almost as big as possible without clipping
#         max_coord = 1.0 / sqrt(2.0) * 0.5 * camera.zFar
#         m = max_coord
#         with self.shader:
#             glUniform1i(self.shader.skybox, 0)
#             glUniform1f(self.shader.eye_shift, camera.eye_shift_in_ground)
#             glBegin(GL_QUADS)
#             # front
#             glVertex3f( m,  m, -m)
#             glVertex3f(-m,  m, -m)
#             glVertex3f(-m, -m, -m)
#             glVertex3f( m, -m, -m)
#             # back
#             glVertex3f( m,  m,  m)
#             glVertex3f( m, -m,  m)
#             glVertex3f(-m, -m,  m)
#             glVertex3f(-m,  m,  m)
#             # right
#             glVertex3f( m,  m,  m)
#             glVertex3f( m,  m, -m)
#             glVertex3f( m, -m, -m)
#             glVertex3f( m, -m,  m)
#             # left
#             glVertex3f(-m,  m,  m)
#             glVertex3f(-m, -m,  m)
#             glVertex3f(-m, -m, -m)
#             glVertex3f(-m,  m, -m)
#             # down
#             glVertex3f( m, -m,  m)
#             glVertex3f( m, -m, -m)
#             glVertex3f(-m, -m, -m)
#             glVertex3f(-m, -m,  m)
#             # up
#             glVertex3f( m,  m,  m)
#             glVertex3f(-m,  m,  m)
#             glVertex3f(-m,  m, -m)
#             glVertex3f( m,  m, -m)
#             #
#             glEnd()
#         glPopAttrib()
