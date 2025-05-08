import pygame
import sys
from heart_model import Heart
from blood_flow import Blood_Pipe
import math
import tkinter as tk
from tkinter import filedialog

RESTITUTION = 0.5
FRICTION = 0.98
SUBSTEPS = 8
MAG_TIME = 0.1

X_R = [160,210]
Y_R = [130,140]
S_B = 300

class Scene:
    def __init__(self, data) -> None:
        self.max_particles = 250
        self.A_MT = (100 - data["Apertura Mitral y Tricúspide"]) * (SUBSTEPS * MAG_TIME)
        self.C_MT = (data["Índice pico R (S1)"] + self.A_MT) * (SUBSTEPS * MAG_TIME)
        self.A_AP = (data["Apertura Aórtica y Pulmonar"] + self.A_MT) * (SUBSTEPS * MAG_TIME)
        self.C_A = (data["Índice pico T (S2)"] + self.A_MT) * (SUBSTEPS * MAG_TIME)
        self.C_P = (data["Cierre Pulmonar"] + self.A_MT) * (SUBSTEPS * MAG_TIME)
        self.Cicle_Time = 100 * (SUBSTEPS * MAG_TIME)

        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.font_c = pygame.font.SysFont("consolas",18)

        self.reset()

        running = True
        while running:
            self.screen.fill((30, 30, 30))
            elapsed_ms = pygame.time.get_ticks() - self.start_ticks
            seconds = elapsed_ms / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if seconds >= self.Cicle_Time:
                self.reset()
                continue

            if not self.valve_MT_opened and seconds >= self.A_MT and self.A_MT != 0:
                for valve in self.valve_objects_flow + self.valve_objects_del:
                    valve.open_valve()
                self.valve_MT_opened = True
            if self.valve_MT_opened and seconds >= self.C_MT and self.C_MT != 0:
                for valve in self.valve_objects_flow:
                    valve.close_valve()
                self.valve_MT_opened = False
            if not self.valve_MT_opened and seconds >= self.A_AP and self.A_AP != 0:
                for valve in self.valve_objects_del:
                    valve.close_valve()
                self.valve_A_opened = True
                self.valve_P_opened = True
            if self.valve_A_opened and seconds >= self.C_A and self.C_A != 0:
                self.valve_objects_del[0].open_valve()
                self.valve_A_opened = False
            if self.valve_P_opened and seconds >= self.C_P and self.C_P != 0:
                self.valve_objects_del[1].open_valve()
                self.valve_P_opened = False

            self.impulse_applied = False
            if self.valve_P_opened and not self.impulse_applied and seconds >= self.A_AP:
                for blood_list in self.blood_particles:
                    for particle in blood_list.entitys:
                        particle.ball_vel[1] -= 2
                self.impulse_applied = True

            if self.generated_particles < self.max_particles and self.valve_MT_opened:
                to_generate = min(self.particles_per_batch, self.max_particles - self.generated_particles) // 2
                for blood_particles in self.blood_particles:
                    new_particles = [blood_particles.create_sphere() for _ in range(to_generate)]
                    blood_particles.entitys.extend(new_particles)
                    self.generated_particles += to_generate

            to_remove = []
            for _ in range(SUBSTEPS):
                MAX_SPEED = 5.0
                for i, blood_list in enumerate(self.blood_particles):
                    chambers = [self.static_objects[0].chambers[0 + (i * 2)], self.static_objects[0].chambers[1 + (i * 2)]]
                    for item in blood_list.entitys:
                        item.ball_vel[1] += item.gravity / SUBSTEPS
                        item.ball_pos[0] += item.ball_vel[0] / SUBSTEPS
                        item.ball_pos[1] += item.ball_vel[1] / SUBSTEPS

                        speed = math.hypot(item.ball_vel[0], item.ball_vel[1])
                        if speed > MAX_SPEED:
                            scale = MAX_SPEED / speed
                            item.ball_vel[0] *= scale
                            item.ball_vel[1] *= scale

                        item.ball_vel[0] *= FRICTION
                        item.ball_vel[1] *= FRICTION

                        for chamber in chambers:
                            for wall in chamber.h_walls:
                                if self.ccd_circle_rect_collision(item, wall, item.ball_vel):
                                    self.reflect_circle(item, wall)

                        for del_wall in self.valve_objects_del:
                            if self.ccd_circle_rect_collision(item, del_wall.valve, item.ball_vel) and not self.valve_MT_opened:
                                to_remove.append(item)
                                break

                    for i in range(len(blood_list.entitys)):
                        for j in range(i + 1, len(blood_list.entitys)):
                            if self.circle_collision(blood_list.entitys[i], blood_list.entitys[j]):
                                self.resolve_collision(blood_list.entitys[i], blood_list.entitys[j])

            for blood_list in self.blood_particles:
                blood_list.entitys = [p for p in blood_list.entitys if p not in to_remove]

            for item in self.scene_objects:
                item.draw()

            # Mostrar tiempo, etapa y fonocardiograma
            etapa = self.get_etapa_actual(seconds)
            text_surface = self.font.render(f"Tiempo: {seconds:02}s", True, (0, 255, 0))
            text_stage = self.font.render(f"Etapa: {etapa}", True, (0, 255, 0))

            text_fono = self.font.render("", True, (255, 255, 255))
            if seconds >= 0 and seconds < self.C_MT:
                text_fono = self.font.render("Fonocardiograma: Inicio Diástole", True, (255, 255, 0))
            elif seconds >= self.C_MT and seconds < self.A_AP:
                text_fono = self.font.render("Fonocardiograma: Fin Diástole ", True, (255, 255, 0))
            elif seconds > self.A_AP and seconds < self.C_A:
                text_fono = self.font.render("Fonocardiograma: Inicio Sístole ", True, (255, 255, 0))
            elif seconds >= self.C_A:
                text_fono = self.font.render("Fonocardiograma: Fin Sístole", True, (255, 255, 0))

            self.screen.blit(text_surface, (10, 10))
            self.screen.blit(text_stage, (10, 35))
            self.screen.blit(text_fono, (10, self.HEIGHT - 110))

            # Mostrar resumen de etapas
            stages = [
                f"1. A. Mitral/Tricúspide: {self.A_MT:02}s",
                f"2. C. Mitral/Tricúspide: {self.C_MT:02}s",
                f"3. A. Aórtica/Pulmonar: {self.A_AP:02}s",
                f"4. C. Aórtica: {self.C_A:02}s",
                f"5. C. Pulmonar: {self.C_P:02}s",
                f"Duración ciclo: {self.Cicle_Time:02}s"
            ]
            for i, line in enumerate(stages):
                text = self.font.render(line, True, (200, 200, 200))
                self.screen.blit(text, (self.WIDTH//2, self.HEIGHT - 118 + (i * 18)))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def get_etapa_actual(self, seconds):
        if seconds < self.A_MT:
            return "0. Inicio del ciclo cardiaco"
        elif seconds < self.C_MT:
            return "1. Apertura Mitral/Tricúspide"
        elif seconds < self.A_AP:
            return "2. Cierre Mitral/Tricúspide"
        elif seconds < self.C_A:
            return "3. Apertura Aórtica/Pulmonar"
        elif seconds < self.C_P:
            return "4. Cierre Aórtica"
        elif seconds < self.C_P + 1:
            return "5. Cierre Pulmonar"
        else:
            return "6. Fin del ciclo cardiaco..."

    def reset(self):
        self.scene_objects = [
            Blood_Pipe(self, X_R[0], X_R[1], Y_R[0], Y_R[1]),
            Heart(self),
            Blood_Pipe(self, X_R[0] + S_B, X_R[1] + S_B, Y_R[0], Y_R[1])
        ]
        self.static_objects = [self.scene_objects[1]]
        self.valve_objects_flow = [self.static_objects[0].chambers[0], self.static_objects[0].chambers[2]]
        self.valve_objects_del = [self.static_objects[0].chambers[1], self.static_objects[0].chambers[3]]
        self.blood_particles = [self.scene_objects[0], self.scene_objects[2]]

        self.particles_per_batch = 5
        self.generated_particles = 0
        self.scene_objects[0].entitys = []

        self.start_ticks = pygame.time.get_ticks()
        self.valve_MT_opened = False
        self.impulse_applied = False
        self.valve_A_opened = False
        self.valve_P_opened = False

    def ccd_circle_rect_collision(self, circle, rect, vel):
        future_pos = [
            circle.ball_pos[0] + vel[0] / SUBSTEPS,
            circle.ball_pos[1] + vel[1] / SUBSTEPS
        ]
        closest_x = max(rect.left, min(future_pos[0], rect.right))
        closest_y = max(rect.top, min(future_pos[1], rect.bottom))
        dx = future_pos[0] - closest_x
        dy = future_pos[1] - closest_y
        return (dx * dx + dy * dy) < circle.ball_radius * circle.ball_radius
    
    def reflect_circle(self, circle, rect):
        closest_x = max(rect.left, min(circle.ball_pos[0], rect.right))
        closest_y = max(rect.top, min(circle.ball_pos[1], rect.bottom))
        dx = circle.ball_pos[0] - closest_x
        dy = circle.ball_pos[1] - closest_y
        dist_sq = dx * dx + dy * dy

        if dist_sq < circle.ball_radius * circle.ball_radius and dist_sq != 0:
            dist = math.sqrt(dist_sq)
            overlap = circle.ball_radius - dist
            nx, ny = dx / dist, dy / dist

            circle.ball_pos[0] += nx * overlap * 1.2
            circle.ball_pos[1] += ny * overlap * 1.2

            vn = circle.ball_vel[0] * nx + circle.ball_vel[1] * ny
            circle.ball_vel[0] -= 2 * vn * nx * RESTITUTION
            circle.ball_vel[1] -= 2 * vn * ny * RESTITUTION

    def circle_collision(self, c1, c2):
        dx = c2.ball_pos[0] - c1.ball_pos[0]
        dy = c2.ball_pos[1] - c1.ball_pos[1]
        dist = math.hypot(dx, dy)
        return dist < 2 * c1.ball_radius and dist > 0

    def resolve_collision(self, c1, c2):
        dx = c2.ball_pos[0] - c1.ball_pos[0]
        dy = c2.ball_pos[1] - c1.ball_pos[1]
        dist = math.hypot(dx, dy) or 1
        overlap = 0.5 * (2 * c1.ball_radius - dist)

        nx, ny = dx / dist, dy / dist
        c1.ball_pos[0] -= nx * overlap
        c1.ball_pos[1] -= ny * overlap
        c2.ball_pos[0] += nx * overlap
        c2.ball_pos[1] += ny * overlap

        vn1 = c1.ball_vel[0] * nx + c1.ball_vel[1] * ny
        vn2 = c2.ball_vel[0] * nx + c2.ball_vel[1] * ny
        impulse = (vn2 - vn1) * 0.5

        c1.ball_vel[0] += impulse * nx * RESTITUTION
        c1.ball_vel[1] += impulse * ny * RESTITUTION
        c2.ball_vel[0] -= impulse * nx * RESTITUTION
        c2.ball_vel[1] -= impulse * ny * RESTITUTION


if __name__ == "__main__":
    # Claves esperadas y sus valores por defecto
    campos_esperados = {
        'Tipo de ECG': [],
        'Índice pico R (S1)': 0,
        'Apertura Aórtica y Pulmonar': 0,
        'Índice pico T (S2)': 0,
        'Cierre Pulmonar': 0,
        'Apertura Mitral y Tricúspide': 0
    }

    def cargar_datos():
        root = tk.Tk()
        root.withdraw()

        archivo = filedialog.askopenfilename(
            title="Selecciona el archivo de datos",
            filetypes=[("Archivos de texto", "*.txt")]
        )

        datos = campos_esperados.copy()

        if archivo:
            with open(archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    if ':' in linea:
                        clave, valor = linea.strip().split(':', 1)
                        clave = clave.strip()
                        valor = valor.strip()
                        if clave in datos:
                            if valor.startswith('[') and valor.endswith(']'):
                                valor = valor.strip("[]").replace("'", "").split(',')
                                valor = [v.strip() for v in valor]
                            elif valor.isdigit():
                                valor = int(valor)
                            else:
                                try:
                                    valor = int(valor)
                                except ValueError:
                                    pass  # conservar como string
                            datos[clave] = valor
            return datos
        else:
            print("No se seleccionó ningún archivo.")


    # Uso
    datos_cargados = cargar_datos()
    if datos_cargados:
        print("Datos cargados:", datos_cargados)
        # Aquí continúa tu programa...
        Scene(datos_cargados)
    else:
        print("No fue posible cargar los datos")
