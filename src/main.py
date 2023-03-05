
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "sync-video t")

#from pandac.PandaModules import loadPrcFileData
#loadPrcFileData('', 'load-display tinydisplay')
import random
import sys
import time
import direct.directbase.DirectStart

from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState
from direct.gui.OnscreenText import OnscreenText,TextNode
from direct.gui.OnscreenImage import OnscreenImage

from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, Wait
from direct.interval.LerpInterval import *
from direct.interval.ActorInterval import ActorInterval, LerpAnimInterval
import logging

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
    # pipeline.use_occlusion_maps = True

    base.setBackgroundColor(0.1, 0.1, 0.8, 1)
    base.setFrameRateMeter(True)

    base.cam.setPos(0, -10, 3)
    base.cam.lookAt(0, 0, 0)

    # self.bg = loader.loadSfx('../sounds/pa2.wav')
    # self.bg.play()

    self.oppas =['../models/oppas/oppa1.egg','../models/oppas/oppa2.egg']
    
    self.hidden = NodePath('hidden')
    self.text = TextNode('text')
    self.textNP = aspect2d.attachNewNode(self.text)
    self.textNP.setScale(.08)
    self.textNP.setPos(-.9,0,-.6)
    self.oppacount = 500
    self.setup()
    self.timer=0

    # Light
    alight = AmbientLight('ambientLight')
    alight.setColor(Vec4(.75, .75, 0.75, .5))
    alightNP = render.attachNewNode(alight)

    dlight = DirectionalLight('directionalLight')
    dlight.setDirection(Vec3(1, -1, -1))
    dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
    dlightNP = render.attachNewNode(dlight)

    plight = PointLight('lvl')
    plightNP = render.attachNewNode(plight)
    plight.setColor(Vec4(0.7, 0.7, 0.7, 1))
    plightNP.setPos(0,0,1)

    render.clearLight()
    render.setLight(alightNP)
    render.setLight(dlightNP)
    render.setLight(plightNP)

    self.collisionSetup()

    self.accept('findoppa-into-oppafound', self.oppaFound)
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


  # _____HANDLER_____

  def doExit(self):
    self.cleanup()
    sys.exit(1)

  def doReset(self):
    self.timer=0
    self.oppacount += 10
    self.oppas =['../models/oppas/oppa1.egg','../models/oppas/oppa2.egg','../models/oppas/oppa3.egg']
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

  def collisionSetup(self):
     traverser = CollisionTraverser('collider')
     base.cTrav = traverser
     
     self.collHandEvent = CollisionHandlerEvent()
     self.collHandEvent.addInPattern('%fn-into-%in') 
     traverser.addCollider(self.findoppa, self.collHandEvent)

     traverser.addCollider(self.found, self.collHandEvent)


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
    if inputState.isSet('turnLeft'):  omega =  30.0
    if inputState.isSet('turnRight'): omega = -30.0

    self.player.setAngularMovement(omega)
    self.player.setLinearMovement(speed, True)

  def oppaFound(self, entry):
     print(' you found opppa! time:', self.timer)

  def update(self, task):
    dt = globalClock.getDt()
    self.timer +=dt
    self.processInput(dt)
    self.world.doPhysics(dt, 4, 1./240.)



    # self.playeranim()
    # self.camtask()
 
    # self.camtarg.setPos(self.playerNP.getPos(render))

    for npc in self.npc_list:
      npc.setP(0)
      npc.setR(0)
    self.oppa.setP(0)
    self.oppa.setR(0)

    #move oppas
    if self.timer > 2:
      for oppa in self.activeNPCs:
        force = Vec3(0, 30, 0)
        torque = Vec3(10, 0, 0)
        # force *= 30.0
        # torque *= 10.0

        force = render.getRelativeVector(oppa, force)
        torque = render.getRelativeVector(oppa, torque)

        oppa.node().setActive(True)
        oppa.node().applyCentralForce(force)
        oppa.node().applyTorque(torque)    

        oppa.setCollideMask(BitMask32.bit(0))

    return task.cont
  def playeranim(self):
        self.anim = self.playerM.getCurrentAnim
        # if self.anim!='sweeping':
        #    self.playerM.loop("walk")
    #  if self.playerM.getCurrentAnim!="sweeping":
        self.playerM.play('sweeping') 
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
  def oppaSetup(self):#, oppaModel, anim):
    
    x = random.randrange(0,len(self.oppas))
    a=random.randint(1,4)
    currentoppa = self.oppas[x]
    self.oppas.remove(currentoppa)

    cylinder_shape = BulletCylinderShape(0.5, 1.4, ZUp)
    self.oppa = self.worldNP.attachNewNode(BulletRigidBodyNode('Cylinder'))
    self.oppa.node().setMass(1.0)
    self.oppa.node().addShape(cylinder_shape)
    self.oppa.setPos(random.randrange(-20,20), random.randrange(30,50), 3)
    self.oppa.setHpr(0,0,0)
    self.oppa.setCollideMask(BitMask32.allOn())
    self.world.attachRigidBody(self.oppa.node())

    oppaModel = Actor(currentoppa,
                      {'idle1': f'../models/oppa{x+1}-idle1.egg',
                       'idle2': f'../models/oppa{x+1}-idle2.egg',
                       'idle3': f'../models/oppa{x+1}-idle3.egg',
                       'idle4': f'../models/oppa{x+1}-idle4.egg'})
    # oppaModel = Actor('../models/oppa1.egg',
    #                   {'idle': '../models/oppa1-idle1.egg'})
    # print(f'../models/oppa-idle{a}.egg')
    oppaModel.reparentTo(self.oppa)
    oppaModel.setZ(-1)
    oppaModel.setScale(.8)
    oppaModel.loop('idle3')

    self.found=self.oppa.attachNewNode(CollisionNode('oppafound'))
    sphere =CollisionSphere(0,0,0, 1)
    self.found.node().addSolid(sphere)
    self.found.show()
    
    def showOppa():
      img = currentoppa.replace("egg", "png")
      print('currentoppa',currentoppa)
      self.text.setText('Wanted')
      wanted = OnscreenImage(image=img, pos=(0, 10, 0.0))
      saranghae = OnscreenText(text='oppa saranghae')

      def show():
         wanted.reparentTo(aspect2d)
         saranghae.reparentTo(aspect2d)
         self.text.setText('Wanted')
      def hide():
         wanted.reparentTo(self.hidden)
         saranghae.reparentTo(self.hidden)
         self.text.clearText()
      s=Func(show)
      h=Func(hide)
      imgseq = Sequence(s,Wait(2),h).start()
    showOppa()
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
    lvlgeom =  loader.loadModel('../models/lvlgeom.glb')
    self.lvl.reparentTo(self.worldNP)
    self.make_collision_from_model(lvlgeom,0,0,self.world,lvlgeom.getPos())

    # Box
    shape = BulletBoxShape(Vec3(1.0, 3.0, 0.3))

    np = self.worldNP.attachNewNode(BulletRigidBodyNode('Box'))
    np.node().setMass(50.0)
    np.node().addShape(shape)
    np.setPos(3, 0, 4)
    np.setH(0)
    np.setCollideMask(BitMask32.allOn())

    self.world.attachRigidBody(np.node())

    self.oppaSetup()

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
    self.playerM = Actor('../models/theplayer.egg', {
                            'idle': '../models/theplayer-idle.egg',
                            'sweeping' : '../models/theplayer-sweeping.egg'})
    self.playerM.reparentTo(self.playerNP)
    self.playerM.setZ(-1)

    shovel = loader.loadModel('../models/shovel.glb')
    handl = self.playerM.exposeJoint(None, 'modelRoot', 'hand.l')
    shovel.reparentTo(handl)
    shovel.setP(-90)


    self.findoppa=self.playerNP.attachNewNode(CollisionNode('findoppa'))
    sphere =CollisionSphere(0,1,0, 1)
    self.findoppa.node().addSolid(sphere)
    self.findoppa.show()
    shovel.setPos(-.1,0,0)

    """----------------- NPC creation ------------------"""
    npc_factory = NPCFactory()
    self.npc_list = npc_factory.create(self.world, self.worldNP, self.oppas,self.oppacount)
    self.activeNPCs = []
    for i in self.npc_list:
       if i < (self.oppacount * .2):
          self.activeNPCs.append(i)

    # minn = loader.loadModel('../models/minn.glb')
    # minn.reparentTo(self.worldNP)
    # self.camtarg = self.worldNP.attachNewNode('cam targ')
    # base.cam.setPos(25,0,15)
    # base.cam.setHpr(-90,-45,0)
    # base.cam.setPos(0,-40,30)
    # base.cam.setP(-30)\handr = self
   
    base.cam.reparentTo(self.playerNP)
    base.cam.setY(-10)

    self.playerM.loop('sweeping')
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


