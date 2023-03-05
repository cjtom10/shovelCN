import random
from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import ZUp
from panda3d.core import BitMask32

from direct.actor.Actor import Actor


class NPCFactory:
    def __init__(self) -> None:
        pass

    def create(self, world, worldNP, oppaList,num_npcs = 1 ) -> list:
        npc_list = []
        for i in range(0, num_npcs):
            cylinder_shape = BulletCylinderShape(0.5, 1.4, ZUp)
            npc = worldNP.attachNewNode(BulletRigidBodyNode('Cylinder'))
            npc.node().setMass(50.0)
            npc.node().addShape(cylinder_shape)
            npc.setPos(random.randrange(-15,10), random.randrange(10,45), 3)
            h=random.randint(-180,180)
            npc.setHpr(h,0,0)

            npc.setCollideMask(BitMask32.allOn())
            world.attachRigidBody(npc.node())
            npc_list.append(npc)
            no = random.randrange(0,len(oppaList))
            oppaModel = Actor(oppaList[no],
                        {'idle1': f'../models/oppa{no+1}-idle1.egg',
                       'idle2': f'../models/oppa{no+1}-idle2.egg',
                       'idle3': f'../models/oppa{no+1}-idle3.egg',
                       'idle4': f'../models/oppa{no+1}-idle4.egg'})
            # oppaModel = Actor('../models/oppa1.egg',
            #                   {'idle': '../models/oppa1-idle1.egg'})
            # print(f'../models/oppa-idle{a}.egg')
            oppaModel.reparentTo(npc)
            oppaModel.setZ(-1)
            oppaModel.setScale(.8)
            oppaModel.loop('idle3')
            
        return npc_list



    
