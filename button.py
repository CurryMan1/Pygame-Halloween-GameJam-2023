import pygame

class Button:
    def __init__(self, x: int, y: int, image: pygame.surface.Surface):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.can_click = False

    def is_clicked(self, screen: pygame.surface.Surface):  #draws button too
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

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return clicked

class UpgradeButton(Button):
    pass