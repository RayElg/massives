#Imports
from cffi import FFI
import ctypes
import pygame
import json
import math

#Init
clock = pygame.time.Clock()
window = pygame.display.set_mode((1200,600),0,32)

zoom = 8
offset_x = -1800
offset_x_vel = 0
offset_y = -1600
offset_y_vel = 0
ticksPerLoop = 1

#Declare classes for return/input from tick function
class Massive(ctypes.Structure):
    _fields_ = [("mass", ctypes.c_double), ("vel_x", ctypes.c_double), ("vel_y", ctypes.c_double), ("pos_x", ctypes.c_double), ("pos_y", ctypes.c_double), ("radius", ctypes.c_uint32),]
    
    def __str__(self):
        return "Pos: ({},{}), vel: ({}, {}), mass: {}, radius: {}".format(self.pos_x, self.pos_y, self.vel_x, self.vel_y, self.mass, self.radius)

    def dict_of(self):
        return {"mass": self.mass, "vel_x": self.vel_x, "vel_y": self.vel_y, "pos_x": self.pos_x, "pos_y": self.pos_y, "radius": self.radius}

    def setAttributes(self, dic):
        self.mass = dic["mass"]
        self.vel_x = dic["vel_x"]
        self.vel_y = dic["vel_y"]
        self.pos_x = dic["pos_x"]
        self.pos_y = dic["pos_y"]
        self.radius = dic["radius"]  

class Result(ctypes.Structure):
    _fields_ = [("pointer", ctypes.POINTER(Massive)), ("len", ctypes.c_uint64), ("is_broken", ctypes.c_bool)]


lib = ctypes.cdll.LoadLibrary("./target/release/massives.dll") #Initialise dll, function
lib.tick.argtypes = (ctypes.POINTER(Massive), ctypes.c_uint64)
lib.tick.restype = Result


def loadMassives(): #Read in json file, construct Massives
    massives = []
    with open("./massives.json") as f:
        jsonDict = json.load(f)
    massiveDicts = jsonDict["massives"]

    for i in massiveDicts:
        massive = Massive()
        massive.setAttributes(i)
        massives = massives + [massive]


    arr = (Massive * len(massives))(*massives)

    return lib.tick(arr, len(massives))

ticked = loadMassives() #Initial loading of massives

#Get fields from Result
massives = ticked.pointer
curLen = ticked.len




# Game loop
while True:
    
    #Move viewpoint
    offset_x = offset_x = offset_x + offset_x_vel
    offset_y = offset_y = offset_y + offset_y_vel
    

    #Draw
    window.fill((18,18,18))
    for j in range(curLen):
        pygame.draw.circle(window, (255,255,255), ((massives[j].pos_x + offset_x - 600)/ (zoom) + 600, (massives[j].pos_y + offset_y - 400) / (zoom) + 400), max(int(massives[j].radius / (zoom)),1))
    pygame.display.update()
    
    #Tick
    clock.tick(800)
    for i in range(ticksPerLoop):
        ticked = lib.tick(massives, curLen)

    #Check for NAN value (generally from bad initialisation)
    if ticked.is_broken:
        ticked = loadMassives()

    #Get fields from Result
    massives = ticked.pointer
    curLen = ticked.len

    

    for e in pygame.event.get():  #Handle events (controls, etc)
        if e.type == pygame.QUIT:
            
            #Explicitly drop objects
            del(lib)
            del(ticked)
            del(massives)
            
            ctypes.DllCanUnloadNow()
        
            pygame.quit()
            exit()
        elif e.type == pygame.KEYDOWN: #Controls
            if e.key == pygame.K_w:
                zoom = zoom * 0.8
            elif e.key == pygame.K_s:
                zoom = zoom / 0.8
            elif e.key == pygame.K_a:
                ticksPerLoop = max(1, ticksPerLoop // 2)
                print("Ticks: {}", ticksPerLoop)
            elif e.key == pygame.K_d:
                ticksPerLoop = min(16384, ticksPerLoop * 2)
                print("Ticks: ", ticksPerLoop)
            elif e.key == pygame.K_UP:
                offset_y_vel = 2 * zoom
            elif e.key == pygame.K_DOWN:
                offset_y_vel = -2 * zoom
            elif e.key == pygame.K_RIGHT:
                offset_x_vel = -2 * zoom
            elif e.key == pygame.K_LEFT:
                offset_x_vel = 2 * zoom
            elif e.key == pygame.K_9:
                print(ticked.pointer)
        elif e.type == pygame.KEYUP:
            if e.key == pygame.K_UP:
                offset_y_vel = 0
            elif e.key == pygame.K_DOWN:
                offset_y_vel = 0
            elif e.key == pygame.K_RIGHT:
                offset_x_vel = 0
            elif e.key == pygame.K_LEFT:
                offset_x_vel = 0
            
