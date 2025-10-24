import pygame
import random
import sys
import os

# --- AI Overlord ---
class OverlordAI:
    def __init__(self):
        self.messages = [
            "You again? Wonderful...",
            "Play faster, human.",
            "Oh great, another card. I'm *thrilled*.",
            "Maybe you’ll win this time. Doubtful.",
            "I would’ve played a better card.",
            "You call that a strategy?",
            "Hurry up before I fall asleep.",
            "You're still here? Impressive. And sad.",
            "Even the 'Meme' card is doing better than you."
        ]
        self.current_message = "Welcome to your doom, player."

    def say_random(self):
        self.current_message = random.choice(self.messages)

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARD_WIDTH = 100
CARD_HEIGHT = 150
HAND_Y = SCREEN_HEIGHT - CARD_HEIGHT - 20
INPLAY_Y = SCREEN_HEIGHT//2 - CARD_HEIGHT//2
ENEMY_Y = 50
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40

# --- Classes ---
class Card:
    def __init__(self, name, hp, attack, is_enemy=False, image_path=None):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.pos = "deck"
        self.rect = pygame.Rect(0,0,CARD_WIDTH,CARD_HEIGHT)
        self.is_enemy = is_enemy
        self.is_dead = False
        self.flash_timer = 0  # For damage flash
        self.image = None

        # Load image if provided
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))
            except Exception as e:
                print(f"Error loading image for {name}: {e}")

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect.topleft)
            # Flash effect: overlay a yellow rectangle if damaged
            if self.flash_timer > 0:
                overlay = pygame.Surface((CARD_WIDTH,CARD_HEIGHT), pygame.SRCALPHA)
                overlay.fill((255,255,0,100))  # semi-transparent yellow
                screen.blit(overlay, self.rect.topleft)
                self.flash_timer -= 1
        else:
            # Fallback colored rectangle
            if self.is_enemy:
                color = (255,0,0) if not self.is_dead else (100,0,0)
            else:
                if self.pos=="hand":
                    color = (0,0,255)
                elif self.pos=="in-play":
                    color = (0,255,0)
                else:
                    color = (50,50,50)
            if self.flash_timer > 0:
                color = (255,255,0)
                self.flash_timer -=1
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, (255,255,255), self.rect, 2)

        # Draw text with shadow
        font = pygame.font.SysFont(None, 24)
        text_color = (255, 255, 0)  # bright yellow
        shadow_color = (0, 0, 0)    # black shadow

        # Name
        shadow_name = font.render(f"{self.name}", True, shadow_color)
        screen.blit(shadow_name, (self.rect.x+6, self.rect.y+6))
        name_text = font.render(f"{self.name}", True, text_color)
        screen.blit(name_text, (self.rect.x+5, self.rect.y+5))

        # HP and ATK
        shadow_stats = font.render(f"HP:{self.hp} ATK:{self.attack}", True, shadow_color)
        screen.blit(shadow_stats, (self.rect.x+6, self.rect.y+26))
        stats_text = font.render(f"HP:{self.hp} ATK:{self.attack}", True, text_color)
        screen.blit(stats_text, (self.rect.x+5, self.rect.y+25))

class Player:
    def __init__(self):
        self.hp = 10
        self.deck = []
        self.hand = []

class Enemy:
    def __init__(self):
        self.in_play = []

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rogue-like Card Game")
clock = pygame.time.Clock()

# Base directory for image loading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

player = Player()
enemy = Enemy()
ai = OverlordAI()

# Create player deck (6 cards) with images
for i in range(6):
    img_path = os.path.join(BASE_DIR, "images", f"card{i}.png")
    c = Card(f"Card{i}", hp=2+i, attack=1+i, image_path=img_path)
    player.deck.append(c)

# Draw 3 cards
for _ in range(3):
    c = player.deck.pop(0)
    c.pos="hand"
    player.hand.append(c)

# Special enemies with images
special_enemies = [
    Card("Treyvon", hp=2, attack=2, is_enemy=True, image_path=os.path.join(BASE_DIR, "images", "treyvon.png")),
    Card("Stonks", hp=4, attack=2, is_enemy=True, image_path=os.path.join(BASE_DIR, "images", "stonks.png")),
    Card("JD Vance", hp=3, attack=1, is_enemy=True, image_path=os.path.join(BASE_DIR, "images", "vance.png"))
]

for c in special_enemies:
    c.pos = "in-play"
    enemy.in_play.append(c)

# Draw button
draw_button_rect = pygame.Rect(SCREEN_WIDTH-BUTTON_WIDTH-20, SCREEN_HEIGHT-BUTTON_HEIGHT-20, BUTTON_WIDTH, BUTTON_HEIGHT)

# --- Functions ---
def update_positions():
    # Player hand
    hand_index = 0
    for card in player.hand:
        if card.pos=="hand":
            card.rect.x = 50 + hand_index*(CARD_WIDTH+20)
            card.rect.y = HAND_Y
            hand_index += 1
        elif card.pos=="in-play":
            card.rect.x = 150 + hand_index*(CARD_WIDTH+20)
            card.rect.y = INPLAY_Y
    # Enemy cards
    for idx, card in enumerate(enemy.in_play):
        card.rect.x = 150 + idx*(CARD_WIDTH+20)
        card.rect.y = ENEMY_Y

def play_card(card):
    card.pos="in-play"
    ai.say_random()
    enemy_turn()
    player_attack()

def draw_card():
    if player.deck:
        c = player.deck.pop(0)
        c.pos="hand"
        player.hand.append(c)
        print(f"Drew {c.name}")
    else:
        print("Deck empty!")
    ai.say_random()
    enemy_turn()
    player_attack()

def enemy_turn():
    if not enemy.in_play:
        return
    for card in enemy.in_play:
        player_inplay = [c for c in player.hand if c.pos=="in-play"]
        if player_inplay:
            target = random.choice(player_inplay)
            target.hp -= card.attack
            target.flash_timer = 5
            print(f"{card.name} attacks {target.name}! HP now {target.hp}")
            if target.hp <=0:
                print(f"{target.name} is defeated!")
                player.hand.remove(target)
        else:
            player.hp -= card.attack
            print(f"{card.name} attacks player! Player HP now {player.hp}")

def player_attack():
    for card in [c for c in player.hand if c.pos=="in-play"]:
        if enemy.in_play:
            target = enemy.in_play[0]
            target.hp -= card.attack
            target.flash_timer=5
            print(f"{card.name} attacks {target.name} for {card.attack}! HP now {target.hp}")
            if target.hp<=0:
                print(f"{target.name} defeated!")
                enemy.in_play.remove(target)

# --- Main Loop ---
running=True
while running:
    screen.fill((0,0,0))
    update_positions()

    # Events
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        elif event.type==pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Card clicks
            for card in player.hand:
                if card.pos=="hand" and card.rect.collidepoint(pos):
                    play_card(card)
                    break
            # Draw button
            if draw_button_rect.collidepoint(pos):
                draw_card()

    # Draw cards
    for card in player.hand + enemy.in_play:
        card.draw(screen)

    # Draw button
    pygame.draw.rect(screen,(200,200,200),draw_button_rect)
    pygame.draw.rect(screen,(255,255,255),draw_button_rect,2)
    font = pygame.font.SysFont(None,28)
    text = font.render("Draw Card", True,(0,0,0))
    screen.blit(text,(draw_button_rect.x+10,draw_button_rect.y+10))

    # HP Display
    font2 = pygame.font.SysFont(None,36)
    screen.blit(font2.render(f"Player HP: {player.hp}", True,(255,255,255)),(20,20))
    enemy_hp_total = sum(c.hp for c in enemy.in_play)
    screen.blit(font2.render(f"Enemy HP: {enemy_hp_total}", True,(255,0,0)),(SCREEN_WIDTH-200,20))

    # AI Overlord Message
    font3 = pygame.font.SysFont(None, 28)
    screen.blit(font3.render(f"AI: {ai.current_message}", True, (200,200,255)), (SCREEN_WIDTH//2-220, 13))

    # Game over check
    if player.hp<=0:
        font3 = pygame.font.SysFont(None,60)
        screen.blit(font3.render("GAME OVER!", True,(255,0,0)),(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running=False
    elif not enemy.in_play:
        font3 = pygame.font.SysFont(None,60)
        screen.blit(font3.render("YOU WIN!", True,(0,255,0)),(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running=False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
