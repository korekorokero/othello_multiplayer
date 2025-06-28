import pygame
from constants import *

class ScreenHeader:
    def __init__(self, title, subtitle=""):
        self.title = title
        self.subtitle = subtitle
        self.font_title = pygame.font.Font(None, FONT_LARGE)
        self.font_subtitle = pygame.font.Font(None, FONT_MEDIUM)
    
    def draw(self, screen, screen_width):
        """Draw the screen header"""
        # Title
        title_surface = self.font_title.render(self.title, True, COLORS['text'])
        title_rect = title_surface.get_rect(center=(screen_width // 2, 60))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        if self.subtitle:
            subtitle_surface = self.font_subtitle.render(self.subtitle, True, COLORS['text'])
            subtitle_rect = subtitle_surface.get_rect(center=(screen_width // 2, 90))
            screen.blit(subtitle_surface, subtitle_rect)

class BackButton:
    def __init__(self, x=20, y=20):
        self.rect = pygame.Rect(x, y, 80, 30)
        self.font = pygame.font.Font(None, FONT_SMALL)
        self.hovered = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return "back"
        return None
    
    def draw(self, screen):
        color = COLORS['button_hover'] if self.hovered else COLORS['button']
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['grid_lines'], self.rect, 2)
        
        text_surface = self.font.render("← Back", True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)