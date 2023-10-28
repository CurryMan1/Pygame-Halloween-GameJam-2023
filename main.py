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
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
DISPLAY = pygame.surface.Surface((WIDTH, HEIGHT))
pygame.display.set_caption('Thalassophobia')

class Game:
    def __init__(self):
        image = load_img('sub.png', True, 3)
        #main sprites
        self.player = Player(WIDTH / 2, HEIGHT / 2, image)
        self.trident = Anchor(*self.player.rect.center, load_img('anchor.png', True, 0.25))

        #group
        self.enemies = []

        #bg
        self.bg = load_img('ocean.png', False, 15)
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
        e = Enemy(load_imgs('squid', True, 0.7))

        self.enemies.append(e)

        #game loop
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
                        self.player.og_img = self.player.image

                #throw trident?
                if mouse_btns[0]:
                    if self.trident.mode == 'still' and not clicked:
                        self.trident.mode = 'away'
                        self.trident.x_vel, self.trident.y_vel = calculate_kb(mouse_pos, self.trident.rect.center, self.trident.SPEED)
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

            #enemies
            for enemy in self.enemies:
                enemy.update(player_x_vel, player_y_vel)
                enemy.draw(DISPLAY)

            #player
            self.player.update()
            self.player.draw(DISPLAY)

            #trident
            self.trident.update(player_x_vel, player_y_vel)
            self.trident.draw(DISPLAY)

            #crosshair
            DISPLAY.blit(self.crosshair, (mouse_pos[0] - self.crosshair.get_width() / 2, mouse_pos[1] - self.crosshair.get_height() / 2))

            #COLLISION
            #trident
            if self.trident.mode == 'return':
                #player-trident
                if pygame.sprite.spritecollideany(self.player, [self.trident], pygame.sprite.collide_mask):
                    self.trident.mode = 'still'
                    self.trident.rect.center = self.player.rect.center
            elif self.trident.mode == 'away':
                #trident-enemies
                for enemy in pygame.sprite.spritecollide(self.trident, self.enemies, False, pygame.sprite.collide_mask):
                    self.trident.mode = 'return'


            #player-enemies
            collided_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_mask)
            if collided_enemies:
                self.player.x_vel *= -1
                self.player.y_vel *= -1
                self.player.on_cooldown = True
            for enemy in collided_enemies:
                enemy.x_vel, enemy.y_vel = calculate_kb(enemy.rect.center, self.player.rect.center, 7)
                enemy.on_cooldown = True

            ####################################
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            SCREEN.blit(DISPLAY, (0, 0))

            pygame.display.update()

if __name__ == '__main__':
    g = Game()