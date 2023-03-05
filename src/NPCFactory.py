import random
from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import ZUp
from panda3d.core import BitMask32



class NPCFactory:
    def __init__(self) -> None:
        pass

    def create(self, world, worldNP, num_npcs = 1) -> list:
        npc_list = []
        for i in range(0, num_npcs):
            cylinder_shape = BulletCylinderShape(0.5, 1.4, ZUp)
            npc = worldNP.attachNewNode(BulletRigidBodyNode('Cylinder'))
            npc.node().setMass(500.0)
            npc.node().addShape(cylinder_shape)
            npc.setPos(random.randrange(-20,20), random.randrange(0,50), 3)
            npc.setHpr(0, 0, 0)
            npc.setCollideMask(BitMask32.allOn())
            world.attachRigidBody(npc.node())
            npc_list.append(npc)
        return npc_list

    
