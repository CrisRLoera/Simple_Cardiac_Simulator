import pygame
import random
import math

# Inicializar Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Parámetros
NUM_CIRCLES = 200
RADIUS = 1
GRAVITY = 0.3
FRICTION = 0.98
RESTITUTION = 0.5  # rebote menos elástico (para simular líquido)

circles = []

# Crear círculos
for _ in range(NUM_CIRCLES):
    x = random.randint(120, WIDTH - 120)
    y = random.randint(120, HEIGHT - 300)
    vx = random.uniform(-1, 1)
    vy = random.uniform(-1, 1)
    circles.append({'x': x, 'y': y, 'vx': vx, 'vy': vy})

# Paredes
walls = [
    pygame.Rect(100, 100, 600, 10),  # top
    pygame.Rect(100, 490, 600, 10),  # bottom
    pygame.Rect(100, 100, 10, 400),  # left
    pygame.Rect(690, 100, 10, 400),  # right
]

def circle_collision(c1, c2):
    dx = c2['x'] - c1['x']
    dy = c2['y'] - c1['y']
    dist = math.hypot(dx, dy)
    return dist < 2 * RADIUS and dist > 0

def resolve_collision(c1, c2):
    dx = c2['x'] - c1['x']
    dy = c2['y'] - c1['y']
    dist = math.hypot(dx, dy) or 1
    overlap = 0.5 * (2 * RADIUS - dist)

    nx, ny = dx / dist, dy / dist

    # Separación suave (presión)
    c1['x'] -= nx * overlap
    c1['y'] -= ny * overlap
    c2['x'] += nx * overlap
    c2['y'] += ny * overlap

    # Intercambiar velocidad amortiguada (rebote viscoso)
    vn1 = c1['vx'] * nx + c1['vy'] * ny
    vn2 = c2['vx'] * nx + c2['vy'] * ny
    impulse = (vn2 - vn1) * 0.5

    c1['vx'] += impulse * nx * RESTITUTION
    c1['vy'] += impulse * ny * RESTITUTION
    c2['vx'] -= impulse * nx * RESTITUTION
    c2['vy'] -= impulse * ny * RESTITUTION

def circle_rect_collision(circle, rect):
    closest_x = max(rect.left, min(circle['x'], rect.right))
    closest_y = max(rect.top, min(circle['y'], rect.bottom))
    dx = circle['x'] - closest_x
    dy = circle['y'] - closest_y
    return (dx * dx + dy * dy) < RADIUS * RADIUS

def reflect_circle(circle, rect):
    closest_x = max(rect.left, min(circle['x'], rect.right))
    closest_y = max(rect.top, min(circle['y'], rect.bottom))
    dx = circle['x'] - closest_x
    dy = circle['y'] - closest_y
    dist_sq = dx * dx + dy * dy

    if dist_sq < RADIUS * RADIUS and dist_sq != 0:
        dist = math.sqrt(dist_sq)
        overlap = RADIUS - dist
        nx, ny = dx / dist, dy / dist

        # Reposicionar fuera del muro
        circle['x'] += nx * overlap
        circle['y'] += ny * overlap

        # Reflejar la velocidad con restitución
        vn = circle['vx'] * nx + circle['vy'] * ny
        circle['vx'] -= 2 * vn * nx * RESTITUTION
        circle['vy'] -= 2 * vn * ny * RESTITUTION


# Loop principal
running = True
while running:
    screen.fill((30, 30, 30))

    for wall in walls:
        pygame.draw.rect(screen, (0, 255, 0), wall)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                for c in circles:
                    c['vy'] = -random.uniform(8, 12)  # impulso hacia arriba
                    c['vx'] += random.uniform(-3, 3)  # impulso lateral leve

    # Actualizar física de círculos
    for c in circles:
        c['vy'] += GRAVITY
        c['x'] += c['vx']
        c['y'] += c['vy']
        c['vx'] *= FRICTION
        c['vy'] *= FRICTION

        # Colisión con paredes
        for wall in walls:
            if circle_rect_collision(c, wall):
                reflect_circle(c, wall)

        pygame.draw.circle(screen, (0, 100, 255), (int(c['x']), int(c['y'])), RADIUS)

    # Colisiones entre círculos
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            if circle_collision(circles[i], circles[j]):
                resolve_collision(circles[i], circles[j])

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
