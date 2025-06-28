import pygame
from constants import *

class InputField:
    def __init__(self, x, y, width, height, placeholder="", max_length=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = pygame.font.Font(None, FONT_MEDIUM)
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif len(self.text) < self.max_length and event.unicode.isprintable():
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
    
    def update(self, dt):
        """Update cursor blinking"""
        self.cursor_timer += dt
        if self.cursor_timer >= 500:  # Blink every 500ms
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen):
        """Draw the input field"""
        # Background
        bg_color = COLORS['white_piece'] if self.active else COLORS['button']
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, COLORS['grid_lines'], self.rect, 2)
        
        # Text or placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = COLORS['grid_lines'] if self.text else COLORS['text']
        
        text_surface = self.font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)
        
        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = text_rect.x + self.font.size(self.text[:self.cursor_pos])[0]
            cursor_y = text_rect.top
            pygame.draw.line(screen, COLORS['grid_lines'], 
                           (cursor_x, cursor_y), (cursor_x, cursor_y + text_rect.height), 2)
    
    def get_text(self):
        return self.text
    
    def set_text(self, text):
        self.text = text[:self.max_length]
        self.cursor_pos = len(self.text)
    
    def clear(self):
        self.text = ""
        self.cursor_pos = 0

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.font = pygame.font.Font(None, FONT_MEDIUM)
    
    def handle_event(self, event):
        """Handle button events"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return self.action
        return None
    
    def draw(self, screen):
        """Draw the button"""
        color = COLORS['button_hover'] if self.hovered else COLORS['button']
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['grid_lines'], self.rect, 2)
        
        text_surface = self.font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class MessageBox:
    def __init__(self, message, message_type="info"):
        self.message = message
        self.type = message_type  # "info", "error", "success"
        self.visible = False
        self.timer = 0
        self.duration = 3000  # 3 seconds
        self.font = pygame.font.Font(None, FONT_SMALL)
    
    def show(self, message, message_type="info"):
        self.message = message
        self.type = message_type
        self.visible = True
        self.timer = 0
    
    def update(self, dt):
        if self.visible:
            self.timer += dt
            if self.timer >= self.duration:
                self.visible = False
    
    def draw(self, screen, x, y):
        if not self.visible:
            return
        
        # Choose color based on type
        if self.type == "error":
            bg_color = (200, 50, 50)
        elif self.type == "success":
            bg_color = (50, 200, 50)
        else:
            bg_color = COLORS['button']
        
        text_surface = self.font.render(self.message, True, COLORS['text'])
        padding = 10
        rect = pygame.Rect(x - padding, y - padding, 
                          text_surface.get_width() + 2*padding, 
                          text_surface.get_height() + 2*padding)
        
        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, COLORS['grid_lines'], rect, 2)
        screen.blit(text_surface, (x, y))