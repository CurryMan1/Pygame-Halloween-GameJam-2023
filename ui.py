import pygame
from utils import *

def get_box(width, height, border_width, fg, bg):
    box = pygame.surface.Surface((width, height))
    box.fill(bg)
    front = pygame.surface.Surface((width - border_width * 2, height - border_width*2))
    front.fill(fg)

    box.blit(front, (border_width, border_width))
    return box

class Button:
    def __init__(self, x: int, y: int, width: int=None, height: int=None, fg=None, bg=None, border_width=None,
                 text: str=None, text_size=None, text_colour=None, draw_text: bool=True, image: pygame.surface.Surface=None):
        self.text = text
        self.text_size = text_size
        self.text_colour = text_colour
        self.draw_text = draw_text
        if image:
            self.image = image
        else:
            self.image = get_box(width, height, border_width, fg, bg)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.can_click = False

    def is_clicked(self, surf: pygame.surface.Surface):  #draws button too
        clicked = False

        #makes button only give true ONCE (until released)
        if self.rect.collidepoint((pygame.mouse.get_pos())):
            if pygame.mouse.get_pressed()[0] == 0:
                self.can_click = True
                self.clicked = True
            else:
                if self.can_click and self.clicked:
                    clicked = True
                self.clicked = False
        else:
            self.can_click = False

        surf.blit(self.image, (self.rect.x, self.rect.y))
        if self.text and self.draw_text:
            draw_text(self.text, PIXEL_FONT, self.text_colour, self.rect.centerx, self.rect.centery, self.text_size, surf, True)

        return clicked

class UpgradeButton(Button):
    def __init__(self, x, y, text, price):
        image = get_box(200, 200, 2, DARK_GREY, LIGHT_GREY)
        super().__init__(x, y, text=text, text_size=25, text_colour=WHITE, image=image, draw_text=False)
        self.price = price
        self.heart_img = load_img('heart.png', True, 1.2)

    def is_clicked(self, surf):
        clicked = super().is_clicked(surf)
        draw_text(self.text, PIXEL_FONT, self.text_colour, self.rect.centerx, self.rect.top+20, self.text_size, surf, True)
        draw_text(str(self.price), PIXEL_FONT, self.text_colour, self.rect.left+40, self.rect.centery+10, 50, surf, True)

        surf.blit(self.heart_img, (self.rect.centerx+10, self.rect.centery-35))

        return clicked
