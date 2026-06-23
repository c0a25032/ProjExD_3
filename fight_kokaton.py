import os
import sys
import math
import random
import pygame as pg

WIDTH = 1100
HEIGHT = 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期座標タプル
        """
        img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 2.0)
        img1 = pg.transform.flip(img0, True, False)  # 右向き
        # 移動方向に応じた8方向の画像を事前生成して辞書に格納
        self.imgs = {
            (+5, 0): img1,  # 右
            (+5, -5): pg.transform.rotozoom(img1, 45, 1.0),  # 右上
            (0, -5): pg.transform.rotozoom(img1, 90, 1.0),  # 上
            (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-5, 0): img0,  # 左
            (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +5): pg.transform.rotozoom(img1, -90, 1.0),  # 下
            (+5, +5): pg.transform.rotozoom(img1, -45, 1.0),  # 右下
        }
        self.dire = (+5, 0)  # 初期の向き（右）
        self.img = self.imgs[self.dire]
        self.rct = self.img.get_rect()
        self.rct.center = xy

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
            
        # 移動していたら向き(dire)と画像(img)を更新する
        if sum_mv != [0, 0]:
            self.dire = tuple(sum_mv)
            self.img = self.imgs[self.dire]
            
        screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2 * rad, 2 * rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:
    """
    【追加機能4】こうかとんの向きに応じたビームに関するクラス
    """
    def __init__(self, bird: Bird):
        self.img = pg.image.load("beam.png")
        self.rct = self.img.get_rect()
        self.rct.centerx = bird.rct.centerx
        self.rct.centery = bird.rct.centery
        # こうかとんの向いている方向(dire)に合わせてビームの速度を設定
        self.vx, self.vy = bird.dire[0] * 2, bird.dire[1] * 2
        
        # 速度ベクトルから角度を計算してビームの画像を回転させる
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.img = pg.transform.rotozoom(self.img, angle, 1.0)

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """
    【追加機能1】打ち落とした爆弾の数を表示するスコアクラス
    """
    def __init__(self):
        self.font = pg.font.SysFont("hgpkyokashotai", 30)
        self.score = 0
        self.color = (0, 0, 255)

    def update(self, screen: pg.Surface):
        score_img = self.font.render(f"SCORE: {self.score}", True, self.color)
        screen.blit(score_img, (50, HEIGHT - 50))


class Explosion:
    """
    【追加機能3】爆弾打ち落とし時の爆発エフェクトクラス
    """
    def __init__(self, obj_rct: pg.Rect):
        # 指示通り「fig/」の中の画像を読み込むように修正したわ！
        self.img = pg.image.load("fig/explosion.gif")
        self.rct = self.img.get_rect()
        self.rct.center = obj_rct.center
        self.life = 20  # 爆発の表示時間（フレーム数）

    def update(self, screen: pg.Surface):
        self.life -= 1
        screen.blit(self.img, self.rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(3)]  # 爆弾を3つに
    beams = []        # 【追加機能2】複数のビームを打てるようにリスト化
    explosions = []
    score = Score()
    
    clock = pg.time.Clock()
    tmr = 0
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))  # スペースキーでビーム追加
                
        screen.blit(bg_img, [0, 0])
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        
        # こうかとんと爆弾の衝突判定
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                bird.img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 2.0)
                screen.blit(bird.img, bird.rct)
                pg.display.update()
                pg.time.wait(2000)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                # -----------------------
                
                pg.display.update()
                pg.time.wait(2000) # 2秒間停止して文字を見せる
                return
                 
    # ビームと爆弾の衝突判定
        for i, bomb in enumerate(bombs):
            if bomb is not None:
                for j, beam in enumerate(beams):
                    if beam is not None and beam.rct.colliderect(bomb.rct):
                        explosions.append(Explosion(bomb.rct)) 
                        score.score += 1                        
                        beams[j] = None  # ビームを消去
                        bombs[i] = None  # 爆弾を消去
                        bombs.append(Bomb((255, 0, 0), 10))  # 爆弾を再生成
                        
                         
                        bird.img = pg.transform.rotozoom(pg.image.load("fig/6.png"), 0, 2.0)
                        
                        break  
        # 各オブジェクトの更新と画面外の削除処理
        for bomb in bombs:
            bomb.update(screen)
            
        for beam in beams.copy():
            beam.update(screen)
            # 画面外に出たビームは削除
            if not check_bound(beam.rct)[0] or not check_bound(beam.rct)[1]:
                beams.remove(beam)
                
        for explosion in explosions.copy():
            explosion.update(screen)
            if explosion.life <= 0:
                explosions.remove(explosion)
                
        score.update(screen)
        
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()