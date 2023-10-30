#modules
import sys
from math import ceil
#files
from entities import *

pygame.init()
pygame.mouse.set_visible(False)

FPS = 60
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
DISPLAY = pygame.surface.Surface((WIDTH, HEIGHT))

pygame.display.set_caption('Anchor')

class Game:
    def __init__(self):
        images = load_imgs('sub', True, 0.6)
        #main sprites
        self.player = Player(*CENTER, images)
        self.anchor = Anchor(*CENTER, load_img('anchor.png', True, 0.25))

        #group
        self.enemy_group = []
        self.heart_group = []
        self.projectile_group = []

        #particles
        #[pos, velocity, timer, speed, colour]
        self.particles = []

        #bg
        self.bg = load_img('ocean.png', False, 15)
        self.bg_tiles = []
        self.bg_w, self.bg_h = self.bg.get_rect().size
        self.bg_dimensions = [ceil(WIDTH / self.bg_w) + 1, ceil(HEIGHT / self.bg_h) + 1]  #0 is x, 1 is y

        for x in range(self.bg_dimensions[0]):
            for y in range(self.bg_dimensions[1]):
                self.bg_tiles.append([(x-1)*self.bg_w, (y-1)*self.bg_h, self.bg]) #randomise stars

        #other
        self.crosshair = load_img('crosshair.png', True, 3)
        self.overlay = load_img('overlay.png', True)
        self.plasmaball_img = load_img('plasmaball.png', True, 0.1)

        #game vars
        self.hearts = 0
        self.screen_shake = 0
        self.enemy_delay = 240
        self.last_enemy = self.enemy_delay

        ###########
        self.main()

    def main(self):
        clicked = False

        for i in range(3):
            e = random.choice([Enemy(load_imgs('squid', True, 0.7)), PlasmaEnemy(load_imgs('squid', True, 0.7))])
            self.enemy_group.append(e)

        #game loop
        while True:
            CLOCK.tick(FPS)

            #mouse and keys
            mouse_pos = pygame.mouse.get_pos()
            mouse_btns = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            #throw anchor?
            if mouse_btns[0]:
                if not clicked:
                    if self.anchor.mode == 'still':
                        self.anchor.mode = 'away'
                        self.anchor.x_vel, self.anchor.y_vel = calculate_kb(mouse_pos, self.anchor.rect.center,
                                                                            self.anchor.SPEED)
                    elif self.anchor.mode == 'away':
                        self.anchor.mode = 'return'
                clicked = True
            else:
                clicked = False

            if keys[pygame.K_SPACE] or mouse_btns[2]:
                if not self.player.on_cooldown:
                    self.player.x_vel, self.player.y_vel =\
                        calculate_kb(CENTER, mouse_pos, self.player.SPEED)

                    self.player.og_img = self.player.image

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

            #particles
            for particle in self.particles:
                particle[0][0] += particle[1][0] + player_x_vel
                particle[0][1] += particle[1][1] + player_y_vel
                particle[2] -= particle[3]

                #outline
                pygame.draw.circle(DISPLAY, WHITE, particle[0], particle[2] + 1)
                #main particle
                pygame.draw.circle(DISPLAY, particle[4], particle[0], particle[2])
                if particle[2] <= 0:
                    self.particles.remove(particle)


            #projectile_group
            for projectile in self.projectile_group:
                if projectile.update(player_x_vel, player_y_vel):
                    self.projectile_group.remove(projectile)
                projectile.draw(DISPLAY)

            #heart_group
            for heart in self.heart_group:
                condition_of_heart = heart.update(player_x_vel, player_y_vel)
                if condition_of_heart:
                    self.coin_group.remove(heart)
                heart.draw(DISPLAY)

            #anchor line
            pygame.draw.line(DISPLAY, DARK_GREY, self.anchor.rect.center, CENTER, 5)

            #enemy_group
            for enemy in self.enemy_group:
                if enemy.update(player_x_vel, player_y_vel):
                    self.enemy_group.remove(enemy)
                    self.add_hearts(enemy.rect.center, random.randint(2, 6))
                if hasattr(enemy, 'last_shot'):
                    if enemy.last_shot == enemy.SHOOTING_DELAY:
                        pball = PlasmaBall(*enemy.rect.center, *calculate_kb(CENTER, enemy.rect.center, enemy.SHOOTING_SPEED), self.plasmaball_img)
                        self.projectile_group.append(pball)
                        enemy.last_shot = 0
                enemy.draw(DISPLAY)

            #player
            self.player.update(mouse_pos[0])
            self.player.draw(DISPLAY)
            self.add_particles(([self.player.rect.right, self.player.rect.left][self.player.img_no], self.player.rect.centery),
                               1, 14, 10, 0.15, [BUBBLE_BLUE])

            #anchor
            self.anchor.update(player_x_vel, player_y_vel, mouse_pos)
            self.anchor.draw(DISPLAY)

            #overlay
            DISPLAY.blit(self.overlay, (0, 0))

            #UI
            #hearts
            draw_text(str(self.hearts), PIXEL_FONT, 'pink', 10, 5, 50, DISPLAY)

            #crosshair
            DISPLAY.blit(self.crosshair, (mouse_pos[0] - self.crosshair.get_width() / 2, mouse_pos[1] - self.crosshair.get_height() / 2))

            #COLLISION
            #anchor
            if self.anchor.mode == 'return':
                #player-anchor
                if pygame.sprite.spritecollideany(self.player, [self.anchor], pygame.sprite.collide_mask):
                    self.anchor.mode = 'still'
                    self.anchor.rect.center = CENTER
            if self.anchor.mode != 'still':
                #anchor-enemy_group
                for enemy in pygame.sprite.spritecollide(self.anchor, self.enemy_group, False, pygame.sprite.collide_mask):
                    enemy.hit(self.player.damage)
                    enemy.on_cooldown = True
                    enemy.x_vel, enemy.y_vel = calculate_kb(enemy.rect.center, self.anchor.rect.center, 14)
                    self.anchor.mode = 'return'
                #anchor-projectile_group
                for projectile in pygame.sprite.spritecollide(self.anchor, self.projectile_group, False, pygame.sprite.collide_mask):
                    projectile.x_vel, projectile.y_vel = calculate_kb(projectile.rect.center, self.anchor.rect.center, projectile.speed)
            #anchor-heart
            for heart in pygame.sprite.spritecollide(self.anchor, self.heart_group, False, pygame.sprite.collide_mask):
                self.heart_group.remove(heart)
                self.hearts += 1

            #player-enemy_group
            for enemy in pygame.sprite.spritecollide(self.player, self.enemy_group, False, pygame.sprite.collide_mask):
                enemy.x_vel, enemy.y_vel = calculate_kb(enemy.rect.center, CENTER, enemy.KB)
                enemy.on_cooldown = True
                self.hit_player(enemy)

            #player-projectile_group
            for projectile in pygame.sprite.spritecollide(self.player, self.projectile_group, False, pygame.sprite.collide_mask):
                self.projectile_group.remove(projectile)
                self.hit_player(projectile)

            #player-heart
            for heart in pygame.sprite.spritecollide(self.player, self.heart_group, False, pygame.sprite.collide_mask):
                self.heart_group.remove(heart)
                self.hearts += 1

            ####################################
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen_offset = [0, 0]
            if self.screen_shake > 0:
                screen_offset = [random.randint(-4, 4), random.randint(-4, 4)]
                self.screen_shake -= 1

            SCREEN.blit(DISPLAY, screen_offset)

            pygame.display.update()

    def hit_player(self, sprite):
        self.player.x_vel, self.player.y_vel = calculate_kb(sprite.rect.center, CENTER, sprite.KB / 2)
        self.player.hit(Enemy.DAMAGE)
        self.screen_shake = 20

    def add_particles(self, pos, number, size, vel, speed, colours):
        for i in range(number):
            self.particles.append(
                [list(pos), [random.randrange(vel) / 10 - vel/20, random.randrange(vel) / 10 - vel/20],
                 random.randrange(size), speed, random.choice(colours)])

    def add_hearts(self, pos, number):
        for i in range(number):
            heart = Heart(pos[0], pos[1], 5)
            self.heart_group.append(heart)

if __name__ == '__main__':
    g = Game()