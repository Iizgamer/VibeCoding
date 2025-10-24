# ALL of the below has been written by AI. Images were made by me though, if that wasn't obvious.

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
        self.flash_timer = 0
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))
            except Exception as e:
                print(f"Error loading image for {name}: {e}")

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect.topleft)
            if self.flash_timer > 0:
                overlay = pygame.Surface((CARD_WIDTH,CARD_HEIGHT), pygame.SRCALPHA)
                overlay.fill((255,255,0,100))
                screen.blit(overlay, self.rect.topleft)
                self.flash_timer -= 1
        else:
            color = (255,0,0) if self.is_enemy else (0,0,255) if self.pos=="hand" else (0,255,0) if self.pos=="in-play" else (50,50,50)
            if self.flash_timer > 0:
                color = (255,255,0)
                self.flash_timer -=1
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, (255,255,255), self.rect, 2)

        # Draw text with shadow
        font = pygame.font.SysFont(None, 24)
        text_color = (255, 255, 0)
        shadow_color = (0, 0, 0)
        shadow_name = font.render(f"{self.name}", True, shadow_color)
        screen.blit(shadow_name, (self.rect.x+6, self.rect.y+6))
        name_text = font.render(f"{self.name}", True, text_color)
        screen.blit(name_text, (self.rect.x+5, self.rect.y+5))
        shadow_stats = font.render(f"HP:{self.hp} ATK:{self.attack}", True, shadow_color)
        screen.blit(shadow_stats, (self.rect.x+6, self.rect.y+26))
        stats_text = font.render(f"HP:{self.hp} ATK:{self.attack}", True, text_color)
        screen.blit(stats_text, (self.rect.x+5, self.rect.y+25))

class Player:
    def __init__(self):
        self.hp = 14
        self.deck = []
        self.hand = []
        self.coins = 0
        self.extra_draw = 0

class Enemy:
    def __init__(self):
        self.in_play = []

# --- Initialize ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Generic Card Game")
clock = pygame.time.Clock()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Music Setup ---
music_path = os.path.join(BASE_DIR, "music.mp3")
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)  # -1 means loop forever
pygame.mixer.music.set_volume(0.5)  # optional: sets volume to 50%

player = Player()
enemy = Enemy()
ai = OverlordAI()
rounds_completed = 0
in_shop = False
shop_selected = {"atk":0,"hp":0,"draw":0}
enemy_last_in_play = []

# --- Functions ---
def setup_enemy():
    round_multiplier = 1 + rounds_completed * 0.2
    enemies = [
        Card("Treyvon", hp=int(2 * round_multiplier), attack=2, is_enemy=True, image_path=os.path.join(BASE_DIR, "images", "treyvon.png")),
        Card("Stonks", hp=int(3 * round_multiplier), attack=1, is_enemy=True, image_path=os.path.join(BASE_DIR, "images", "stonks.png")),
        Card("JD Vance", hp=int(1 * round_multiplier), attack=1, is_enemy=True, image_path=os.path.join(BASE_DIR, "images", "vance.png"))
    ]
    for c in enemies:
        c.pos = "in-play"
    return enemies

def update_positions():
    hand_index = 0
    for card in player.hand:
        if card.pos=="hand":
            card.rect.x = 50 + hand_index*(CARD_WIDTH+20)
            card.rect.y = HAND_Y
            hand_index += 1
        elif card.pos=="in-play":
            card.rect.x = 150 + hand_index*(CARD_WIDTH+20)
            card.rect.y = INPLAY_Y
    for idx, card in enumerate(enemy.in_play):
        card.rect.x = 150 + idx*(CARD_WIDTH+20)
        card.rect.y = ENEMY_Y

def play_card(card):
    card.pos="in-play"
    ai.say_random()
    enemy_turn()
    player_attack()

def draw_card():
    # If deck is empty, shuffle non-in-play cards from hand back into deck
    if not player.deck:
        to_shuffle = [c for c in player.hand if c.pos != "in-play"]
        if to_shuffle:
            random.shuffle(to_shuffle)
            for c in to_shuffle:
                c.pos="deck"
                player.deck.append(c)
                player.hand.remove(c)
        else:
            print("No more cards to draw!")
            return

    c = player.deck.pop(0)
    c.pos="hand"
    player.hand.append(c)
    print(f"Drew {c.name}")

    ai.say_random()
    enemy_turn()
    player_attack()

# --- NEW: draw card silently for extra draws ---
def draw_card_silent():
    if not player.deck:
        to_shuffle = [c for c in player.hand if c.pos != "in-play"]
        if to_shuffle:
            random.shuffle(to_shuffle)
            for c in to_shuffle:
                c.pos="deck"
                player.deck.append(c)
                player.hand.remove(c)
        else:
            print("No more cards to draw!")
            return

    c = player.deck.pop(0)
    c.pos="hand"
    player.hand.append(c)
    print(f"Silently drew {c.name}")

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
    global enemy_last_in_play
    for card in [c for c in player.hand if c.pos=="in-play"]:
        if enemy.in_play:
            target = enemy.in_play[0]
            target.hp -= card.attack
            target.flash_timer=5
            print(f"{card.name} attacks {target.name} for {card.attack}! HP now {target.hp}")
            if target.hp <=0:
                print(f"{target.name} defeated!")
                enemy_last_in_play.append({'name': target.name, 'coins': max(1, target.attack)})
                enemy.in_play.remove(target)

def start_shop():
    global in_shop, shop_selected, enemy_last_in_play
    in_shop = True
    shop_selected = {"atk":0,"hp":0,"draw":0}
    player.coins += sum(c['coins'] for c in enemy_last_in_play)
    enemy_last_in_play.clear()
    print(f"Entering shop with {player.coins} coins!")

def apply_shop():
    global in_shop
    player.extra_draw += shop_selected["draw"]
    for c in player.deck + player.hand:
        c.attack += shop_selected["atk"]
        c.hp += shop_selected["hp"]
    in_shop = False
    print(f"Shop applied: {shop_selected}")

def start_next_round():
    global enemy, rounds_completed
    rounds_completed += 1

    # Recycle cards in hand back into deck
    to_recycle = [c for c in player.hand if not c.is_dead]
    for c in to_recycle:
        c.pos = "deck"
        player.deck.append(c)
        player.hand.remove(c)

    enemy.in_play = setup_enemy()

    for _ in range(player.extra_draw):
        draw_card_silent()  # EXTRA DRAW WITHOUT SPENDING A TURN

    print(f"Starting round {rounds_completed + 1}!")

# --- Initial Setup ---
for i in range(10):
    img_path = os.path.join(BASE_DIR, "images", f"card{i}.png")
    c = Card(f"Card{i}", hp=2+i, attack=1+i, image_path=img_path)
    player.deck.append(c)

for _ in range(3):
    c = player.deck.pop(0)
    c.pos="hand"
    player.hand.append(c)

enemy.in_play = setup_enemy()

draw_button_rect = pygame.Rect(SCREEN_WIDTH-BUTTON_WIDTH-20, SCREEN_HEIGHT-BUTTON_HEIGHT-20, BUTTON_WIDTH, BUTTON_HEIGHT)
shop_buttons = {
    "atk": pygame.Rect(150, 200, 200, 50),
    "hp": pygame.Rect(150, 300, 200, 50),
    "draw": pygame.Rect(150, 400, 200, 50),
    "confirm": pygame.Rect(500, 500, 150, 50)
}

# --- Main Loop ---
running=True
while running:
    screen.fill((0,0,0))

    if in_shop:
        font = pygame.font.SysFont(None,36)
        screen.blit(font.render(f"Coins: {player.coins}", True, (255,255,0)), (20,20))
        pygame.draw.rect(screen,(150,150,250),shop_buttons["atk"])
        pygame.draw.rect(screen,(150,150,250),shop_buttons["hp"])
        pygame.draw.rect(screen,(150,150,250),shop_buttons["draw"])
        pygame.draw.rect(screen,(100,255,100),shop_buttons["confirm"])
        font2 = pygame.font.SysFont(None,28)
        screen.blit(font2.render(f"Increase ATK (+1) [{shop_selected['atk']}]", True, (0,0,0)), (shop_buttons["atk"].x+5, shop_buttons["atk"].y+10))
        screen.blit(font2.render(f"Increase HP (+1) [{shop_selected['hp']}]", True, (0,0,0)), (shop_buttons["hp"].x+5, shop_buttons["hp"].y+10))
        screen.blit(font2.render(f"Extra Draw (+1) [{shop_selected['draw']}]", True, (0,0,0)), (shop_buttons["draw"].x+5, shop_buttons["draw"].y+10))
        screen.blit(font2.render("Confirm", True, (0,0,0)), (shop_buttons["confirm"].x+25, shop_buttons["confirm"].y+10))
    else:
        update_positions()
        for card in player.hand + enemy.in_play:
            card.draw(screen)
        pygame.draw.rect(screen,(200,200,200),draw_button_rect)
        pygame.draw.rect(screen,(255,255,255),draw_button_rect,2)
        font = pygame.font.SysFont(None,28)
        text = font.render("Draw Card", True,(0,0,0))
        screen.blit(text,(draw_button_rect.x+10,draw_button_rect.y+10))
        font2 = pygame.font.SysFont(None,36)
        screen.blit(font2.render(f"Player HP: {player.hp}", True,(255,255,255)),(20,20))
        enemy_hp_total = sum(c.hp for c in enemy.in_play)
        screen.blit(font2.render(f"Enemy HP: {enemy_hp_total}", True,(255,0,0)),(SCREEN_WIDTH-200,20))
        font3 = pygame.font.SysFont(None, 28)
        screen.blit(font3.render(f"AI: {ai.current_message}", True, (200,200,255)), (SCREEN_WIDTH//2-220, 13))

    # Events
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        elif event.type==pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if in_shop:
                if shop_buttons["atk"].collidepoint(pos) and player.coins >=2:
                    shop_selected["atk"] +=1
                    player.coins -=2
                elif shop_buttons["hp"].collidepoint(pos) and player.coins >=2:
                    shop_selected["hp"] +=1
                    player.coins -=2
                elif shop_buttons["draw"].collidepoint(pos) and player.coins >=3:
                    shop_selected["draw"] +=1
                    player.coins -=3
                elif shop_buttons["confirm"].collidepoint(pos):
                    apply_shop()
                    start_next_round()
            else:
                for card in player.hand:
                    if card.pos=="hand" and card.rect.collidepoint(pos):
                        play_card(card)
                        break
                if draw_button_rect.collidepoint(pos):
                    draw_card()

    # Check game over / next round
    if not in_shop:
        if player.hp <=0:
            font3 = pygame.font.SysFont(None,60)
            screen.blit(font3.render("GAME OVER!", True,(255,0,0)),(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running=False
        elif not enemy.in_play:
            start_shop()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
