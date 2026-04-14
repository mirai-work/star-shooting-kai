import pyxel
import random
import math
import os

mapping = "03000000490b00004406000000000000,ASCII Game Controller,a:b0,b:b1,x:b3,y:b2,back:b8,start:b9,leftshoulder:b4,rightshoulder:b5,dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,platform:Windows,"
os.environ["SDL_GAMECONTROLLERCONFIG"] = mapping
# --- Constants ---
W, H = 160, 120
SCENE_TITLE, SCENE_PLAY, SCENE_PAUSE, SCENE_BOSS = 0, 1, 2, 3
SCENE_GAMEOVER, SCENE_STAGE_CLEAR, SCENE_ENDING = 4, 5, 6
SCENE_TUTORIAL = 7 
MAX_STAGE = 5
POWER_MAX = 4

class StarSoldier:
    def __init__(self):
        pyxel.init(W, H, title="STAR SHOTTER! KAI", fps=60)
        self.init_sound()
        self.stage_colors = {
            1: (7, 1), 2: (14, 5), 3: (10, 1), 4: (8, 0), 5: (7, 0)
        }
        self.scene = SCENE_TITLE
        self.gameover_timer = 0
        self.clear_timer = 0 
        self.scroll_y = 0    
        
        self.far_cloud = [(-10, 75), (40, 65), (90, 60)]
        self.near_cloud = [(10, 25), (70, 35), (120, 15)]
        self.space_stars = [[random.randint(0, W), random.randint(0, H), random.uniform(1.0, 2.5)] for _ in range(60)]
        
        self.command_index = 0
        self.command_list = ["UP", "UP", "DOWN", "DOWN", "LEFT", "RIGHT", "LEFT", "RIGHT"]
        
        self.m_index = 0
        self.m_list = ["B", "A", "B", "A", "B", "A", "UP", "DOWN", "UP", "DOWN"]
        self.muteki_enabled = False
        
        self.cheat_enabled = False
        self.used_cheats = 0
        self.high_score = 10000
        self.warp_effect = 0
        
        self.reset_all()
        pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def init_sound(self):
        # --- SE ---
        pyxel.sounds[0].set("G2G1", "P", "7", "F", 5)       # ショット
        pyxel.sounds[1].set("C2C1C0", "N", "742", "F", 10)  # 爆発
        pyxel.sounds[2].set("C3E3G3C4", "P", "6", "V", 15)  # アイテム取得
        pyxel.sounds[3].set("G3C4G3C4", "P", "3", "V", 10)  # 1UP・決定音
        # ★エンディング用（番号を60番台の空きへ変更）
        pyxel.sounds[4].set("C4 G3 A3 E3 F3 C3 F3 G3", "P", "7", "V", 15)
        pyxel.sounds[5].set("C3E3G3 R D3F3A3 R E3G3B3 R C3E3G3 R", "P", "4", "N", 15)
        pyxel.sounds[6].set("C2 C2 G1 G1 A1 A1 G1 G1", "T", "6", "N", 15)
        pyxel.sounds[7].set("C1 R C1 C1 G1 R C1 R", "N", "2", "F", 15)
        # --- BGMパーツ（オクターブ5番以上を削除済み） ---
        pyxel.sounds[10].set("C3 E3 G3 C4 G3 E3 C3 R", "P", "7531", "N", 10)
        pyxel.sounds[11].set("C2 C2 C2 C2 G1 G1 G1 G1", "T", "5", "N", 20)
        
        # 本編1面用 (旧12,13)
        pyxel.sounds[12].set("C4 C4 G3 G3 E4 E4 C4 C4 D4 D4 A3 A3 F4 F4 D4 D4", "P", "7531", "N", 5)
        pyxel.sounds[13].set("C1 C2 C1 C2 G0 G1 G0 G1 D1 D2 D1 D2 A0 A1 A0 A1", "T", "7", "N", 5)
        
        # 本編2面用
        pyxel.sounds[22].set("E4 G4 B3 D4 F4 A4 C4 E4", "S", "6421", "N", 5)
        pyxel.sounds[23].set("E1 R B0 R F1 R C1 R", "T", "6", "N", 5)
        
        # 本編3面用
        pyxel.sounds[24].set("G4 A4 B4 C4 B4 A4 G4 F4", "P", "5310", "V", 5)
        pyxel.sounds[25].set("G1 G1 D1 D1 A1 A1 E1 E1", "T", "5", "V", 5)
        
        # 本編4面用
        pyxel.sounds[26].set("A3 C4 E4 A4 G3 B3 D4 G4", "S", "7531", "S", 5)
        pyxel.sounds[27].set("A0 R G0 R F0 R E0 R", "T", "7", "S", 5)
        
        # 本編5面用
        pyxel.sounds[28].set("C4 G3 C4 E4 D4 A3 D4 F4 E4 B3 E4 G4 F4 C4 F4 A4", "P", "7777", "F", 5)
        pyxel.sounds[29].set("C1 C1 C1 C1 G1 G1 G1 G1", "T", "7", "N", 5)
        # 共通パーツ
        pyxel.sounds[14].set("C3E3G3C4 G3E3C3G2 D3F3A3D4 A3F3D3A2", "P", "4", "V", 5)
        pyxel.sounds[15].set("G1 R R R G1 R R R", "T", "7", "N", 5) # バスドラム
        pyxel.sounds[16].set("R R G1 R R R G1 R", "N", "60", "F", 5) # 鋭いスネア
        pyxel.sounds[17].set("C4E4G4B4 G4E4C4G3", "P", "7474", "V", 2)


        # ボス関連
        pyxel.sounds[30].set("A3 A#3 B3 C4 C#4 D4 D#4 E4", "P", "7", "S", 4)
        pyxel.sounds[31].set("A1 A1 A1 A1 G1 G1 G1 G1", "T", "7", "N", 4)
        pyxel.sounds[32].set("C4 C#4 D4 D#4 E4 F4 F#4 G4", "P", "7", "N", 2)
        pyxel.sounds[33].set("C2 R C2 R C2 R C2 R", "T", "7", "N", 2)
        
        # 演出用
        pyxel.sounds[40].set("C3 G2 D#2 C2 B1 G1 R R", "P", "76543210", "NNSSSSSS", 10)
        pyxel.sounds[41].set("C4E4G4C4 R C4E4G4C4 R C4E4G4C4 R R R", "P", "7654", "SSSS", 20)
        pyxel.sounds[42].set("G3B3D4G4 R G3B3D4G4 R G3B3D4G4 R R R", "S", "5432", "SSSS", 20)
        pyxel.sounds[43].set("C3 E3 G3 B3 D3 F3 A3 C4", "P", "6420", "V", 20)
        pyxel.sounds[44].set("C1E1G1B1 D1F1A1C2", "T", "4", "N", 20)
        pyxel.sounds[45].set("C2 R C2 R C2 R G1 R", "T", "7654", "NNNN", 20)
        pyxel.sounds[50].set("C3E3G3C4 E3G3B3E4", "P", "3", "V", 5)
        pyxel.sounds[51].set("C1 R D#1 R F1 R G1 R", "T", "5", "N", 40)
        pyxel.sounds[52].set("R R R R C2 C1 R R", "N", "4321", "FFFF", 20)
        pyxel.sounds[55].set("C3 E3 G3 C4 G3 E3 C3 R", "S", "2", "N", 20)
        pyxel.sounds[56].set("C2 R G1 R", "T", "3", "N", 20)
        pyxel.sounds[60].set("C4E4G4C4 G3B3D4G4 A3C4E4A4 G3B3D4G4", "P", "7654", "SSSS", 15)
        pyxel.sounds[61].set("C4 E4 G4 C4 G3 B3 D4 G4", "S", "4", "V", 15)
        pyxel.sounds[62].set("C2 R G1 R A1 R G1 R", "T", "7", "N", 15)
        pyxel.sounds[63].set("C1 R G0 R C1 R G0 R", "N", "5", "F", 15)
        

        # --- Music登録 ---
        pyxel.musics[0].set([10], [11], [50], [])# タイトル
        pyxel.musics[1].set([12], [13], [], []) # 道中
        pyxel.musics[2].set([30], [31], [], []) # ボス
        pyxel.musics[3].set([32], [33], [], []) # ボスピンチ
        pyxel.musics[4].set([40], [51], [52], [])   # ゲームオーバー
        pyxel.musics[5].set([60], [61], [62], [63]) # ステージクリア
        pyxel.musics[6].set([4], [5], [6], [7]) # ★エンディング（感動のフィナーレ）
        pyxel.musics[7].set([55], [56], [], []) # チュートリアル
        
    def reset_all(self):
        self.stage = 1; self.score = 0; self.lives = 3
        self.kill_count = 0; self.barrier_hp = 0
        self.scene_timer = 0
        self.used_cheats = 0 
        self.muteki_enabled = False
        self.cheat_enabled = False
        self.reset_stage_env()
        self.x, self.y = 80, 100
        self.respawn_player()
        self.stars = [[random.randint(0, W), random.randint(0, H), (random.random()*1.2+0.3)*0.6] for _ in range(60)]

    def reset_stage_env(self):
        self.frame = 0; self.stage_timer = 0; self.shots = []; self.enemy_shots = []
        self.enemies = []; self.capsules = []; self.explosions = []; self.ground_targets = []; self.boss = None

    def respawn_player(self):
        self.power = 1; self.inv_timer = 90; self.enemy_shots = []; self.barrier_hp = 0

    def check_any_button(self):
        for b in [pyxel.GAMEPAD1_BUTTON_A, pyxel.GAMEPAD1_BUTTON_B, pyxel.GAMEPAD1_BUTTON_X, pyxel.GAMEPAD1_BUTTON_Y]:
            if pyxel.btnp(b): return True
        return False

    def draw_planetary_surface(self, gx, gy, size, seed):
        old_seed = random.seed()
        random.seed(seed)
        for _ in range(3):
            cx = gx + random.randint(-4, 4)
            cy = gy + random.randint(-4, 4)
            r = random.randint(1, 2)
            pyxel.circ(cx, cy, r, 13)
            pyxel.pset(cx + 1, cy - 1, 6)
        for _ in range(2):
            lx = gx + random.randint(-5, 2)
            ly = gy + random.randint(-5, 5)
            pyxel.line(lx, ly, lx + 3, ly, 5)
        random.seed(old_seed)

    def update(self):
        key_pressed = None 
        for s in self.space_stars:
            s[1] += s[2]
            if s[1] > H: s[1] = 0; s[0] = random.randint(0, W)
        for s in self.stars:
            s[1] += s[2]
            if s[1] > H: s[1], s[0] = 0, random.randint(0, W)
        if not hasattr(self, 'scene_timer'): self.scene_timer = 0
        self.scene_timer += 1

        if self.scene in (SCENE_TITLE, SCENE_PAUSE, SCENE_GAMEOVER, SCENE_BOSS):
            key_pressed = None 
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP): key_pressed = "UP"
        elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): key_pressed = "DOWN"
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): key_pressed = "LEFT"
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): key_pressed = "RIGHT"
        elif pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B): key_pressed = "B"
        elif pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A): key_pressed = "A"

        cheat_just_activated = False
        if key_pressed:
            if key_pressed == self.command_list[self.command_index]:
                self.command_index += 1
                if self.command_index >= len(self.command_list):
                    limit_table = {1: 1, 2: 1, 3: 2, 4: 3, 5: 5}
                    limit = limit_table.get(self.stage, 1)
                    if self.used_cheats < limit:
                        pyxel.play(3, 2)
                        self.cheat_enabled = True
                        self.power, self.barrier_hp = POWER_MAX, 3
                        self.used_cheats += 1
                        cheat_just_activated = True
                    self.command_index = 0
            else:
                self.command_index = 1 if key_pressed == self.command_list[0] else 0
            
            if key_pressed == self.m_list[self.m_index]:
                self.m_index += 1
                if self.m_index >= len(self.m_list):
                    pyxel.play(3, 3)
                    self.muteki_enabled = not self.muteki_enabled
                    self.m_index = 0
                    cheat_just_activated = True
            else:
                self.m_index = 1 if key_pressed == self.m_list[0] else 0

        if cheat_just_activated:
            key_pressed = None

        if self.scene == SCENE_TITLE:
            if self.scene_timer == 1: self.cheat_enabled = False
            self.update_play_logic() 
            if self.cheat_enabled:
                if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                    self.stage = self.stage - 1 if self.stage > 1 else MAX_STAGE; pyxel.play(3, 3)
                elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                    self.stage = self.stage + 1 if self.stage < MAX_STAGE else 1; pyxel.play(3, 3)
            
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START): 
                self.handle_start_button()
            elif self.scene_timer > 840 or pyxel.btnp(pyxel.KEY_SPACE) or self.check_any_button():
                if not cheat_just_activated:
                    self.scene = SCENE_TUTORIAL; self.scene_timer = 0; pyxel.playm(7, loop=True)
                    
        elif self.scene == SCENE_TUTORIAL:
            self.update_play_logic()
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START): 
                self.handle_start_button()
            elif self.scene_timer > 420 or pyxel.btnp(pyxel.KEY_SPACE) or self.check_any_button():
                self.scene = SCENE_TITLE; self.scene_timer = 0; pyxel.playm(0, loop=True)

        elif self.scene == SCENE_STAGE_CLEAR:
            self.clear_timer += 1; self.next_stage()

        elif self.scene == SCENE_GAMEOVER:
            self.update_play_logic()
            if self.boss: self.update_boss()
            if self.score > self.high_score: self.high_score = self.score
            if self.scene_timer > 480: self.reset_all(); self.scene = SCENE_TITLE; pyxel.playm(0, loop=True)

        elif self.scene == SCENE_ENDING:
            self.scroll_y += 0.3
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START): 
                self.scene = SCENE_TITLE; self.scene_timer = 0; pyxel.playm(0, loop=True)

        elif self.scene in (SCENE_PLAY, SCENE_BOSS, SCENE_PAUSE):
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START): 
                self.handle_start_button()
            elif self.scene != SCENE_PAUSE: 
                self.update_play()
                if self.scene == SCENE_BOSS: self.update_boss()

    def handle_start_button(self):
        if self.scene in (SCENE_TITLE, SCENE_TUTORIAL):
            pyxel.play(2, 2)
            selected_stg, cheat_on = self.stage, self.cheat_enabled
            m_on = self.muteki_enabled 
            self.reset_all()
            self.stage, self.cheat_enabled, self.muteki_enabled = selected_stg, cheat_on, m_on
            if self.cheat_enabled: self.power, self.barrier_hp = POWER_MAX, 3
            
            # ステージに応じたBGMセット
            self.apply_stage_music()
            self.scene = SCENE_PLAY; pyxel.playm(1, loop=True)
        elif self.scene in (SCENE_PLAY, SCENE_BOSS): self.scene = SCENE_PAUSE; pyxel.stop(); pyxel.play(3, 3)
        elif self.scene == SCENE_PAUSE: 
            if self.boss: self.scene = SCENE_BOSS; pyxel.playm(2 if not self.boss["panic"] else 4, loop=True)
            else: self.scene = SCENE_PLAY; pyxel.playm(1, loop=True)

    def apply_stage_music(self):
        # 各ステージで使用する「メロディ」と「ベース」のSound番号
        music_map = {
            1: [12, 13], # Stage 1
            2: [22, 23], # Stage 2
            3: [24, 25], # Stage 3
            4: [26, 27], # Stage 4
            5: [28, 29]  # Stage 5
        }
        
        m_set = music_map.get(self.stage, [12, 13])
        
        # Music 1 (メインBGM) を構成するチャンネルを設定
        # ch0: メロディ, ch1: ベース, ch2: 共通サブメロ(14), ch3: ドラム(15,16)
        pyxel.musics[1].set([m_set[0]], [m_set[1]], [14], [15, 16])

    def update_play_logic(self):
        self.frame += 1
        curr_stg = self.stage if self.scene not in (SCENE_TITLE, SCENE_TUTORIAL) else 1
        if self.scene not in (SCENE_BOSS, SCENE_GAMEOVER):
            if self.frame % 166 == 0: 
                self.ground_targets.append({"x": random.randint(20, W-20), "y": -15, "hp": 5, "seed": random.randint(0, 999)})
            spawn_rate = max(5, int((35 - curr_stg * 6) / 0.6))
            if self.frame % spawn_rate == 0: 
                self.enemies.append({"x": random.randint(10, W-10), "y": -10, "type": random.choice(["sotta", "kappa", "calderon"]), "t": 0, "vx": 0, "vy": 0})
        self.update_entities()

    def update_play(self):
        self.stage_timer += 1
        if self.muteki_enabled: self.inv_timer = 90
        elif self.inv_timer > 0: self.inv_timer -= 1
            
        dx = (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) - (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT))
        dy = (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)) - (pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP))
        self.x = max(0, min(W-8, self.x + dx * 1.6 * 0.6)); self.y = max(0, min(H-8, self.y + dy * 1.6 * 0.6))
        shot_interval = int((12 if self.power == 1 else 6) / 0.6)
        if any(pyxel.btn(k) for k in [pyxel.KEY_Z, pyxel.KEY_X, pyxel.GAMEPAD1_BUTTON_A, pyxel.GAMEPAD1_BUTTON_B]):
            if pyxel.frame_count % shot_interval == 0: self.fire(); pyxel.play(3, 1)
        if self.scene == SCENE_PLAY:
            self.update_play_logic()
            if self.stage_timer > (1100 + self.stage * 100) / 0.6: self.init_boss()
        else: self.update_entities()

    def fire(self):
        if self.power >= 3:
            for ang in [-10, 0, 10, 170, 190]: self.shots.append([self.x+4, self.y, ang])
        elif self.power == 2:
            for ang in [-5, 5, 180]: self.shots.append([self.x+4, self.y, ang])
        else:
            for ang in [-5, 5]: self.shots.append([self.x+4, self.y, ang])

    def update_entities(self):
        for s in self.shots[:]:
            rad = math.radians(s[2]-90); s[0] += math.cos(rad)*6*0.6; s[1] += math.sin(rad)*6*0.6
            if not (-10 < s[1] < H+10 and -10 < s[0] < W+10):
                if s in self.shots: self.shots.remove(s)
        for g in self.ground_targets[:]:
            g["y"] += 0.5 * 0.6
            for s in self.shots[:]:
                if abs(g["x"]-s[0]) < 8 and abs(g["y"]-s[1]) < 8:
                    g["hp"] -= 1
                    if s in self.shots: self.shots.remove(s)
                    if g["hp"] <= 0: self.score += 1000; pyxel.play(2, 0); self.explosions.append([g["x"], g["y"], 0]); self.ground_targets.remove(g)
                    break
            if g["y"] > H: self.ground_targets.remove(g)
        for e in self.enemies[:]:
            e["t"] += 1
            if e["type"] == "sotta":
                e["y"] += (1.5 + (self.stage * 0.1)) * 0.6
                target_x = self.x if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) else W//2
                e["x"] += (target_x - e["x"]) * 0.05 * 0.6
            elif e["type"] == "kappa":
                if e["t"] < 35 / 0.6: e["y"] += 3.0 * 0.6
                else:
                    if e["vx"] == 0: target_x = self.x if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) else W//2; e["vx"] = 2.5 * 0.6 if e["x"] < target_x else -2.5 * 0.6
                    e["x"] += e["vx"]; e["y"] += 0.6 * 0.6
            elif e["type"] == "calderon":
                e["y"] += 1.2 * 0.6
                if e["t"] % max(20, int((45 - self.stage*5) / 0.6)) == 0 and self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL): 
                    self.shoot_at_player(e["x"], e["y"], (1.8 + (self.stage*0.3)) * 0.6)
            for s in self.shots[:]:
                if abs(e["x"]-s[0]) < 6 and abs(e["y"]-s[1]) < 6:
                    self.score += 100; self.explosions.append([e["x"], e["y"], 0]); pyxel.play(2, 1)
                    if e in self.enemies: self.enemies.remove(e)
                    if s in self.shots: self.shots.remove(s)
                    self.kill_count += 1
                    if self.kill_count >= 10:
                        if random.random() > (self.stage * 0.18): self.capsules.append({"x": e["x"], "y": e["y"], "type": "barrier"})
                        self.kill_count = 0
                    else:
                        rand_val, factor = random.random(), max(0.05, 0.8 - (self.stage * 0.15))
                        if rand_val < 0.04 * factor: self.capsules.append({"x": e["x"], "y": e["y"], "type": "1up"})
                        elif rand_val < 0.12 * factor: self.capsules.append({"x": e["x"], "y": e["y"], "type": "power"})
                    break
            if e in self.enemies and self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) and self.inv_timer == 0:
                if abs(e["x"]-(self.x+4)) < 6 and abs(e["y"]-(self.y+4)) < 6: self.hit_player()
            if e["y"] > H:
                if e in self.enemies: self.enemies.remove(e)
        for s in self.enemy_shots[:]:
            if len(s) == 2: s[1] += (2.2 + (self.stage * 0.1)) * 0.6
            else: s[0] += s[2]; s[1] += s[3]
            if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) and self.inv_timer == 0:
                if abs(s[0]-(self.x+4)) < 4 and abs(s[1]-(self.y+4)) < 4: 
                    self.hit_player()
                    if s in self.enemy_shots: self.enemy_shots.remove(s)
            if not (-20 < s[1] < H+20 and -20 < s[0] < W+20): 
                if s in self.enemy_shots: self.enemy_shots.remove(s)
        for c in self.capsules[:]:
            c["y"] += 0.8 * 0.6
            if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) and abs(c["x"]-(self.x+4)) < 8 and abs(c["y"]-(self.y+4)) < 8:
                if c["type"] == "power":
                    if self.power >= POWER_MAX:
                        for e in self.enemies[:]: self.score += 100; self.explosions.append([e["x"], e["y"], 0]); self.enemies.remove(e)
                        self.enemy_shots = []
                        if self.boss: self.boss["hp"] -= 20; self.boss["dmg_t"] = 6
                        pyxel.play(3, 1)
                    else: self.power = min(POWER_MAX, self.power + 1)
                    self.score += 500; pyxel.play(3, 2)
                elif c["type"] == "barrier":
                    self.barrier_hp = 3; self.score += 500; pyxel.play(3, 2)
                elif c["type"] == "1up": self.lives += 1; self.score += 1000; pyxel.play(3, 3)
                self.capsules.remove(c)
            elif c["y"] > H: self.capsules.remove(c)
        for ex in self.explosions[:]:
            ex[2] += 1
            if ex[2] > 12: self.explosions.remove(ex)

    def shoot_at_player(self, ex, ey, speed):
        ang = math.atan2((self.y+4)-ey, (self.x+4)-ex)
        self.enemy_shots.append([ex, ey, math.cos(ang)*speed, math.sin(ang)*speed])

    def hit_player(self):
        if self.muteki_enabled: return
        if self.barrier_hp > 0: 
            self.barrier_hp -= 1; pyxel.play(3, 0); self.inv_timer = 30
            return
        self.lives -= 1; pyxel.play(3, 1); self.explosions.append([self.x+4, self.y+4, 0])
        if self.lives <= 0:
            pyxel.stop()               # すべての再生中の音（BGM/SE）を強制停止
            self.scene = SCENE_GAMEOVER; self.scene_timer = 0; pyxel.playm(4, loop=False)
        else:
            pyxel.play(3, 1)           # ミス時のSE
            self.respawn_player()
            
    def init_boss(self):
        self.scene, self.enemies, self.ground_targets = SCENE_BOSS, [], []
        hp_table = {1: 80, 2: 120, 3: 180, 4: 250, 5: 400}
        m_hp = hp_table.get(self.stage, 100)
        self.boss = {"x": 80, "y": -20, "hp": m_hp, "max_hp": m_hp, "t": 0, "dmg_t": 0, "panic": False}
        pyxel.playm(2, loop=True)

    def update_boss(self):
        b = self.boss
        if not b: return
        if b["dmg_t"] > 0: b["dmg_t"] -= 1
        hp_rate = b["hp"] / b["max_hp"]
        difficulty_speed = 0.5 + (self.stage * 0.1) 
        panic_threshold = 0.15 + (self.stage * 0.05) 
        if hp_rate < panic_threshold and not b["panic"]: 
            b["panic"] = True
            pyxel.playm(3, loop=True)
        speed_mult = 1.0 + (0.2 if b["panic"] else 0)
        density_mult = 1.0 - (0.1 if b["panic"] else 0)
        b["t"] += 0.05 * 0.6 * difficulty_speed * speed_mult
        descent_speed = 0.15 * 0.6 
        if self.stage == 1:
            b["y"] = min(25, b["y"] + descent_speed)
            b["x"] = 80 + math.sin(b["t"] * 0.8) * 50
        elif self.stage == 2:
            b["y"] = min(25, b["y"] + descent_speed) + math.cos(b["t"] * 1.0) * 2
            b["x"] = 80 + math.sin(b["t"] * 0.7) * 40
        elif self.stage == 3:
            b["y"] = min(25, b["y"] + descent_speed) + math.cos(b["t"] * 1.2) * 4 + math.cos(b["t"] * 18.0) * 2
            b["x"] = 80 + math.sin(b["t"] * 1.0) * 50 + math.sin(b["t"] * 15.0) * 2
        elif self.stage == 4:
            b["y"] = min(25, b["y"] + descent_speed)
            target_x = 80 + math.sin(b["t"] * 0.5) * 60
            b["x"] += (target_x - b["x"]) * 0.1
        else:
            b["y"] = min(40, b["y"] + 0.1 * 0.6)
            b["x"] = 80 + math.sin(b["t"] * 0.4) * 30

        if self.scene != SCENE_GAMEOVER:
            shot_interval = max(4, int((30 - self.stage * 3) / 0.6 * density_mult))
            if pyxel.frame_count % shot_interval == 0:
                base_shot_speed = (1.5 + (self.stage * 0.3)) * 0.6 * speed_mult
                if self.stage == 1:
                    self.enemy_shots.append([b["x"], b["y"], 0, base_shot_speed])
                elif self.stage == 2:
                    for a in [-15, 0, 15]:
                        rad = math.radians(90 + a)
                        self.enemy_shots.append([b["x"], b["y"], math.cos(rad)*base_shot_speed, math.sin(rad)*base_shot_speed])
                elif self.stage == 3:
                    self.shoot_at_player(b["x"], b["y"], base_shot_speed)
                    if pyxel.frame_count % (shot_interval * 2) == 0:
                        for a in [-30, -15, 0, 15, 30]:
                            rad = math.radians(90 + a)
                            self.enemy_shots.append([b["x"], b["y"], math.cos(rad)*base_shot_speed, math.sin(rad)*base_shot_speed])
                elif self.stage == 4:
                    ang = (pyxel.frame_count * 3) % 360
                    for a in [0, 90, 180, 270]:
                        rad = math.radians(ang + a)
                        self.enemy_shots.append([b["x"], b["y"], math.cos(rad)*base_shot_speed, math.sin(rad)*base_shot_speed])
                else:
                    self.shoot_at_player(b["x"], b["y"], base_shot_speed * 1.1)
                    if pyxel.frame_count % (shot_interval * 2) == 0:
                        for a in range(-60, 61, 30):
                            rad = math.radians(90 + a + math.sin(b["t"])*15)
                            offset = math.sin(b["t"] * 2) * 15
                            self.enemy_shots.append([b["x"]-40 + offset, b["y"]+15, math.cos(rad)*base_shot_speed*0.7, math.sin(rad)*base_shot_speed*0.7])
                            self.enemy_shots.append([b["x"]+40 - offset, b["y"]+15, math.cos(rad)*base_shot_speed*0.7, math.sin(rad)*base_shot_speed*0.7])

        bw, bh = (40, 20) if self.stage == 5 else (22, 16)
        if self.inv_timer == 0:
            if abs(self.x + 4 - b["x"]) < bw and abs(self.y + 4 - b["y"]) < bh:
                pyxel.play(2, 2)  # ダメージ音（SE）
                self.hit_player()
        for s in self.shots[:]:
            if abs(s[0]-b["x"]) < bw and abs(s[1]-b["y"]) < bh:
                b["hp"] -= 1; self.score += 50; b["dmg_t"] = 4
                if s in self.shots: self.shots.remove(s)
        if b["hp"] <= 0: 
            self.score += 10000
            self.scene = SCENE_STAGE_CLEAR
            self.clear_timer = 0
            # --- 爆発演出の追加 ---
            # ボスのいた場所に複数の爆発エフェクトを散らす
            import random
            for _ in range(8):
                self.explosions.append([b["x"]+random.uniform(-16,16), b["y"]+random.uniform(-12,12), random.randint(10,20)])
            self.boss = None
            pyxel.stop()
            pyxel.play(2, 1)
            pyxel.play(3, 3)
            pyxel.playm(5, loop=False)      # クリアファンファーレ再生
            return                          # ここで処理を抜ける     

    def next_stage(self):
        if self.clear_timer < 160:
            if self.clear_timer > 30: 
                self.y -= (self.clear_timer - 30) * 0.2
            return

        if self.stage >= MAX_STAGE: 
            self.scene = SCENE_ENDING
            self.scroll_y = 0
            pyxel.playm(6, loop=True)
        else: 
            # ステータスの保持
            p, b, s, l, m = self.power, self.barrier_hp, self.score, self.lives, self.muteki_enabled
            
            self.stage += 1
            
            # --- ここで次のステージのBGMを適用 ---
            self.apply_stage_music()
            
            self.scene = SCENE_PLAY
            self.reset_stage_env()
            self.x, self.y = 80, 100 # 開始位置を調整
            self.inv_timer = 90
            
            # ステータスを復元
            self.power, self.barrier_hp, self.score, self.lives, self.muteki_enabled = p, b, s, l, m
            
            # 再生開始
            pyxel.playm(1, loop=True)
    # --- ヘルパー描画メソッド ---
    def draw_big_s(self, x, y):
        parts = [(0,0,16,42), (16,0,32,10), (0,16,48,10), (32,26,16,10), (0,32,48,10)]
        mid_y = 21 
        for dx, dy, dw, dh in parts:
            pyxel.rect(x+dx+2, y+dy+2, dw, dh, 13) 
            if dy < mid_y:
                h_top = min(dh, mid_y - dy)
                pyxel.rect(x+dx, y+dy, dw, h_top, 12) 
                if dy + dh > mid_y: pyxel.rect(x+dx, y+mid_y, dw, dh - h_top, 8) 
            else:
                pyxel.rect(x+dx, y+dy, dw, dh, 8)

    def draw_bold_text(self, text, x, y, col):
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]: pyxel.text(x+dx, y+dy, text, 13)
        pyxel.text(x, y, text, col)

    def draw(self):
        bg_themes = {1:(0,1,"nebula"), 2:(5,12,"grid"), 3:(1,2,"plasma"), 4:(0,5,"warp"), 5:(0,1,"fortress")}
        curr_stg = self.stage if self.scene not in (SCENE_TITLE, SCENE_TUTORIAL) else 1
        theme = bg_themes.get(curr_stg, bg_themes[1])
        pyxel.cls(theme[0])
        
        # --- 背景演出 ---
        if theme[2] == "nebula":
            for i in range(3): 
                pyxel.circb(80 + math.sin(pyxel.frame_count*0.01 + i)*40, 60 + math.cos(pyxel.frame_count*0.01 + i)*20, 30+i*10, theme[1])
        elif theme[2] == "grid":
            offset = pyxel.frame_count % 20
            for i in range(0, 160 + 20, 20): pyxel.line(i, 0, i, 120, theme[1])
            for i in range(0, 120 + 20, 20): pyxel.line(0, i + offset, 160, i + offset, theme[1])
        elif theme[2] == "plasma":
            for i in range(4):
                y_base = (pyxel.frame_count * (1 + i) * 0.5) % 120
                for x in range(0, 160, 4):
                    y = y_base + math.sin(x * 0.05 + pyxel.frame_count * 0.1) * 5
                    pyxel.pset(x, y, theme[1])
        elif theme[2] == "warp":
            for i in range(12):
                lx = (i * 15 + 7) % 160
                ly_base = (pyxel.frame_count * 8 + i * 40) % (120 + 40)
                pyxel.line(lx, ly_base - 20, lx, ly_base, theme[1])
        elif theme[2] == "fortress":
            pyxel.cls(1) 
            for i in range(2):
                y_base = (pyxel.frame_count * 4 + i * 120) % (120 * 2) - 120
                pyxel.rectb(20, y_base, 30, 120 - 20, 13)
                pyxel.rectb(110, y_base, 30, 120 - 20, 13)
                if pyxel.frame_count % 30 < 15:
                    pyxel.rect(30, y_base + 30, 10, 5, 8)
                    pyxel.rect(120, y_base + 30, 10, 5, 8)
                else:
                    pyxel.rect(30, y_base + 40, 10, 5, 10)
                    pyxel.rect(120, y_base + 40, 10, 5, 10)
            band_offset = (pyxel.frame_count * 10) % (120 + 60)
            pyxel.tri(50, band_offset - 60, 50, band_offset, 0, band_offset, 2)
            pyxel.tri(160-50, band_offset - 60, 160-50, band_offset, 160, band_offset, 2)
            for i in range(3):
                str_y = (pyxel.frame_count * 6 + i * 60) % (120 + 60) - 60
                pyxel.rect(0, str_y, 10, 40, 0)
                pyxel.rect(160-10, str_y, 10, 40, 0)
                pyxel.line(10, str_y, 10, str_y + 40, 13)
                pyxel.line(160-11, str_y, 160-11, str_y + 40, 13)
            for i in range(15):
                point_y, point_x = (pyxel.frame_count * 12 + i * 13) % 120, (i * 11) % 160
                if point_x < 60 or point_x > 100: pyxel.pset(point_x, point_y, 7)

        if theme[2] != "fortress":
            for s in self.space_stars:
                if self.scene == SCENE_STAGE_CLEAR:
                    if self.clear_timer % 6 < 3: pyxel.rect(0, 0, 160, 120, 1)
                    else: pyxel.pset(s[0], s[1], 7 if s[2] > 1.8 else 13)
                else:
                    pyxel.pset(s[0], s[1], 7 if s[2] > 1.8 else 13)

        # --- 各種オブジェクト描画 ---
        if self.scene == SCENE_ENDING:
            self.draw_ending()
            return

        for g in self.ground_targets:
            gx, gy = g["x"], g["y"]
            pyxel.rect(gx-6, gy-6, 13, 13, 1)
            self.draw_planetary_surface(gx, gy, 13, g.get("seed", 0))
            pyxel.rectb(gx-6, gy-6, 13, 13, 13)
            core_col = 10 if pyxel.frame_count % 8 < 4 else 8
            pyxel.circb(gx, gy, 2, core_col)
            pyxel.pset(gx, gy, 7)

        for e in self.enemies:
            ex, ey = e["x"], e["y"]
            if e["type"] == "sotta":
                rot = (pyxel.frame_count // 2) % 4
                pyxel.circ(ex, ey, 3, 13)
                pyxel.circb(ex, ey, 3, 5)
                pyxel.line(ex-2, ey, ex+2, ey, 7 if rot%2==0 else 1)
                pyxel.line(ex, ey-2, ex, ey+2, 7 if rot%2!=0 else 1)
                pyxel.pset(ex, ey, 8)
            elif e["type"] == "kappa":
                pyxel.tri(ex, ey+3, ex-4, ey-3, ex+4, ey-3, 11)
                pyxel.tri(ex, ey+1, ex-2, ey-3, ex+2, ey-3, 3)
                pyxel.pset(ex, ey-1, 8)
            else:
                pyxel.rect(ex-4, ey-3, 9, 7, 4); pyxel.rect(ex-2, ey-4, 5, 9, 2)
                pyxel.pset(ex-3, ey-1, 8); pyxel.pset(ex+3, ey-1, 8)
                pyxel.line(ex-1, ey, ex+1, ey, 10)

        for s in self.shots: pyxel.rect(s[0], s[1], 2, 4, 10); pyxel.pset(s[0], s[1]+1, 7)
        for s in self.enemy_shots: pyxel.circ(s[0], s[1], 1, 8); pyxel.pset(s[0], s[1], 7)
        for c in self.capsules:
            col = 12 if pyxel.frame_count % 4 < 2 else 6
            if c["type"] == "barrier":
                pyxel.circ(c["x"], c["y"], 4, col); pyxel.circb(c["x"], c["y"], 4, 7)
                pyxel.text(c["x"]-1, c["y"]-2, "B", 7)
            else:
                col_main = 8 if pyxel.frame_count % 4 < 2 else 10
                if c["type"] == "1up": col_main = 3 if pyxel.frame_count % 4 < 2 else 11
                pyxel.circ(c["x"], c["y"], 4, col_main); pyxel.circb(c["x"], c["y"], 4, 7)
                pyxel.text(c["x"]-1 if c["type"]=="power" else c["x"]-3, c["y"]-2, "P" if c["type"]=="power" else "1U", 7)
        
        for ex in self.explosions:
            pyxel.circb(ex[0], ex[1], ex[2], 7)
            if ex[2] < 6: pyxel.circ(ex[0], ex[1], ex[2]//2, 10)

        # --- 自機描画 ---
        if self.scene in (SCENE_PLAY, SCENE_BOSS, SCENE_PAUSE, SCENE_STAGE_CLEAR):
            if self.muteki_enabled: pyxel.text(70, 2, "MUTEKI", 10 if pyxel.frame_count % 4 < 2 else 7)
            if self.inv_timer == 0 or (pyxel.frame_count % 2 == 0):
                px, py = self.x, self.y
                pyxel.tri(px+4, py, px+2, py+4, px+6, py+4, 7); pyxel.rect(px+3, py+4, 3, 4, 7)
                pyxel.tri(px+3, py+5, px-1, py+2, px+1, py+8, 8); pyxel.tri(px+5, py+5, px+9, py+2, px+7, py+8, 8)
                pyxel.line(px-1, py+2, px+1, py+4, 7); pyxel.line(px+9, py+2, px+7, py+4, 7)
                pyxel.pset(px+4, py+6, 12)
                if pyxel.frame_count % 2 == 0: pyxel.tri(px+3, py+8, px+5, py+8, px+4, py+11, 9)
                if self.barrier_hp > 0: pyxel.circb(self.x+4, self.y+4, 10, (12 if self.barrier_hp > 1 else 6) if pyxel.frame_count % 2 == 0 else 7)
                if self.muteki_enabled: pyxel.circb(self.x+4, self.y+4, 12, 10 if pyxel.frame_count % 4 < 2 else 7)

        # --- ボス描画 ---
        if self.boss and self.scene not in (SCENE_TITLE, SCENE_TUTORIAL):
            bx, by = self.boss["x"], self.boss["y"]
            hp_rate = self.boss["hp"] / self.boss["max_hp"]
            is_panic_flash = (self.stage == 5 and hp_rate < 0.2 and pyxel.frame_count % 4 < 2)
            if self.boss["dmg_t"] > 0 and pyxel.frame_count % 2 == 0:
                f_w = 90 if self.stage == 5 else 30
                pyxel.rect(bx - f_w//2, by - 15, f_w, 35, 7)
            elif is_panic_flash: pyxel.rect(bx - 45, by - 15, 90, 35, 8)
            else:
                if self.stage == 5:
                    for side in [-1, 1]:
                        pyxel.tri(bx+side*20, by-15, bx+side*50, by+5, bx+side*20, by+25, 13)
                        pyxel.rectb(bx+side*20, by-15, 10, 40, 5)
                        if pyxel.frame_count % 4 < 2: pyxel.line(bx+side*25, by-10, bx+side*45, by+5, 10)
                    shot_interval = max(4, int((30 - self.stage * 3) / 0.6 * (1.0 - (0.1 if self.boss["panic"] else 0))))
                    is_firing = pyxel.frame_count % (shot_interval * 2) == 0
                    for side in [-1, 1]:
                        offset = math.sin(self.boss["t"] * 2) * 15 * side
                        p_x = bx + side * 40 - offset
                        pyxel.rect(p_x-6, by+12, 12, 10, 5); pyxel.rectb(p_x-6, by+12, 12, 10, 13)
                        if is_firing: pyxel.circ(p_x, by+22, 3, 7)
                        else: pyxel.rect(p_x-2, by+20, 5, 3, 8)
                    pyxel.rect(bx-20, by-12, 40, 28, 1); pyxel.rectb(bx-20, by-12, 40, 28, 13)
                    c_col = 10 if hp_rate > 0.5 else (9 if hp_rate > 0.2 else 8)
                    pyxel.circ(bx, by, 10, 5); pyxel.circ(bx, by, 7, c_col)
                    if pyxel.frame_count % 2 == 0: pyxel.circb(bx, by, 8, 7)
                    pyxel.pset(bx, by, 7)
                else:
                    b_base = 8 if hp_rate < 0.3 else 2
                    pyxel.rect(bx-14, by-12, 28, 24, 1); pyxel.rectb(bx-14, by-12, 28, 24, 5)
                    pyxel.circ(bx, by, 7, b_base)
                    core_col = 8 if pyxel.frame_count % 10 < 5 else 10
                    pyxel.circ(bx, by, 4, core_col); pyxel.pset(bx, by, 7)
                    for side in [-1, 1]:
                        ax = bx + side * 20
                        pyxel.tri(ax, by-14, ax+side*14, by-4, ax, by+10, 13 if hp_rate > 0.5 else 8)
                        pyxel.tri(ax, by-12, ax+side*10, by-4, ax, by+8, 5)
                        pyxel.rect(bx + side*10, by-16, 6, 12, 4 if hp_rate > 0.4 else 2)
            pyxel.text(bx-2, by-20, chr(ord('A') + self.stage - 1), 7)

        # --- シーン別UI描画 ---
        if self.scene == SCENE_TITLE:
            cx, cy = 80, 32
            pyxel.circb(cx, cy, 34, 13); pyxel.circb(cx, cy, 30, 1)
            for i in range(8):
                ang = math.radians(i * 45 + pyxel.frame_count * 0.5)
                pyxel.line(cx, cy, cx + math.cos(ang) * 35, cy + math.sin(ang) * 35, 1)
            pyxel.circ(cx, cy, 18, 1); pyxel.circb(cx, cy, 18, 13)
            if pyxel.frame_count % 10 < 5: pyxel.rect(cx-8, cy-2, 4, 4, 8); pyxel.rect(cx+4, cy-2, 4, 4, 12)
            
            lx, ly = 20, 10
            self.draw_big_s(lx, ly)
            self.draw_bold_text("TAR", lx + 54, ly + 2, 12)
            self.draw_bold_text("HOTTER", lx + 54, ly + 24, 8)
            self.draw_bold_text("KAI", lx + 80, ly + 36, 10)
            
            pyxel.text(40, 72, "PUSH START/ENTER BUTTON", 7 if pyxel.frame_count % 30 < 15 else 13)
            pyxel.text(52, 91, f"HI-SCORE  {self.high_score:06}", 7)
            pyxel.text(25, 100, "(C) 2026 MIRAI WORK / M.T", 7)
            pyxel.text(20, 82, "PUSH ANY/SPACE KEY: HOW TO PLAY", 3)
            if self.muteki_enabled: pyxel.text(54, 108, "MUTEKI MODE ENABLED", 10 if pyxel.frame_count % 4 < 2 else 7)
            elif self.cheat_enabled: pyxel.text(32, 108, f"SPECIAL: STAGE {self.stage} READY", 11)

        elif self.scene == SCENE_TUTORIAL:
            pyxel.rect(20, 20, 120, 80, 1); pyxel.rectb(20, 20, 120, 80, 7)
            pyxel.text(55, 30, "- HOW TO PLAY -", 10)
            pyxel.text(35, 45, "ARROW: MOVE", 7); pyxel.text(35, 55, "Z/X/A/B: FIRE", 7)
            pyxel.text(35, 70, "P: POWER UP / B: BARRIER", 12); pyxel.text(35, 80, "1U: 1UP (EXTRA LIFE)", 11)
            pyxel.text(26, 92, "ANY/SPACE KEY:BACK TO TITLE", 13 if pyxel.frame_count % 10 < 5 else 5)

        elif self.scene == SCENE_GAMEOVER:
            pyxel.text(62, 50, "GAME OVER", 8)
            score_text = f"SCORE: {self.score:07}"
            pyxel.text(160//2 - len(score_text)*2, 62, score_text, 7)

        elif self.scene == SCENE_PAUSE: pyxel.text(66, 50, "PAUSE", 7)
        elif self.scene == SCENE_STAGE_CLEAR: pyxel.text(48, 50, "STAGE CLEAR!", 11); pyxel.text(45, 65, "GET READY FOR NEXT", 7)

        # ステータス表示
        if self.scene not in (SCENE_TITLE, SCENE_TUTORIAL, SCENE_GAMEOVER, SCENE_ENDING):
            pyxel.text(5, 4, f"SCORE {self.score:07}", 7); pyxel.text(100, 4, f"STAGE {self.stage}", 7)
            pyxel.text(5, 112, "PLAYER", 7)
            for i in range(self.lives): pyxel.rect(32 + i*6, 112, 3, 5, 8)
            b_status = f" B:{self.barrier_hp}" if self.barrier_hp > 0 else ""
            pyxel.text(100, 112, f"POWER {self.power}{b_status}", 10)

    def draw_ending(self):
        texts = ["CONGRATULATIONS!", "", "YOU HAVE SAVED", "THE GALAXY", "", "--- STAFF ---", "", 
                 "DIRECTOR: M.T", "GRAPHIC: M.T", "MUSIC: M.T", "THANKS: T.D TEAMS", 
                 "SPECIAL THANKS: YOU!", "", "PRESENTS BY", "MIRAI WORK CO., LTD.", "2026"]
        for i, t in enumerate(texts):
            y = 120 - self.scroll_y + i * 12
            if -10 < y < 120 + 10: 
                pyxel.text(160//2 - len(t)*2, y, t, 7 if i % 2 == 0 else 10)
        
        scroll_end_y = 120 - self.scroll_y + len(texts) * 12
        if scroll_end_y < -20:
            pyxel.text(45, 60, "THANKS FOR PLAYING!", pyxel.frame_count % 16)
           
            # さらに一定時間（座標）が経過したらタイトルへ
            if scroll_end_y < -170:
                # --- すべてのステータスとフラグを完全に初期化 ---
                self.reset_all() 
                self.scene = SCENE_TITLE
                self.scene_timer = 0
                self.score = 0
                self.stage = 1
                self.scroll_y = 0
                self.power = 0
                self.barrier_hp = 0
                self.lives = 3 # 残機も初期値へ
                self.muteki_enabled = False # 無敵モードを解除
                self.cheat_enabled = False  # チートフラグを解除
                # ------------------------------------------
                pyxel.playm(0, loop=True)

StarSoldier()

