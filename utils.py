import pygame
from math import hypot
from os import listdir

#size
WIDTH, HEIGHT = 1500, 900
CENTER = (WIDTH/2, HEIGHT/2)

#other
TINT_FADE = 15

#colour
WHITE = (255, 255, 255)
BUBBLE_BLUE = (0, 191, 255)
OCEAN_BLUE = (0, 0, 60)
PLASMA_GREEN = (33, 187, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 115, 59)
YELLOW = (255, 255, 0)
DARK_GREY = (28, 28, 28)
LIGHT_GREY = (188, 188, 188)
BLACK = (0, 0, 0)

#font
PIXEL_FONT = 'assets/other/pixel_font.ttf'

def load_img(path, transparent=False, scale=None, rotate=None):
    img = pygame.image.load('assets/img/'+path)

    if scale:
        img = pygame.transform.scale_by(img, scale)

    if rotate:
        img = pygame.transform.rotate(img, rotate)

    if transparent:
        img = img.convert_alpha()
    else:
        img = img.convert()

    return img

def load_imgs(path, transparent=False, scale=None, rotate=None):
    images = []

    for file in listdir(f'assets/img/{path}'):
        img = load_img(f'{path}/{file}', transparent, scale, rotate)
        images.append(img)

    return images

def load_sound(path, volume=None):
    sound = pygame.mixer.Sound('assets/sound/'+path)
    if volume:
        sound.set_volume(volume)

    return sound

def draw_text(text, font, colour, x, y, size, surf, center=False, opacity=None):
    font = pygame.font.Font(font, size)
    img = font.render(text, True, colour)
    if opacity:
        img.set_alpha(opacity)

    if center:
        surf.blit(img, (x-img.get_width()/2, y-img.get_height()/2))
    else:
        surf.blit(img, (x, y))

def calculate_kb(pos1, pos2, power):
    #get pos difference between mouse and player
    x, y = pos1[0] - pos2[0], pos1[1] - pos2[1]

    #calculate ratio
    total = abs(x) + abs(y)
    base = power/total if total else 0

    return base*x, base*y

def calculate_hypot(pos1, pos2):
    x, y = pos1[0] - pos2[0], pos1[1] - pos2[1]
    return hypot(x, y)
