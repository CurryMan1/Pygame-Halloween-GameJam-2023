import pygame
import random
from utils import *

class Entity(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, image: pygame.surface.Surface):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, disp: pygame.surface.Surface):
        disp.blit(self.image, (self.rect.x, self.rect.y))

    def get_bound(self, bound=0):
        return self.rect.centerx not in range(-bound, WIDTH + bound
            ) or self.rect.centery not in range(-bound, HEIGHT + bound)

class Player(Entity):
    SPEED = 12
    WATER_RESISTANCE = 0.95 #for timesing

    def __init__(self, x: int, y: int, images: list):
        super().__init__(x, y, images[0])

        #(changeable) stats
        self.damage = 5
        self.shooting_delay = 20

        self.mask = pygame.mask.from_surface(self.image)
        self.og_img = self.image
        self.images = images
        self.last_shot = self.shooting_delay
        self.angle = 0
        self.x_vel, self.y_vel = 0, 0

        self.on_cooldown = False

    def update(self):
        self.x_vel *= self.WATER_RESISTANCE
        self.y_vel *= self.WATER_RESISTANCE

        if self.last_shot < self.shooting_delay:
            self.last_shot += 1

        if self.og_img == self.images[1]:
            self.og_img = self.images[0]

        if self.on_cooldown:
            if abs(self.x_vel) < 1 and abs(self.y_vel) < 1:
                self.on_cooldown = False

class Trident(Entity):
    SPEED = 30

    def __init__(self, x: int, y: int):
        image = pygame.surface.Surface((10, 75), pygame.SRCALPHA)
        image.fill('green')
        super().__init__(x, y, image)
        self.og_img = self.image
        self.mask = pygame.mask.from_surface(self.image)
        self.x_vel, self.y_vel = 0, 0
        self.angle = 0

        self.mode = 'still'

    def update(self, player_x_vel, player_y_vel):
        if self.mode in ('still', 'return'):
            if self.mode == 'still':
                x, y = pygame.mouse.get_pos()
            else:
                x, y = WIDTH / 2, HEIGHT / 2

            pos = pygame.math.Vector2(x, y) - self.rect.center
            self.angle = pos.angle_to((0, 0))
            self.image = pygame.transform.rotate(self.og_img, self.angle - 90)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pygame.mask.from_surface(self.image)

            #vel
            self.x_vel, self.y_vel = calculate_kb((x, y), self.rect.center, self.SPEED)

        if self.mode != 'still':
            self.rect.x += self.x_vel + player_x_vel
            self.rect.y += self.y_vel + player_y_vel

        if self.get_bound():
            self.mode = 'return'
            self.x_vel *= -1
            self.y_vel *= -1

    def get_bound(self, bound=0):
        return self.rect.top < 0 or\
            self.rect.bottom > HEIGHT or\
            self.rect.left < 0 or\
            self.rect.right > WIDTH

class Enemy(Entity):
    SPEED = 11
    WATER_RESISTANCE = 0.95

    def __init__(self):
        image = pygame.surface.Surface((75, 75), pygame.SRCALPHA)
        image.fill('purple')

        w = image.get_width()
        h = image.get_height()

        if random.random() > 0.5:
            x = random.choice([-w, WIDTH+w])
            y = random.randint(-h, HEIGHT+h)
        else:
            x = random.randint(-w, WIDTH + w)
            y = random.choice([-h, HEIGHT + h])

        super().__init__(x, y, image)
        self.og_img = self.image
        self.mask = pygame.mask.from_surface(self.image)
        self.x_vel, self.y_vel = 0, 0
        self.angle = 0

        self.on_cooldown = False

    def update(self, player_x_vel, player_y_vel):
        #rotate towards player
        x, y = WIDTH / 2, HEIGHT / 2
        pos = pygame.math.Vector2(x, y) - self.rect.center
        self.angle = pos.angle_to((0, 0))
        self.image = pygame.transform.rotate(self.og_img, self.angle - 90)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

        #vel
        if not self.on_cooldown:
            self.x_vel, self.y_vel = calculate_kb((x, y), self.rect.center, self.SPEED)
        else:
            if abs(self.x_vel) < 1 and abs(self.y_vel) < 1:
                self.on_cooldown = False

        self.x_vel *= self.WATER_RESISTANCE
        self.y_vel *= self.WATER_RESISTANCE

        self.rect.x += self.x_vel + player_x_vel
        self.rect.y += self.y_vel + player_y_vel

class Coin(Entity):
    BOUND = 3000
    AIR_RESISTANCE = 0.95

    def __init__(self, x: int, y: int, image: pygame.surface.Surface, vel: int):
        super().__init__(x, y, image)
        self.mask = pygame.mask.from_surface(self.image)
        self.x_vel, self.y_vel = random.randint(-vel, vel), random.randint(-vel, vel)

    def update(self, player_x_vel, player_y_vel):
        self.rect.centerx += self.x_vel + player_x_vel
        self.rect.centery += self.y_vel + player_y_vel

        self.x_vel *= self.AIR_RESISTANCE
        self.y_vel *= self.AIR_RESISTANCE

        if self.get_bound(self.BOUND):
            return 'out of bound'
