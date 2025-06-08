import pygame
from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square
import sys

class Game:

    def __init__(self, screen):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.game_over = False
        self.check_message = ""
        self.check_message_time = 0
        self.font = pygame.font.SysFont('Arial', 32, bold=True)
        self.screen = screen
    
    def show_bg(self, surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

                if col == 0:
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    surface.blit(lbl, lbl_pos)

                if row == 7:
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece
            
            for move in piece.moves:
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            color = (180, 180, 180)
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect, width=3)

    def show_check_message(self, surface):
        if self.check_message and pygame.time.get_ticks() - self.check_message_time < 3000:
            text = self.font.render(self.check_message, True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH//2, 30))
            surface.blit(text, text_rect)

    def show_game_over_popup(self):
        pygame.time.delay(500)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        popup_width, popup_height = 400, 200
        popup = pygame.Surface((popup_width, popup_height))
        popup.fill((240, 240, 240))
        pygame.draw.rect(popup, (0, 0, 0), (0, 0, popup_width, popup_height), 3)
        
        title_font = pygame.font.SysFont('Arial', 36, bold=True)
        text_font = pygame.font.SysFont('Arial', 24)
        
        title = title_font.render("Game Over!", True, (255, 0, 0))
        winner = 'Brancas' if self.next_player == 'black' else 'Pretas'
        message = text_font.render(f"{winner} ganharam por xeque-mate!", True, (0, 0, 0))
        instruction = text_font.render("Clique para reiniciar", True, (0, 0, 0))
        
        popup.blit(title, (popup_width//2 - title.get_rect().width//2, 30))
        popup.blit(message, (popup_width//2 - message.get_rect().width//2, 80))
        popup.blit(instruction, (popup_width//2 - instruction.get_rect().width//2, 130))
        
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(popup, (WIDTH//2 - popup_width//2, HEIGHT//2 - popup_height//2))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    self.reset()

    def move(self, piece, move):
        initial = move.initial
        final = move.final

        self.board.move(piece, move)

        if isinstance(piece, Pawn):
            self.board.check_promotion(piece, final)

        if self.board.is_checkmate(self.next_player):
            self.check_message = f"Xeque-mate! {'Brancas' if self.next_player == 'black' else 'Pretas'} ganharam!"
            self.check_message_time = pygame.time.get_ticks()
            self.game_over = True
            self.show_game_over_popup()
        elif self.board.is_check(self.next_player):
            self.check_message = f"Xeque para {'brancas' if self.next_player == 'black' else 'pretas'}!"
            self.check_message_time = pygame.time.get_ticks()
        
        self.next_turn()

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()  
        self.dragger = Dragger()  
        self.game_over = False
        self.check_message = ""
        self.check_message_time = 0

    def check_game_over(self):
        if self.board.is_checkmate(self.next_player):
            self.game_over = True
            self.show_game_over_popup()
        elif self.board.is_check(self.next_player):
            self.check_message = f"Xeque para {'brancas' if self.next_player == 'black' else 'pretas'}!"
            self.check_message_time = pygame.time.get_ticks()