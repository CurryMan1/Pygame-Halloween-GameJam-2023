import pygame
from utils import *

class Entity(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, image: pygame.surface.Surface):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, disp: pygame.surface.Surface):
        disp.blit(self.image, (self.rect.x, self.rect.y))

    def get_bound(self, WIDTH, HEIGHT, bound=0):
        if self.rect.top < 0 or\
            self.rect.bottom > HEIGHT or\
            self.rect.left < 0 or\
            self.rect.right > WIDTH:
            return True

class Player(Entity):
    SPEED = 12
    AIR_RESISTANCE = 0.95 #for timesing

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
        self.x_vel *= self.AIR_RESISTANCE
        self.y_vel *= self.AIR_RESISTANCE

        if self.last_shot < self.shooting_delay:
            self.last_shot += 1

        if self.og_img == self.images[1]:
            self.og_img = self.images[0]

        if self.on_cooldown:
            if abs(self.x_vel) < 1 and abs(self.y_vel) < 1:
                self.on_cooldown = False

class Spear(Entity):
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

    def update(self, width, height, player_x_vel, player_y_vel):
        if self.mode in ('still', 'return'):
            if self.mode == 'still':
                x, y = pygame.mouse.get_pos()
            else:
                x, y = width / 2, height / 2

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

        if self.get_bound(width, height):
            self.mode = 'return'
            self.x_vel *= -1
            self.y_vel *= -1

class Enemy(Entity):
    pass

class Coin(Entity):
    BOUND = 3000
    AIR_RESISTANCE = 0.95

    def __init__(self, x: int, y: int, image: pygame.surface.Surface, vel: int):
        super().__init__(x, y, image)
        self.mask = pygame.mask.from_surface(self.image)
        self.x_vel, self.y_vel = random.randint(-vel, vel), random.randint(-vel, vel)

    def update(self, width, height, player_x_vel, player_y_vel):
        self.rect.centerx += self.x_vel + player_x_vel
        self.rect.centery += self.y_vel + player_y_vel

        self.x_vel *= self.AIR_RESISTANCE
        self.y_vel *= self.AIR_RESISTANCE

        if self.get_bound(width, height, self.BOUND):
            return 'out of bound'
