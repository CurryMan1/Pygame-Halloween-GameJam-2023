#modules
import sys
from math import ceil
from webbrowser import open

#files
from entities import *
from ui import *

pygame.init()
pygame.mouse.set_visible(False)

#mixer
pygame.mixer.init()
pygame.mixer.music.set_volume(0.1)

FPS = 60
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
DISPLAY = pygame.surface.Surface((WIDTH, HEIGHT))

pygame.display.set_caption('Anchor')
pygame.display.set_icon(load_img('icon.png', True))

class Game:
    def __init__(self):
        #main sprites
        self.player = Player(*CENTER, load_imgs('sub', True, 0.6), load_img('shield.png', True, 0.6))
        self.anchor = Anchor(*CENTER, [load_img('anchor.png', True, 0.25), load_img('torpedo.png', True, 0.6)])

        #group
        self.enemy_group = []
        self.consumable_group = []
        self.projectile_group = []
        self.upgrade_button_group = []
        self.bg_tile_group = []

        #effects
        #[pos, velocity, timer, speed, colour]
        self.particles = []
        #[text, opacity, x, y]
        self.splash_texts = []

        #upgrade buttons
        self.upgrade_btn_tags = [['shield', 30], ['torpedo', 60], ['quad damage', 45], ['sharp anchor', 15]]

        for i, btn in enumerate(self.upgrade_btn_tags):
            tag, price = btn

            u_btn = UpgradeButton(i*210+10, HEIGHT-210, tag, price)
            self.upgrade_button_group.append(u_btn)

        #other
        self.logo = load_img('logo.png', True, 1.1)
        self.crosshair = load_img('crosshair.png', True, 3)
        self.light = load_img('light.png', True)
        self.overlay = load_img('overlay.png', True)
        self.plasmaball_img = load_img('plasmaball.png', True, 0.1)
        self.heart_img = load_img('heart.png', True, 0.5)
        self.plasmaenemy_img = load_img('plasmaenemy.png', True, 0.4)
        self.seamine_img = load_img('seamines.png', True, 0.4)
        self.squid_imgs = load_imgs('squid', True, 0.7)

        #game vars
        self.sound_on = 1
        self.effects_on = 1
        self.shake_enabled = 1
        self.hearts = 0
        self.screen_shake = 0

        #sound
        self.siren_sound = load_sound('sub/siren.mp3')

    def start(self, first=False):
        if first:
            pygame.mixer.music.load('assets/sound/theme.wav')
            pygame.mixer.music.play(-1)

        start_btn = Button(WIDTH/2-400, HEIGHT/2+30, 800, 150, text='Start', fg=DARK_GREY, bg=LIGHT_GREY, text_size=90,
                           text_colour=WHITE, border_width=5)

        settings_btn = Button(WIDTH/2-400, HEIGHT/2+190, 800, 150, text='Settings', fg=DARK_GREY, bg=LIGHT_GREY, text_size=90,
                           text_colour=WHITE, border_width=5)

        while True:
            CLOCK.tick(FPS)

            mouse_pos = pygame.mouse.get_pos()

            #bg
            DISPLAY.fill(OCEAN_BLUE)

            DISPLAY.blit(self.logo, (WIDTH/2-self.logo.get_width()/2, 60))

            if start_btn.is_clicked(DISPLAY):
                return self.main()
            if settings_btn.is_clicked(DISPLAY):
                return self.settings(self.start)

            #overlay
            DISPLAY.blit(self.overlay, (0, 0))

            #light
            DISPLAY.blit(self.light, (
            mouse_pos[0] - self.light.get_width() / 2, mouse_pos[1] - self.light.get_height() / 2))

            #crosshair
            DISPLAY.blit(self.crosshair, (mouse_pos[0] - self.crosshair.get_width() / 2, mouse_pos[1] - self.crosshair.get_height() / 2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            SCREEN.blit(DISPLAY, (0, 0))

            pygame.display.update()

    def settings(self, last_menu):
        title_box = get_box(900, 200, 10, BLACK, DARK_GREY)

        back_btn = Button(10, 10, 170, 120, text='Back', fg=DARK_GREY, bg=LIGHT_GREY,
                           text_size=50,
                           text_colour=WHITE, border_width=5)

        sound_btn = Button(WIDTH/5, 350, 450, 120, text='Sound:ON', fg=DARK_GREY, bg=LIGHT_GREY,
                           text_size=70,
                           text_colour=WHITE, border_width=5)

        performance_btn = Button(WIDTH/2+10, 350, 450, 120, text='Effects:ON', fg=DARK_GREY, bg=LIGHT_GREY,
                           text_size=65,
                           text_colour=WHITE, border_width=5)

        shake_btn = Button(WIDTH/5, 550, 450, 120, text='Shake:ON', fg=DARK_GREY, bg=LIGHT_GREY,
                            text_size=70,
                            text_colour=WHITE, border_width=5)

        github_btn = Button(WIDTH/2+10, 550, 450, 120, text='Github', fg=DARK_GREY, bg=LIGHT_GREY,
                           text_size=70,
                           text_colour=WHITE, border_width=5)

        while True:
            CLOCK.tick(FPS)

            mouse_pos = pygame.mouse.get_pos()

            #bg
            DISPLAY.fill(OCEAN_BLUE)

            #title
            DISPLAY.blit(title_box, (WIDTH/2-title_box.get_width()/2, 170-title_box.get_height()/2))
            draw_text('Settings', PIXEL_FONT, WHITE, WIDTH/2, 170, 150, DISPLAY, True)

            #buttons
            if back_btn.is_clicked(DISPLAY):
                return last_menu()
            if sound_btn.is_clicked(DISPLAY):
                self.sound_on = 1-self.sound_on
                sound_btn.text = f'Sound:{["OFF", "ON"][self.sound_on]}'
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            if performance_btn.is_clicked(DISPLAY):
                self.effects_on = 1-self.effects_on
                performance_btn.text = f'Effects:{["OFF", "ON"][self.effects_on]}'
            if shake_btn.is_clicked(DISPLAY):
                self.shake_enabled = 1-self.shake_enabled
                shake_btn.text = f'Shake:{["OFF", "ON"][self.shake_enabled]}'
            if github_btn.is_clicked(DISPLAY):
                open('https://github.com/CurryMan1/Pygame-Halloween-GameJam-2023')

            #overlay
            DISPLAY.blit(self.overlay, (0, 0))

            #light
            DISPLAY.blit(self.light, (
                mouse_pos[0] - self.light.get_width() / 2, mouse_pos[1] - self.light.get_height() / 2))

            #crosshair
            DISPLAY.blit(self.crosshair, (mouse_pos[0] - self.crosshair.get_width() / 2, mouse_pos[1] - self.crosshair.get_height() / 2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            SCREEN.blit(DISPLAY, (0, 0))

            pygame.display.update()

    def main(self):
        pygame.mixer.music.load('assets/sound/ambience.wav')
        pygame.mixer.music.play()

        pygame.mixer.Channel(0).set_volume(0)
        pygame.mixer.Channel(0).play(self.siren_sound, -1)

        clicked = True
        can_shoot_torpedo = False
        quad_damage_timer = 0

        enemy_spawn_delay = 10*FPS
        frames_since_last_enemy = enemy_spawn_delay-2*FPS
        score = 0


        #game loop
        while True:
            CLOCK.tick(FPS)

            #score
            score += 1
            if self.player.hp < self.player.MAX_HP:
                self.player.hp += 0.1

            #mouse and keys
            mouse_pos = pygame.mouse.get_pos()
            mouse_btns = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            #throw anchor/torpedo?
            if mouse_btns[0]:
                if not clicked:
                    if not self.anchor.torpedo_enabled:
                        if self.anchor.mode == 'still':
                            self.anchor.mode = 'away'
                            self.anchor.x_vel, self.anchor.y_vel = calculate_kb(mouse_pos, CENTER,
                                                                                self.anchor.SPEED)
                        elif self.anchor.mode == 'away':
                            self.anchor.mode = 'return'
                    else:
                        torpedo = Projectile(*CENTER, *calculate_kb(mouse_pos, CENTER, self.anchor.SPEED+10), self.anchor.image, 'torpedo')
                        self.projectile_group.append(torpedo)
                        self.anchor.torpedo_enabled = False
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
            DISPLAY.fill(OCEAN_BLUE)

            #particles
            for particle in self.particles:
                particle[0][0] += particle[1][0] + player_x_vel
                particle[0][1] += particle[1][1] + player_y_vel
                particle[2] -= particle[3]

                if particle[5] == 'torpedo':
                    collision_rect = pygame.rect.Rect(particle[0][0]-particle[2], particle[0][1]-particle[2], particle[2]*2, particle[2]*2)
                    for enemy in collision_rect.collideobjectsall(self.enemy_group):
                        enemy.hit(100)

                elif particle[5] == 'bubble':
                    #outline
                    pygame.draw.circle(DISPLAY, WHITE, particle[0], particle[2] + 1)

                if self.effects_on or particle[5] == 'bubble':
                    #main particle
                    pygame.draw.circle(DISPLAY, particle[4], particle[0], particle[2])

                if particle[2] <= 0:
                    self.particles.remove(particle)

            #consumable_group
            for consumable in self.consumable_group:
                condition_of_heart = consumable.update(player_x_vel, player_y_vel)
                if condition_of_heart:
                    self.consumable_group.remove(consumable)
                consumable.draw(DISPLAY)

            #anchor line
            pygame.draw.line(DISPLAY, DARK_GREY, self.anchor.rect.center, CENTER, 5)

            #enemy_group
            for enemy in self.enemy_group:
                if enemy.update(player_x_vel, player_y_vel):
                    self.enemy_group.remove(enemy)
                    self.add_hearts(enemy.rect.center, random.randint(2, 6))
                if hasattr(enemy, 'last_shot'):
                    if enemy.last_shot == enemy.SHOOTING_DELAY:
                        pball = Projectile(*enemy.rect.center, *calculate_kb(CENTER, enemy.rect.center, enemy.SHOOTING_SPEED), self.plasmaball_img, 'plasmaball')
                        self.projectile_group.append(pball)
                        enemy.last_shot = 0
                enemy.draw(DISPLAY)

            if frames_since_last_enemy >= round(enemy_spawn_delay):
                for i in range(5):
                    e = random.choice([Enemy(self.squid_imgs), PlasmaEnemy([self.plasmaenemy_img])])
                    self.enemy_group.append(e)
                frames_since_last_enemy = 0
                if enemy_spawn_delay > 5*FPS:
                    enemy_spawn_delay -= 0.3

                #mine
                while True:
                    position_x = random.randint(-2000, WIDTH+2000)
                    position_y = random.randint(-2000, HEIGHT+2000)
                    if position_x not in range(0, WIDTH) and\
                        position_y not in range(0, HEIGHT):
                        mine = Consumable(position_x, position_y, 0, self.seamine_img, 'seamine')
                        self.consumable_group.append(mine)
                        break
            else:
                frames_since_last_enemy += 1

            #player
            if self.player.update(mouse_pos[0]):
                self.player_dead(score/FPS)

            self.player.draw(DISPLAY)
            self.add_particles(([self.player.rect.right, self.player.rect.left][self.player.img_no], self.player.rect.centery),
                               1, 14, 10, 0.3, [BUBBLE_BLUE], 'bubble')

            #quad damage
            if quad_damage_timer > 0:
                quad_damage_timer -= 1
                if quad_damage_timer == 0:
                    self.player.damage = int(self.player.damage/4)

            #anchor
            self.anchor.update(player_x_vel, player_y_vel, mouse_pos)
            self.anchor.draw(DISPLAY)

            #projectile_group
            for projectile in self.projectile_group:
                if projectile.update(player_x_vel, player_y_vel):
                    self.projectile_group.remove(projectile)
                projectile.draw(DISPLAY)

            #splash_texts
            if self.effects_on:
                for sp_text in self.splash_texts:
                    text, opacity, x, y, colour = sp_text
                    sp_text[1] -= 10

                    draw_text(text, PIXEL_FONT, colour, x, y, 50, DISPLAY, True, opacity)
                    if opacity <= 0:
                        self.splash_texts.remove(sp_text)

            #overlay
            DISPLAY.blit(self.overlay, (0, 0))

            #UI
            #no_of_hearts
            DISPLAY.blit(self.heart_img, (10, 10))
            draw_text(str(self.hearts), PIXEL_FONT, PINK, self.heart_img.get_width()+10, 5, 50, DISPLAY)

            #tab for shop text
            draw_text('Tab for shop', PIXEL_FONT, WHITE, WIDTH-360, 5, 50, DISPLAY)

            #buttons
            #upgrade buttons
            if keys[pygame.K_TAB]:
                for button in self.upgrade_button_group:
                    if button.is_clicked(DISPLAY):
                        if self.hearts >= button.price:
                            charge = True
                            if button.text == 'shield':
                                if not self.player.shield.enabled:
                                    self.player.shield.toggle()
                            elif button.text == 'torpedo':
                                self.anchor.torpedo_enabled = True
                                self.anchor.mode = 'still'
                                self.anchor.x_vel, self.anchor.y_vel = 0,0
                                self.anchor.rect.center = CENTER
                            elif button.text == 'quad damage':
                                if quad_damage_timer == 0:
                                    quad_damage_timer = 600
                                    self.player.damage *= 4
                                else:
                                    charge = False
                            else:
                                self.player.damage += 5

                            if charge:
                                self.splash_texts.append([f'-{button.price}', 256, *mouse_pos, RED])
                                self.hearts -= button.price
                                button.price = round(button.price*1.2)

            #light
            DISPLAY.blit(self.light, (
                mouse_pos[0] - self.light.get_width() / 2, mouse_pos[1] - self.light.get_height() / 2))

            #player hp
            dec = self.player.hp/self.player.MAX_HP
            #siren
            pygame.mixer.Channel(0).set_volume(max(0.25 - dec, 0))
            #tint
            tint = DISPLAY.copy()
            tint.fill(RED, special_flags=pygame.BLEND_RGB_MULT)
            tint.set_alpha(max(100-dec*255, 0))
            DISPLAY.blit(tint, (0, 0))

            #crosshair
            DISPLAY.blit(self.crosshair, (mouse_pos[0] - self.crosshair.get_width() / 2, mouse_pos[1] - self.crosshair.get_height() / 2))

            #COLLISION
            #anchor
            if self.anchor.mode == 'return':
                #player-anchor
                if pygame.sprite.spritecollideany(self.player, [self.anchor], pygame.sprite.collide_mask):
                    self.anchor.mode = 'still'
                    self.anchor.rect.center = CENTER
            if self.anchor.mode == 'away':
                #anchor-projectile_group
                for projectile in pygame.sprite.spritecollide(self.anchor, self.projectile_group, False, pygame.sprite.collide_mask):
                    if projectile.tag != 'torpedo':
                        projectile.x_vel, projectile.y_vel = calculate_kb(self.anchor.rect.center, projectile.rect.center, projectile.speed)
            if self.anchor.mode != 'still':
                #anchor-enemy_group
                for enemy in pygame.sprite.spritecollide(self.anchor, self.enemy_group, False, pygame.sprite.collide_mask):
                    enemy.hit(self.player.damage)
                    enemy.on_cooldown = True
                    enemy.x_vel, enemy.y_vel = calculate_kb(enemy.rect.center, self.anchor.rect.center, 14)
                    self.anchor.mode = 'return'
                    self.splash_texts.append(
                        [f'-{self.player.damage}', 256, enemy.rect.centerx,
                         enemy.rect.centery, RED])

            #anchor-consumable
            for consumable in pygame.sprite.spritecollide(self.anchor, self.consumable_group, False, pygame.sprite.collide_mask):
                self.consumable_group.remove(consumable)
                if consumable.tag != 'seamine':
                    self.splash_texts.append(['+1', 256, *consumable.rect.center, GREEN])
                    self.hearts += 1
                else:
                    self.add_particles(consumable.rect.center, 50, 25, 20, 0.5, [RED, ORANGE, YELLOW], 'seamine')

            #projectile_group-enemy_group
            collided_projectiles = pygame.sprite.groupcollide(self.projectile_group, self.enemy_group, False, False, pygame.sprite.collide_mask)
            for projectile in collided_projectiles.keys():
                if projectile.tag == 'torpedo':
                    self.projectile_group.remove(projectile)
                    enemies = collided_projectiles[projectile]
                    for enemy in enemies:
                        enemy.hit(100)
                    self.add_particles(enemies[0].rect.center, 50, 25, 20, 0.5, [RED, ORANGE, YELLOW], 'torpedo')

            #player-enemy_group
            for enemy in pygame.sprite.spritecollide(self.player, self.enemy_group, False, pygame.sprite.collide_mask):
                enemy.x_vel, enemy.y_vel = calculate_kb(enemy.rect.center, CENTER, enemy.KB)
                enemy.on_cooldown = True
                self.hit_player(enemy)

            #player-projectile_group
            for projectile in pygame.sprite.spritecollide(self.player, self.projectile_group, False, pygame.sprite.collide_mask):
                if projectile.tag != 'torpedo':
                    self.projectile_group.remove(projectile)
                    self.hit_player(projectile)
                    self.add_particles(projectile.rect.center, 30, 10, 70, 0.15, [PLASMA_GREEN, GREEN, WHITE], 'plasma')

            #player-consumable_group
            for consumable in pygame.sprite.spritecollide(self.player, self.consumable_group, False, pygame.sprite.collide_mask):
                self.consumable_group.remove(consumable)
                if consumable.tag == 'seamine':
                    self.screen_shake = 30
                    self.hit_player(consumable)
                    self.add_particles(consumable.rect.center, 50, 25, 20, 0.5, [RED, ORANGE, YELLOW], 'seamine')
                else:
                    self.splash_texts.append(['+1', 256, *consumable.rect.center, GREEN])
                    self.hearts += 1

            if self.player.shield.enabled:
                #player.shield-enemy_group
                for enemy in pygame.sprite.spritecollide(self.player.shield, self.enemy_group, False, pygame.sprite.collide_mask):
                    enemy.x_vel, enemy.y_vel = calculate_kb(enemy.rect.center, CENTER, enemy.KB*2)
                    enemy.on_cooldown = True
                    if self.player.shield.hit(enemy.DAMAGE):
                        self.add_particles(CENTER, 50, 20, 140, 0.15, [BUBBLE_BLUE, WHITE], 'shield')

                #player.shield-projectile_group
                for projectile in pygame.sprite.spritecollide(self.player.shield, self.projectile_group, False, pygame.sprite.collide_mask):
                    if projectile.tag != 'torpedo':
                        self.projectile_group.remove(projectile)
                        self.add_particles(projectile.rect.center, 30, 10, 70, 0.15, [PLASMA_GREEN, WHITE], 'plasma')
                        if self.player.shield.hit(projectile.DAMAGE):
                            self.add_particles(CENTER, 50, 20, 140, 0.15, [BUBBLE_BLUE, WHITE], 'shield')

            ####################################
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen_offset = [0, 0]
            if self.shake_enabled:
                if self.screen_shake > 0:
                    screen_offset = [random.randint(-4, 4), random.randint(-4, 4)]
                    self.screen_shake -= 1

            SCREEN.blit(DISPLAY, screen_offset)

            pygame.display.update()

    def player_dead(self, score):
        pygame.mixer.Channel(0).fadeout(1)
        belt = pygame.surface.Surface((WIDTH, 400))
        belt.fill(LIGHT_GREY)

        home_btn = Button(WIDTH / 2 - 300, 700, 600, 120, text='Try Again', fg=DARK_GREY, bg=LIGHT_GREY,
                            text_size=70,
                            text_colour=WHITE, border_width=5)

        #RESET
        self.enemy_group = []
        self.consumable_group = []
        self.projectile_group = []
        self.upgrade_button_group = []
        self.bg_tile_group = []
        self.particles = []
        self.splash_texts = []

        self.player.shield.enabled = False
        self.player.hp = self.player.MAX_HP
        self.player.damage = 10

        #upgrade buttons
        for i, btn in enumerate(self.upgrade_btn_tags):
            tag, price = btn
            u_btn = UpgradeButton(i * 210 + 10, HEIGHT - 210, tag, price)
            self.upgrade_button_group.append(u_btn)

        #game vars
        self.hearts = 0
        self.screen_shake = 0

        opacity = 0
        while True:
            CLOCK.tick(FPS)

            mouse_pos = pygame.mouse.get_pos()

            #bg
            DISPLAY.fill(OCEAN_BLUE)

            #dead message
            belt.set_alpha(opacity)
            if opacity < 255:
                opacity += 2
            DISPLAY.blit(belt, (0, HEIGHT/2 - 200))

            draw_text('wasted', PIXEL_FONT, BLACK, WIDTH/2, HEIGHT/2-50, 230, DISPLAY, True, opacity)
            draw_text(f'You lasted {round(score, 1)} seconds', PIXEL_FONT, BLACK, WIDTH / 2, HEIGHT / 2+100, 70, DISPLAY, True, opacity)

            #btn
            if home_btn.is_clicked(DISPLAY):
                return self.start(True)

            #overlay
            DISPLAY.blit(self.overlay, (0, 0))

            #light
            DISPLAY.blit(self.light, (
            mouse_pos[0] - self.light.get_width() / 2, mouse_pos[1] - self.light.get_height() / 2))

            #crosshair
            DISPLAY.blit(self.crosshair, (mouse_pos[0] - self.crosshair.get_width() / 2, mouse_pos[1] - self.crosshair.get_height() / 2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            SCREEN.blit(DISPLAY, (0, 0))

            pygame.display.update()

    def hit_player(self, sprite):
        self.player.x_vel, self.player.y_vel = calculate_kb(sprite.rect.center, CENTER, sprite.KB / 2)
        self.player.hit(sprite.DAMAGE)
        self.screen_shake = 20
        self.splash_texts.append([f'-{sprite.DAMAGE}', 256, self.player.rect.centerx+random.randint(-50, 50),
                                  self.player.rect.centery+random.randint(-50, 50), RED])

    def add_particles(self, pos, number, size, vel, speed, colours, tag):
        for i in range(number):
            self.particles.append(
                [list(pos), [random.randrange(vel) / 10 - vel/20, random.randrange(vel) / 10 - vel/20],
                 random.randrange(size), speed, random.choice(colours), tag])

    def add_hearts(self, pos, number):
        for i in range(number):
            heart = Consumable(pos[0], pos[1], 5, self.heart_img)
            self.consumable_group.append(heart)

    def play_sound(self, sound):
        if self.sound_on:
            sound.play()

if __name__ == '__main__':
    g = Game()
    g.start(True)
