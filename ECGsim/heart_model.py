import pygame
import random

DARK_RED = (155, 0, 0)
RED = (255, 0, 0)
LIGHT_RED = (255, 100, 100)

DARK_BLUE = (0, 0, 155)
BLUE = (0, 0, 255)
LIGHT_BLUE = (100, 100, 255)

LIGHT_PURPLE = (200, 75, 200)
DARK_PURPLE = (155, 75, 155)

TIMES = 5

LINE_WIDTH = 20

SCALE_ATRIUM =[19.17 * TIMES,60 * TIMES,32 * TIMES]
SCALE_VENTRICLE =[19.17 * TIMES,60 * TIMES,36 * TIMES]
X_POS = 100
Y_POS = 100

class Heart:
    def __init__(self,scene) -> None:
        self.l_atrium = L_Atrium(scene)
        self.l_ventricle = L_VENTRICLE(scene,self.l_atrium)
        self.r_atrium = R_Atrium(scene,self.l_atrium)
        self.r_ventricle = R_VENTRICLE(scene,self.r_atrium)
        self.chambers = [self.l_atrium,self.l_ventricle,self.r_atrium,self.r_ventricle]

    def draw(self):
         for chamber in self.chambers:
              chamber.draw()

class Heart_Chamber:
    def __init__(self,scene) -> None:
        self.h_walls = []
        self.valve_state = False
        self.scene = scene
        self.x = X_POS
        self.y = Y_POS
        self.line_width = LINE_WIDTH
        self.color = (0,0,0)
        self.color_valve = (255,255,255)
        

    def draw(self):
        for wall in self.h_walls:
            pygame.draw.rect(self.scene.screen, self.color, wall)
        
        if self.valve_state:
            pygame.draw.rect(self.scene.screen, self.color_valve, self.valve)
        
    
        indicator_x = self.x + self.height - 200
        indicator_y = self.y + 40 if isinstance(self, (L_Atrium, R_Atrium)) else self.y + self.width - 130
        
        color = (155, 0, 155)
        pygame.draw.circle(self.scene.screen, color, (indicator_x, indicator_y), 8)
        
        font = pygame.font.SysFont(None, 18)
        text = font.render(self.valve_name, True, (255, 255, 255))
        self.scene.screen.blit(text, (indicator_x + 15, indicator_y - 6))
        
        chamber_text = font.render(self.name, True, (255, 255, 255))
        if isinstance(self, (L_Atrium, R_Atrium)):
            self.scene.screen.blit(chamber_text, (self.x + 10, self.y + 5))
        else:
            self.scene.screen.blit(chamber_text, (self.x + 10, self.y + self.width + 3))
    
    def close_valve(self):
        self.valve_state = False
        self.h_walls.append(self.valve)
    
    def open_valve(self):
        self.valve_state = True
        if self.valve in self.h_walls:
            self.h_walls.pop()

class L_Atrium(Heart_Chamber):
    def __init__(self,scene) -> None:
        super().__init__(scene)
        self.height = SCALE_ATRIUM[1]
        self.width = SCALE_ATRIUM[2]
        self.name = "Aurícula Izquierda"
        self.valve_name = "Mitral"
        self.h_walls = [pygame.Rect(self.x, self.y, self.line_width, self.width),  # Left
                        pygame.Rect(self.x, self.y, self.height, self.line_width),   # Top
                        pygame.Rect(self.x+self.height, self.y, self.line_width, self.width)]      # Right
        self.color = DARK_BLUE
        self.color_valve = DARK_BLUE
        self.valve = pygame.Rect(self.x + self.line_width, self.y + self.width - self.line_width, self.height - self.line_width, self.line_width)
        self.close_valve()
    


    

class L_VENTRICLE(Heart_Chamber):
    def __init__(self,scene,atrium) -> None:
        super().__init__(scene)
        self.height = SCALE_VENTRICLE[1]
        self.width = SCALE_VENTRICLE[2]
        self.name = "Ventrículo Izquierdo"
        self.valve_name = "Aórtica"
        self.y = self.y + atrium.width
        self.h_walls = [pygame.Rect(self.x, self.y, self.line_width, self.width),  # Left
                        pygame.Rect(self.x, self.y+self.width, self.height, self.line_width),   # Top
                        pygame.Rect(self.x+self.height, self.y, self.line_width, self.width)]      # Right
        self.color = BLUE
        self.color_valve = BLUE
        self.valve = pygame.Rect(self.x + self.line_width, self.y ,self.height - self.line_width, self.line_width + (self.line_width//2))
        self.close_valve()

class R_Atrium(Heart_Chamber):
    def __init__(self,scene,other_chamber) -> None:
        super().__init__(scene)
        self.x = other_chamber.x + other_chamber.height + (LINE_WIDTH * 1.5)
        self.height = SCALE_ATRIUM[1]
        self.width = SCALE_ATRIUM[2]
        self.name = "Aurícula Derecha"
        self.valve_name = "Tricúspide"
        self.h_walls = [pygame.Rect(self.x, self.y, self.line_width, self.width),  # Left
                        pygame.Rect(self.x, self.y, self.height, self.line_width),   # Top
                        pygame.Rect(self.x+self.height, self.y, self.line_width, self.width)]      # Right
        self.color = DARK_RED
        self.color_valve = DARK_RED
        self.valve = pygame.Rect(self.x + self.line_width, self.y + self.width - self.line_width, self.height - self.line_width, self.line_width)
        self.close_valve()
    

    
class R_VENTRICLE(Heart_Chamber):
    def __init__(self,scene,atrium) -> None:
        super().__init__(scene)
        self.height = SCALE_VENTRICLE[1]
        self.width = SCALE_VENTRICLE[2]
        self.name = "Ventrículo Derecho"
        self.valve_name = "Pulmonar"
        self.x = atrium.x
        self.y = self.y + atrium.width
        self.h_walls = [pygame.Rect(self.x, self.y, self.line_width, self.width),  # Left
                        pygame.Rect(self.x, self.y+self.width, self.height, self.line_width),   # Bottom
                        pygame.Rect(self.x+self.height, self.y, self.line_width, self.width)]      # Right

        self.color = RED
        self.color_valve = RED
        self.valve = pygame.Rect(self.x + self.line_width, self.y ,self.height - self.line_width, self.line_width + (self.line_width//2))
        self.close_valve()
    