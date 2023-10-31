#modules
import pygame
import random
#files
from utils import *

class Healthbar:
    WIDTH = 130
    HEIGHT = 20
    BORDER = 3

    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.hp = max_hp

    def draw(self, surf, center):
        border = pygame.surface.Surface((self.WIDTH + self.BORDER * 2, self.HEIGHT + self.BORDER * 2))
        border.fill(BLACK)
        redbar = pygame.surface.Surface((self.WIDTH, self.HEIGHT))
        redbar.fill(RED)
        greenbar = pygame.surface.Surface((self.WIDTH * (self.hp / self.max_hp), self.HEIGHT))
        greenbar.fill(GREEN)

        redbar.blit(greenbar, (0, 0))
        border.blit(redbar, (self.BORDER, self.BORDER))
        surf.blit(border, (center[0] - self.WIDTH / 2, center[1]-70))

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

class Shield(Entity):
    def __init__(self, image):
        super().__init__(*CENTER, image)
        self.enabled = 0
        self.hp = 50

    def toggle(self):
        self.enabled = 1-self.enabled

class Player(Entity):
    SPEED = 12
    WATER_RESISTANCE = 0.95 #for timesing

    def __init__(self, x: int, y: int, images: list, shield_img: pygame.surface.Surface):
        self.img_no = 0
        super().__init__(x, y, images[self.img_no])

        #(changeable) stats
        self.damage = 10
        self.shooting_delay = 20

        self.images = images
        self.mask = pygame.mask.from_surface(self.image)
        self.og_img = self.image
        self.last_shot = self.shooting_delay
        self.angle = 0
        self.x_vel, self.y_vel = 0, 0

        self.on_cooldown = False
        self.hp = 1500

        self.shield = Shield(shield_img)

    def update(self, mousex):
        self.x_vel *= self.WATER_RESISTANCE
        self.y_vel *= self.WATER_RESISTANCE

        img = self.image

        if mousex < WIDTH/2:
            self.img_no = 0
        else:
            self.img_no = 1
        self.image = self.images[self.img_no]

        if self.image != img:
            self.mask = pygame.mask.from_surface(self.image)

        if self.last_shot < self.shooting_delay:
            self.last_shot += 1

        if self.on_cooldown:
            if abs(self.x_vel) < 1 and abs(self.y_vel) < 1:
                self.on_cooldown = False

    def hit(self, damage):
        self.hp -= damage
        self.on_cooldown = True

    # def draw(self, disp: pygame.surface.Surface):
    #     pass

class Anchor(Entity):
    SPEED = 30

    def __init__(self, x: int, y: int, image: pygame.surface.Surface):
        super().__init__(x, y, image)
        self.og_img = self.image
        self.mask = pygame.mask.from_surface(self.image)
        self.x_vel, self.y_vel = 0, 0
        self.angle = 0

        self.mode = 'still'

    def update(self, player_x_vel, player_y_vel, mouse_pos):
        if self.mode in ('still', 'return'):
            if self.mode == 'still':
                x, y = mouse_pos
                pos = pygame.math.Vector2(x, y) - self.rect.center
            else:
                x, y = CENTER
                pos = self.rect.center - pygame.math.Vector2(x, y)

            self.angle = pos.angle_to((0, 0))
            self.image = pygame.transform.rotate(self.og_img, self.angle - 90)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pygame.mask.from_surface(self.image)

            #vel
            self.x_vel, self.y_vel = calculate_kb((x, y), self.rect.center, self.SPEED)

        elif calculate_hypot(CENTER, self.rect.center) >= 400: #checks if length of wire is over 400
            self.mode = 'return'

        if self.mode != 'still':
            self.rect.x += self.x_vel+player_x_vel
            self.rect.y += self.y_vel+player_y_vel

    def get_bound(self, bound=0):
        return self.rect.top < 0 or\
            self.rect.bottom > HEIGHT or\
            self.rect.left < 0 or\
            self.rect.right > WIDTH

class Enemy(Entity):
    SPEED = 10
    WATER_RESISTANCE = 0.95
    DAMAGE = 10
    ANIMATION_DELAY = 5
    KB = 7

    def __init__(self, images):
        self.images = images
        image = images[0]

        w = image.get_width()
        h = image.get_height()

        if random.random() > 0.5:
            x = random.choice([-w-200, WIDTH+w])
            y = random.randint(-h-200, HEIGHT+h)
        else:
            x = random.randint(-w-200, WIDTH + w+200)
            y = random.choice([-h-200, HEIGHT + h+200])

        super().__init__(x, y, image)
        self.og_img = self.image
        self.mask = pygame.mask.from_surface(self.image)
        self.x_vel, self.y_vel = 0, 0
        self.angle = 0
        self.animation_count = 0

        self.tint = 0
        self.on_cooldown = False
        self.healthbar = Healthbar(100)

    def update(self, player_x_vel, player_y_vel):
        self.animation_count += 1
        if self.animation_count == len(self.images)*self.ANIMATION_DELAY:
            self.animation_count = 0

        self.og_img = self.images[self.animation_count//self.ANIMATION_DELAY]

        #rotate towards player
        x, y = CENTER
        pos = pygame.math.Vector2(x, y) - self.rect.center
        self.angle = pos.angle_to((0, 0))
        self.image = pygame.transform.rotate(self.og_img, self.angle-90)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

        if self.tint > 0:
            #tint overlay
            tint = self.image.copy()
            tint.fill(RED, special_flags=pygame.BLEND_RGB_MULT)
            tint.set_alpha(self.tint)

            self.image.blit(tint, (0, 0))
            self.tint -= TINT_FADE

        #vel
        if not self.on_cooldown:
            self.x_vel, self.y_vel = calculate_kb((x, y), self.rect.center, self.SPEED)
            #giration
            self.x_vel += random.randint(-2, 2)
            self.y_vel += random.randint(-2, 2)
        else:
            if abs(self.x_vel) < 1 and abs(self.y_vel) < 1:
                self.on_cooldown = False

        self.x_vel *= self.WATER_RESISTANCE
        self.y_vel *= self.WATER_RESISTANCE

        self.move(self.x_vel + player_x_vel, self.y_vel + player_y_vel)

        #dead?
        if self.healthbar.hp <= 0:
            return True

    def draw(self, disp: pygame.surface.Surface):
        disp.blit(self.image, self.rect.topleft)
        self.healthbar.draw(disp, self.rect.center)

    def hit(self, damage):
        self.healthbar.hp -= damage
        self.tint = 255

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y

class PlasmaEnemy(Enemy):
    SHOOTING_DELAY = 120
    SHOOTING_SPEED = 20
    SPEED = 8
    KB = 14

    def __init__(self, images):
        super().__init__(images)
        self.last_shot = self.SHOOTING_DELAY

    def update(self, player_x_vel, player_y_vel):
        if self.last_shot < self.SHOOTING_DELAY:
            self.last_shot += 1

        return super().update(player_x_vel, player_y_vel)

class PlasmaBall(Entity):
    BOUND = 3000
    KB = 7

    def __init__(self, x: int, y: int, x_vel: float, y_vel: float, image: pygame.surface.Surface = None):
        super().__init__(x, y, image)
        self.mask = pygame.mask.from_surface(self.image)
        self.x_vel, self.y_vel = x_vel, y_vel
        self.speed = x_vel+y_vel

    def update(self, player_x_vel, player_y_vel):
        self.rect.centerx += self.x_vel + player_x_vel
        self.rect.centery += self.y_vel + player_y_vel

        if self.get_bound(self.BOUND):
            return True

class Heart(Entity):
    BOUND = 3000
    AIR_RESISTANCE = 0.95

    def __init__(self, x: int, y: int, vel: int, image: pygame.surface.Surface):
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