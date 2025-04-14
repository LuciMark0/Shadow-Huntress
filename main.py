import random
import pgzrun

WIDTH = 960
HEIGHT = 540

backgrounds = [Actor('bg0'), Actor('bg1'), Actor('bg2'), Actor('bg3'), Actor('bg4'), Actor('bg5'), Actor('bg6')]
backgroundsSpeed = [0.15, 0.30, 0.45, 0.6, 0.85, 1.7, 2.75]
scroll_bgs  = [0] * len(backgrounds)  

sound_on = True
menu_state = "main"  

play_button = Rect(430, 230, 100, 40)  
sound_button = Rect(380, 280, 200, 40)  
exit_button = Rect(450, 330, 60, 40)

button_color = (169, 169, 169)

class Player(Actor):
    def __init__(self, image):
        super().__init__(image)
        self.x = 480
        self.y = 480
        self.health = 3
        self.speed = 2.5
        self.state = "idle"
        self.old_state = "idle"
        self.runWay = 1  # 1 for right, -1 for left
        self.attackChain = 0
        self.set_frameTimers()

    def set_frameTimers(self):
        self.idle_frameTimer = 0  
        self.idle_frameDuration = 6
        self.idle_frame = 0

        self.run_frameTimer = 0
        self.run_frameDuration = 6
        self.run_frame = 0

        self.dash_frameTimer = 0
        self.dash_frameDuration = 6
        self.dash_frame = 0

        self.attack_frameTimer = 0
        self.attackh_frameDurations = [6, 5, 4, 3, 5]
        self.attack_frameDurations = [6, 4, 8, 5, 5]
        self.attack_frame = 0

    
    def check_stateChange(self):
        if self.state != self.old_state:
            self.old_state = self.state
            if self.state == "attack":
                self.attack_frame = 0
                self.attack_frameTimer = 0
            elif self.state == "run":
                self.run_frame = 0
                self.run_frameTimer = 0
            elif self.state == "idle":
                self.idle_frame = 0
                self.idle_frameTimer = 0

    def move(self, dx):
        self.x += dx


    def idle_anim(self):
        self.idle_frameTimer += 1
        if self.idle_frameTimer >= self.idle_frameDuration:
            self.idle_frameTimer = 0
            self.idle_frame += 1
            if self.idle_frame > 11:
                self.idle_frame = 0
            if self.runWay == 1:
                self.image = f'playeridle{self.idle_frame}'
            else:
                self.image = f'playeridlel{self.idle_frame}'

    def run_anim(self):
        self.run_frameTimer += 1
        if self.run_frameTimer >= self.run_frameDuration:
            self.run_frameTimer = 0
            self.run_frame += 1
            if self.run_frame > 7:
                self.run_frame = 0
            if self.runWay == 1:
                self.image = f'playerrun{self.run_frame}'
            else:
                self.image = f'playerrunl{self.run_frame}'

    def dash_anim(self):
        self.dash_frameTimer += 1
        if self.dash_frameTimer >= self.dash_frameDuration:
            self.dash_frameTimer = 0
            self.dash_frame += 1
            if self.dash_frame > 3:
                self.dash_frame = 0
                self.state = "idle"
                return
            if self.dash_frame == 2:
                if self.runWay == 1:
                    self.x += 200
                else:
                    self.x -= 200
            if self.runWay == 1:
                self.image = f'playerdash{self.dash_frame}'
            else:
                self.image = f'playerdashl{self.dash_frame}'
    
    
    def attack_anim(self):
        nextImageName = "playerattackh" if self.attackChain == 0 else "playerattack"
        nextImageName += "l" if self.runWay == -1 else ""
        currentFrameDuration = self.attackh_frameDurations if self.attackChain == 0 else self.attack_frameDurations

        self.attack_frameTimer += 1
        if self.attack_frameTimer >= currentFrameDuration[self.attack_frame]:
            self.attack_frameTimer = 0
            self.attack_frame += 1
            if self.attack_frame > 4:
                self.attack_frame = 0
                self.state = "idle"
                self.attackChain = 0 if self.attackChain == 1 else 1
                return
            if self.attackChain == 0 and self.attack_frame == 3:
                self.deal_damage()
            elif self.attackChain == 1 and self.attack_frame == 1:
                self.deal_damage()
            self.image = f'{nextImageName}{self.attack_frame}'
    
    def attack_sound(self):
        if not sound_on:
            return
        if self.attackChain == 0:
            sounds.playerattackh.set_volume(0.01)  
            sounds.playerattackh.play()
        else:
            sounds.playerattack.set_volume(0.01)  
            sounds.playerattack.play()

    def deal_damage(self):
        global active_enemies, menu_state
        self.attack_sound()
        for active_enemy in active_enemies:
            if self.get_attackbox().colliderect(active_enemy.get_hitbox()):
                active_enemy.health -= 10
                active_enemy.take_damage_anim()
                if active_enemy.health <= 0:
                    active_enemy.state = "dead"
                    if sound_on:
                        sounds.enemydeath.set_volume(0.025)
                        sounds.enemydeath.play()
                    if active_enemy == enemy:
                        active_enemies = [enemy1, enemy2]
                        if sound_on:
                            sounds.enemyspawn.set_volume(0.025)
                            sounds.enemyspawn.play()
                        return
                    active_enemies.remove(active_enemy)
                    if active_enemies == []:
                        menu_state = "Victory"
                    
        

    def take_damage_anim(self):
        self.image = "playerhit" if self.runWay == 1 else "playerhitl"

    def get_hitbox(self):
        return Rect((self.x - 10, self.y - 30), (25, 80))
    
    def get_attackbox(self):
        if self.runWay == 1:
            return Rect((self.x + 10, self.y - 10), (100, 30))
        else:
            return Rect((self.x - 110, self.y - 10), (100, 30))
    
    def take_damage(self):
        global menu_state
        self.health -= 1
        if self.health <= 0:
            menu_state = "gameover"
            
    
class Enemy(Actor):
    def __init__(self, image, posx=1000, posy=400):
        super().__init__(image)
        self.x = posx
        self.y = posy

        self.speed = 0.65
        self.max_health = 100
        self.health = 100

        self.state = "run"
        self.runWay = 1  # 1 for right, -1 for left
        self.attackCooldownMax = 2
        self.attackCooldown = 2
        self.canAttack = True
        self.attackType = 1

        self.set_frameTimers()

    def set_frameTimers(self):
        self.run_frameTimer = 0
        self.run_frameDuration = 6
        self.run_frame = 0

        self.attack_frameTimer = 0
        self.attackh_frameDurations = [6, 36, 3, 6, 6, 6, 6]
        self.attack_frameDurations = [12, 12, 12, 3, 6, 6, 3]
        self.attack_frame = 0

        self.hit_frameTimer = 0
        self.hit_frameDuration = 6

    def move(self, player_x):
        if self.x < player_x - 50:
            self.runWay = 1
            if player.state == "run":
                self.x += self.speed + player.speed if player.runWay == -1  else self.speed - player.speed
            else:
                self.x += self.speed
        elif self.x > player_x + 50:
            self.runWay = -1
            if player.state == "run":
                self.x -= self.speed + player.speed if player.runWay == 1 and player.state == "run" else self.speed - player.speed
            else:
                self.x -= self.speed
    
    def run_anim(self):
        self.move(player.x)
        self.run_frameTimer += 1
        if self.run_frameTimer >= self.run_frameDuration:
            self.run_frameTimer = 0
            self.run_frame += 1
            if self.run_frame > 13:
                self.run_frame = 0
            if self.runWay == 1:
                self.image = f'enemyrun{self.run_frame}'
            else:
                self.image = f'enemyrunl{self.run_frame}'
    
    def attack_anim(self):
        if self.state == "dead":
            return

        attackImageName = "enemyattackh" if self.attackType == 0 else "enemyattack"
        self.attack_frameTimer += 1
        if self.attack_frameTimer >= self.attack_frameDurations[self.attack_frame]:
            self.attack_frameTimer = 0
            self.attack_frame += 1
            if self.attack_frame > 6:
                self.attack_frame = 0
                if self.attackType == 2:
                    self.attackType = 0
                    return
                self.state = "run"
                self.canAttack = False
                self.attackCooldown = self.attackCooldownMax
                return
            if self.runWay == 1:
                self.image = f'{attackImageName}{self.attack_frame}'
            else:
                self.image = f'{attackImageName}l{self.attack_frame}'
            if self.attack_frame == 4 and self.get_attackbox().colliderect(player.get_hitbox()) and player.state != "dash": 
                player.take_damage()
                if player.state != "attack":
                    player.take_damage_anim()
    
    def take_damage_anim(self):
        self.image = "enemyhit" if self.runWay == 1 else "enemyhitl"

        if not sound_on:
            return
        sounds.enemyhit.set_volume(0.025)
        sounds.enemyhit.play()
                

    def get_hitbox(self):
        return Rect((self.x - 10, self.y - 10), (65, 100))
    
    def get_attackbox(self):
        rect_width = 200 if self.attackType != 0 else 300
        rect_xpadding = 100 if self.attackType != 0 else 300
        if self.runWay == 1:
            return Rect((self.x + (rect_xpadding - 100), self.y + 40), (rect_width, 30))
        else:
            return Rect((self.x - (rect_xpadding + 50), self.y + 40), (rect_width, 30))
    
    def draw_healthBar(self):
        # Bar position and size
        bar_width = 100
        bar_height = 10

        # Health percent
        health_ratio = self.health / self.max_health

        # Draw background (depleted health)
        screen.draw.filled_rect(Rect((self.x -30, self.y - 100), (bar_width, bar_height)), 'black')

        # Draw foreground (current health)
        current_width = int(bar_width * health_ratio)
        screen.draw.filled_rect(Rect((self.x -30, self.y - 100), (current_width, bar_height)), 'red')



def start():
    global player, enemy, enemy1, enemy2, active_enemies
    player = Player('playeridle0')
    enemy = Enemy('enemyrun0' )
    enemy1 = Enemy('enemyrun0' , 1000, 400)
    enemy2 = Enemy('enemyrun0' , -40, 400)

    active_enemies = [enemy]
    

start()

def draw():
    
    if menu_state == "main":
        screen.fill((0, 0, 0))

        screen.draw.text("Shadow Huntress", center=(480, 150), fontsize=50, color="white")
        
        screen.draw.filled_rect(play_button, button_color)
        screen.draw.text("Play", center=(480, 250), fontsize=30, color="black")
        
        screen.draw.filled_rect(sound_button, button_color)
        screen.draw.text("Sound: On" if sound_on else "Sound: Off", center=(480, 300), fontsize=30, color="black")
        
        screen.draw.filled_rect(exit_button, button_color)
        screen.draw.text("Exit", center=(480, 350), fontsize=30, color="black")
    
    elif menu_state == "game":
        screen.clear()
        
        for i in range(len(backgrounds)-1):
            backgrounds[i].x = scroll_bgs[i] % WIDTH
            screen.blit(backgrounds[i].image, (backgrounds[i].x - WIDTH, 0))
            screen.blit(backgrounds[i].image, (backgrounds[i].x, 0))
        
        player.draw()
       # screen.draw.filled_rect(player.get_attackbox(), (255, 0, 0, 0.5)) 
       # screen.draw.filled_rect(player.get_hitbox(), (255, 0, 0, 0.5))  # Draw hitbox for debugging

        for active_enemy in active_enemies:
            if active_enemy.state != "dead":
                active_enemy.draw()
                active_enemy.draw_healthBar()
                #screen.draw.filled_rect(active_enemy.get_hitbox(), (255, 0, 0, 0.5))
                #screen.draw.filled_rect(active_enemy.get_attackbox(), (255, 0, 0, 0.5))  # Draw attackbox for debugging

        backgrounds[-1].x = scroll_bgs[-1] % WIDTH
        screen.blit(backgrounds[-1].image, (backgrounds[-1].x - WIDTH, 0))
        screen.blit(backgrounds[-1].image, (backgrounds[-1].x, 0))

        for i in range(player.health):
            screen.blit("health0", (i * 50 + 10, 10))
    
    elif menu_state == "gameover":
        screen.fill((0, 0, 0))
        screen.draw.text("You Died", center=(480, 270), fontsize=50, color="red")
        screen.draw.text("Click to Exit", center=(480, 350), fontsize=30, color="red")
    
    elif menu_state == "Victory":
        screen.fill((0, 0, 0))
        screen.draw.text("You Win!", center=(480, 270), fontsize=50, color="white")
        screen.draw.text("Click to Exit", center=(480, 350), fontsize=30, color="white")


def update():
    global scroll_bgs
    
    player.check_stateChange()

    if not player.state == "attack" and not player.state == "dash":
        player.state = "idle"  # Default state

    if keyboard.a:  # Move left
        if not player.state == "attack" and not player.state == "dash":
            player.state = "run"
        player.runWay = -1
        if player.x > 0:
            player.x -= player.speed
        for i in range(len(backgrounds)):
            scroll_bgs[i] += backgroundsSpeed[i]

    if keyboard.d:  # Move right
        if not player.state == "attack" and not player.state == "dash":
            player.state = "run"
        player.runWay = 1
        if player.x < 960:
            player.x += player.speed
        for i in range(len(backgrounds)):
            scroll_bgs[i] -= backgroundsSpeed[i]
    
    if keyboard.lshift:  # Dash
        if not player.state == "attack" and not player.state == "dash":
            player.state = "dash"
            
    enemy_controller()
    
    
    if player.state == "attack":
        player.attack_anim()
    
    elif player.state == "dash":
        player.dash_anim()

    elif player.state == "run":
        player.run_anim()

    elif player.state == "idle":
        player.idle_anim()

def enemy_controller():
    for active_enemy in active_enemies:
        if active_enemy.state == "dead":
            continue

        active_enemy.attackCooldown -= 1 / 60
        if active_enemy.attackCooldown <= 0 and active_enemy.state != "attack":
            active_enemy.attackCooldown = active_enemy.attackCooldownMax
            active_enemy.canAttack = True
            #active_enemy.attackType = random.choice([1,1,1,1,2]) # Randomly choose attack type
        
        if active_enemy.canAttack:
            enemy_attackCheck(active_enemy)

        enemy_actions(active_enemy)       

def enemy_attackCheck(active_enemy):
    if active_enemy.canAttack and active_enemy.get_attackbox().colliderect(player.get_hitbox()):
        active_enemy.state = "attack"

def enemy_actions(active_enemy):
    if active_enemy.state == "run":
        active_enemy.run_anim()
            
    elif active_enemy.state == "attack":
        active_enemy.attack_anim()

def on_mouse_down(pos):
    global menu_state, boss_health, enemy
    if menu_state == "main":
        if play_button.collidepoint(pos):
            start_game()
        elif sound_button.collidepoint(pos):
            toggle_sound()
        elif exit_button.collidepoint(pos):
            exit_game()
    
    if menu_state == "game":
        if not player.state == "attack":
            player.state = "attack"

    if menu_state == "gameover" or menu_state == "Victory":
        exit_game()                   

def start_game():
    global menu_state
    menu_state = "game"
    if sound_on:
        sounds.ambient0.set_volume(0.05)  # Set the volume to 50%
        sounds.ambient0.play(-1)

        sounds.enemyspawn.set_volume(0.025)
        sounds.enemyspawn.play()


def toggle_sound():
    global sound_on
    sound_on = not sound_on

def exit_game():
    exit()


pgzrun.go()