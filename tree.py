from loader import loadColorMesh
from node import Node

class Tree:
	"""
	a tree in the 3d scene
	"""
	def __init__(self, x, y, z):
		"""
		init the tree and put it in the correct place
		"""
		self.node = Node()
		self.meshes = loadColorMesh("tree/tree.obj", )
		for mesh in self.meshes:
			self.node.add(mesh)