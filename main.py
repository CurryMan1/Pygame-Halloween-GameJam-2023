#modules
import pygame
import sys
from math import ceil
#files
from entities import *
from utils import *

pygame.init()
pygame.mouse.set_visible(False)

FPS = 60
WIDTH, HEIGHT = 1500, 900
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
DISPLAY = pygame.surface.Surface((WIDTH, HEIGHT))
pygame.display.set_caption('Thalassophobia')

class Game:
    def __init__(self):
        surf = pygame.surface.Surface((50, 50), pygame.SRCALPHA)
        surf.fill('red')

        images = [surf, surf]
        #main sprites
        self.player = Player(WIDTH / 2, HEIGHT / 2, images)
        self.spear = Spear(*self.player.rect.center)

        #group
        self.enemies = []

        #bg
        self.bg = load_img('ocean.png', True, 15)
        self.bg_tiles = []  #layers for parallax effect
        self.bg_w, self.bg_h = self.bg.get_rect().size
        self.bg_dimensions = [ceil(WIDTH / self.bg_w) + 1, ceil(HEIGHT / self.bg_h) + 1]  #0 is x, 1 is y

        for x in range(self.bg_dimensions[0]):
            for y in range(self.bg_dimensions[1]):
                self.bg_tiles.append([(x-1)*self.bg_w, (y-1)*self.bg_h, self.bg]) #randomise stars

        #other img
        self.crosshair = load_img('crosshair.png', True, 3)

        self.main()

    def main(self):
        clicked = False
        e = Enemy()

        while True:
            CLOCK.tick(FPS)

            #mouse and keys
            mouse_pos = pygame.mouse.get_pos()
            mouse_btns = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            if (keys[pygame.K_SPACE] or mouse_btns[2]) or mouse_btns[0]:
                if not self.player.on_cooldown:
                    if keys[pygame.K_SPACE] or mouse_btns[2]:
                        self.player.x_vel, self.player.y_vel =\
                            calculate_kb(self.player.rect.center, mouse_pos, self.player.SPEED)
                        self.player.og_img = self.player.images[1]

                #throw spear?
                if mouse_btns[0]:
                    if self.spear.mode == 'still' and not clicked:
                        self.spear.mode = 'away'
                        self.spear.x_vel, self.spear.y_vel = calculate_kb(mouse_pos, self.spear.rect.center, self.spear.SPEED)
                    clicked = True
            else:
                clicked = False

            player_x_vel, player_y_vel = self.player.x_vel, self.player.y_vel

            #DRAW AND UPDATE
            #bg
            DISPLAY.fill((0, 0, 0))
            for i, coords_and_bg in enumerate(self.bg_tiles): #bg_tiles
                x, y, bg = coords_and_bg

                diff_x = x - WIDTH
                diff_y = y - HEIGHT

                #works regardless of window size (if FOV is bigger than tile)
                if 0 < diff_x:
                    x = WIDTH - (self.bg_dimensions[0] * self.bg_w) + diff_x
                elif x < WIDTH - (self.bg_dimensions[0] * self.bg_w):
                    diff_x = x - (WIDTH - (self.bg_dimensions[0] * self.bg_w))
                    x = WIDTH + diff_x

                if 0 < diff_y:
                    y = HEIGHT - (self.bg_dimensions[1] * self.bg_h) + diff_y
                elif y < HEIGHT - (self.bg_dimensions[1] * self.bg_h):
                    diff_y = y - (HEIGHT - (self.bg_dimensions[1] * self.bg_h))
                    y = HEIGHT + diff_y

                self.bg_tiles[i] = [x + player_x_vel, y + player_y_vel, bg]

                DISPLAY.blit(bg, (x, y))

            #player
            self.player.update()
            self.player.draw(DISPLAY)

            #spear
            self.spear.update(WIDTH, HEIGHT, player_x_vel, player_y_vel)
            self.spear.draw(DISPLAY)

            #crosshair
            DISPLAY.blit(self.crosshair, (mouse_pos[0] - self.crosshair.get_width() / 2, mouse_pos[1] - self.crosshair.get_height() / 2))

            #COLLISION

            #player-spear
            if self.spear.mode == 'return':
                if pygame.sprite.spritecollideany(self.player, [self.spear], pygame.sprite.collide_mask):
                    self.spear.mode = 'still'
                    self.spear.rect.center = self.player.rect.center

            ####################################
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            SCREEN.blit(DISPLAY, (0, 0))

            pygame.display.update()

if __name__ == '__main__':
    g = Game()