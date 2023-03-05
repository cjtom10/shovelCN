
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "sync-video t")

#from pandac.PandaModules import loadPrcFileData
#loadPrcFileData('', 'load-display tinydisplay')

import sys
import time
import direct.directbase.DirectStart

from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState

import simplepbr
import gltf

from panda3d.core import *
# from panda3d.core import AmbientLight
# from panda3d.core import DirectionalLight
# from panda3d.core import Vec3
# from panda3d.core import Vec4
# from panda3d.core import Point3
# from panda3d.core import TransformState
# from panda3d.core import BitMask32
# from panda3d.core import Filename
# from panda3d.core import PNMImage

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletHeightfieldShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import ZUp

from NPCFactory import NPCFactory

class Game(DirectObject):

  def __init__(self):
    gltf.patch_loader(loader)
    pipeline = simplepbr.init()
    pipeline.use_normal_maps = True
    pipeline.use_occlusion_maps = True

    base.setBackgroundColor(0.1, 0.1, 0.8, 1)
    base.setFrameRateMeter(True)

    base.cam.setPos(0, -20, 4)
    base.cam.lookAt(0, 0, 0)
    self.lerpCam=None

    # Light
    alight = AmbientLight('ambientLight')
    alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
    alightNP = render.attachNewNode(alight)

    dlight = DirectionalLight('directionalLight')
    dlight.setDirection(Vec3(1, 1, -1))
    dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
    dlightNP = render.attachNewNode(dlight)

    render.clearLight()
    render.setLight(alightNP)
    render.setLight(dlightNP)

    # Input
    self.accept('escape', self.doExit)
    self.accept('r', self.doReset)
    self.accept('f1', self.toggleWireframe)
    self.accept('f2', self.toggleTexture)
    self.accept('f3', self.toggleDebug)
    self.accept('f5', self.doScreenshot)

    #self.accept('space', self.doJump)
    #self.accept('c', self.doCrouch)

    inputState.watchWithModifiers('forward', 'w')
    inputState.watchWithModifiers('left', 'a')
    inputState.watchWithModifiers('reverse', 's')
    inputState.watchWithModifiers('right', 'd')
    inputState.watchWithModifiers('turnLeft', 'q')
    inputState.watchWithModifiers('turnRight', 'e')

    # Task
    taskMgr.add(self.update, 'updateWorld')

    # Physics
    self.setup()

  # _____HANDLER_____

  def doExit(self):
    self.cleanup()
    sys.exit(1)

  def doReset(self):
    self.cleanup()
    self.setup()

  def toggleWireframe(self):
    base.toggleWireframe()

  def toggleTexture(self):
    base.toggleTexture()

  def toggleDebug(self):
    if self.debugNP.isHidden():
      self.debugNP.show()
    else:
      self.debugNP.hide()

  def doScreenshot(self):
    base.screenshot('Bullet')

  #def doJump(self):
  #  self.player.setMaxJumpHeight(5.0)
  #  self.player.setJumpSpeed(8.0)
  #  self.player.doJump()

  #def doCrouch(self):
  #  self.crouching = not self.crouching
  #  sz = self.crouching and 0.6 or 1.0

  #  self.playerNP2.setScale(Vec3(1, 1, sz))

  # ____TASK___

  def processInput(self, dt):
    speed = Vec3(0, 0, 0)
    omega = 0.0
    speed.setY( 2.0)
    # if inputState.isSet('forward'): speed.setY( 2.0)
    if inputState.isSet('reverse'): speed.setY(-2.0)
    if inputState.isSet('left'):    speed.setX(-2.0)
    if inputState.isSet('right'):   speed.setX( 2.0)
    if inputState.isSet('turnLeft'):  omega =  120.0
    if inputState.isSet('turnRight'): omega = -120.0

    self.player.setAngularMovement(omega)
    self.player.setLinearMovement(speed, True)

  def update(self, task):
    dt = globalClock.getDt()

    self.processInput(dt)
    self.world.doPhysics(dt, 4, 1./240.)

    # self.camtask()
    # self.camtarg.setPos(self.playerNP.getPos(render))

    return task.cont
  # 
  def camtask(self):
    dis = (self.playerNP.getPos(render) - self.camtarg.getPos(render))
    if dis > 2 and self.lerpCam == None:

      self.lerpCam = Sequence(LerpPosInterval(self.camtarg, delaytime, mp)).start()
      # self.lerpCam.start()
      return #task.contmovetarget

    if dis <2 and self.lerpCam != None: #and self.isIdle == True:
            
            self.lerpCam.pause()
            self.lerpCam = None
            return #task.cont
        
    #offset camera moveme
  # def wait(self, t):


  def cleanup(self):
    self.world = None
    self.worldNP.removeNode()

  def pplSetup(self):
    r
  def setup(self):
    self.worldNP = render.attachNewNode('World')

    # World
    self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
    self.debugNP.show()

    self.world = BulletWorld()
    self.world.setGravity(Vec3(0, 0, -9.81))
    self.world.setDebugNode(self.debugNP.node())

    # Ground
    shape = BulletPlaneShape(Vec3(0, 0, 1), 0)

    #img = PNMImage(Filename('models/elevation2.png'))
    #shape = BulletHeightfieldShape(img, 1.0, ZUp)

    np = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
    np.node().addShape(shape)
    np.setPos(0, 0, -1)
    np.setCollideMask(BitMask32.allOn())

    self.world.attachRigidBody(np.node())

    self.lvl = loader.loadModel('../models/lvl.glb')
    self.lvl.reparentTo(self.worldNP)
    self.make_collision_from_model(self.lvl,0,0,self.world,self.lvl.getPos())

    # Box
    shape = BulletBoxShape(Vec3(1.0, 3.0, 0.3))

    np = self.worldNP.attachNewNode(BulletRigidBodyNode('Box'))
    np.node().setMass(50.0)
    np.node().addShape(shape)
    np.setPos(3, 0, 4)
    np.setH(0)
    np.setCollideMask(BitMask32.allOn())

    self.world.attachRigidBody(np.node())

    # Character
    h = 1.75
    w = 0.4
    shape = BulletCapsuleShape(w, h - 2 * w, ZUp)

    self.player = BulletCharacterControllerNode(shape, 0.4, 'Player')
    # self.player.setMass(20.0)
    # self.player.setMaxSlope(45.0)
    # self.player.setGravity(9.81)
    self.playerNP = self.worldNP.attachNewNode(self.player)
    self.playerNP.setPos(-2, 10, 10)
    # self.playerNP.setH(-90)
    self.playerNP.setCollideMask(BitMask32.allOn())
    self.world.attachCharacter(self.player)

    """----------------- NPC creation ------------------"""
    npc_factory = NPCFactory()
    npc_factory.create(self.world, self.worldNP, 500)

    minn = loader.loadModel('../models/minn.glb')
    minn.reparentTo(self.worldNP)
    # self.camtarg = self.worldNP.attachNewNode('cam targ')
    # base.cam.setPos(25,0,15)
    # base.cam.setHpr(-90,-45,0)
    # base.cam.setPos(0,-40,30)
    # base.cam.setP(-30)
    base.cam.reparentTo(self.playerNP)
    base.cam.setY(-10)
    # base.cam.reparentTo(self.camtarg)
    #self.crouching = False

    #self.player = node # For player control
    #self.playerNP2 = np
  def make_collision_from_model(self, input_model, node_number, mass, world, target_pos,mask = BitMask32.bit(0),name ='input_model_tri_mesh'):
                # tristrip generation from static models
                # generic tri-strip collision generator begins
                geom_nodes = input_model.find_all_matches('**/+GeomNode')
                geom_nodes = geom_nodes.get_path(node_number).node()
                # print(geom_nodes)
                geom_target = geom_nodes.get_geom(0)
                # print(geom_target)
                output_bullet_mesh = BulletTriangleMesh()
                output_bullet_mesh.add_geom(geom_target)
                tri_shape = BulletTriangleMeshShape(output_bullet_mesh, dynamic=False)
                print(output_bullet_mesh)

                body = BulletRigidBodyNode(name)
                np = render.attach_new_node(body)
                np.node().add_shape(tri_shape)
                np.node().set_mass(mass)
                np.node().set_friction(0.01)
                np.set_pos(target_pos)
                np.set_scale(1)
                # np.set_h(180)
                # np.set_p(180)
                # np.set_r(180)
                # np.set_collide_mask(BitMask32.allOn())
                np.set_collide_mask(mask)
                
                world.attach_rigid_body(np.node())
    #self.playerNP = Actor('models/ralph/ralph.egg', {
    #                      'run' : 'models/ralph/ralph-run.egg',
    #                      'walk' : 'models/ralph/ralph-walk.egg',
    #                      'jump' : 'models/ralph/ralph-jump.egg'})
    #self.playerNP.reparentTo(np)
    #self.playerNP.setScale(0.3048) # 1ft = 0.3048m
    #self.playerNP.setH(180)
    #self.playerNP.setPos(0, 0, -1)

game = Game()
run()


