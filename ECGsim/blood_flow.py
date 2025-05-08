import pygame
import random

class Sphere:

    def __init__(self,scene,x_l,x_h,y_l,y_h) -> None:
        self.scene = scene
        x = random.randint(x_l, x_h)
        y = random.randint(y_l, y_h)
        vx = random.uniform(-1, 1)
        vy = random.uniform(-1, 1)
        #vx = random.uniform(-1, 1)
        #vy = random.uniform(-1, 1)
        self.ball_pos = [x,y]
        self.ball_vel = [0, 0]
        self.ball_radius = 1 * 8
        self.gravity = 0.9
        self.bounce = -0.7

    def draw(self):
        pygame.draw.circle(self.scene.screen, (200, 50, 50), (int(self.ball_pos[0]), int(self.ball_pos[1])), self.ball_radius)



class Blood_Pipe:
    def __init__(self,scene,x_l,x_h,y_l,y_h) -> None:
        self.x_l = x_l
        self.x_h = x_h
        self.y_l = y_l
        self.y_h = y_h
        self.scene = scene
        self.entitys = []

    def draw(self):
        for entity in self.entitys:
            entity.draw()

    def create_sphere(self):
        return Sphere(self.scene,self.x_l,self.x_h,self.y_l,self.y_h)
