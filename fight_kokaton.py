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
    delta = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, xy: tuple[int, int]):
        img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 2.0)
        img1 = pg.transform.flip(img0, True, False)

        self.imgs = {
            (+5, 0): img1,
            (+5, -5): pg.transform.rotozoom(img1, 45, 1.0),
            (0, -5): pg.transform.rotozoom(img1, 90, 1.0),
            (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),
            (-5, 0): img0,
            (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),
            (0, +5): pg.transform.rotozoom(img1, -90, 1.0),
            (+5, +5): pg.transform.rotozoom(img1, -45, 1.0),
        }

        self.dire = (+5, 0)
        self.img = self.imgs[self.dire]
        self.rct = self.img.get_rect()
        self.rct.center = xy

        self.joy_timer = 0  # ★追加

    def change_img(self, img_path: str, zoom: float = 2.0):
        self.img = pg.transform.rotozoom(pg.image.load(img_path), 0, zoom)

    def joy(self):
        self.change_img("fig/6.png", 2.0)
        self.joy_timer = 30

    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        self.rct.move_ip(sum_mv)

        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])

        if sum_mv != [0, 0]:
            self.dire = tuple(sum_mv)
            self.img = self.imgs[self.dire]

        screen.blit(self.img, self.rct)

        if self.joy_timer > 0:
            self.joy_timer -= 1
            if self.joy_timer == 0:
                self.change_img("fig/3.png", 2.0)


class Bomb:
    """
    追加機能2
    打ち落とした爆弾の数を表示するスコアクラス
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
    追加機能4
    こうかとんの向きに応じたビームに関するクラス
    """
    def __init__(self, bird: Bird):
        self.img = pg.image.load("beam.png")
        self.rct = self.img.get_rect()
        self.rct.center = bird.rct.center

        self.vx = bird.dire[0] * 2
        self.vy = bird.dire[1] * 2

        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.img = pg.transform.rotozoom(self.img, angle, 1.0)

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """
    スコア表示
    """
    def __init__(self):
        self.font = pg.font.SysFont("hgpkyokashotai", 30)
        self.score = 0
        self.color = (0, 0, 255)

    def update(self, screen: pg.Surface):
        img = self.font.render(f"SCORE: {self.score}", True, self.color)
        screen.blit(img, (50, HEIGHT - 50))


class Explosion:
    """
    追加機能3
    爆弾打ち落とし時の爆発エフェクトクラス
    """
    def __init__(self, obj_rct: pg.Rect):
        self.img = pg.image.load("fig/explosion.gif")
        self.rct = self.img.get_rect()
        self.rct.center = obj_rct.center
        self.life = 20

    def update(self, screen: pg.Surface):
        self.life -= 1
        screen.blit(self.img, self.rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    unko_img = pg.image.load("fig/unko.png")
    
    unko_img = pg.transform.scale(unko_img, (50, 50))
    unko_list = []
    clock = pg.time.Clock()
    tmr = 0
    sum_mv = [0, 0] 
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))

    bombs = [Bomb((255, 0, 0), 10) for _ in range(3)]
    """
    追加機能2
    複数のビームを打てるようにする
    """
    beams = []
    explosions = []
    score = Score()

    clock = pg.time.Clock()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))
        tmr += 1
        screen.blit(bg_img, [0, 0])
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        # 10秒に1回（50fpsなので500フレームごと）落とす処理
        if tmr > 0 and tmr % 500 == 0:
            new_unko_rct = unko_img.get_rect()
            new_unko_rct.center = bird.rct.center  # こうかとんの現在地
            unko_list.append(new_unko_rct)

        # 画面内の物体を下に移動させて描画（画面外に出たら削除）
        for u_rct in unko_list[:]:
            u_rct.move_ip(0, 4)  # 下方向に毎フレーム4ピクセルずつ落下
            if u_rct.top > HEIGHT:
                unko_list.remove(u_rct)
            else:
                screen.blit(unko_img, u_rct)
        # 衝突：鳥 vs 爆弾
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                bird.img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 2.0)
                screen.blit(bird.img, bird.rct)
                pg.display.update()
                pg.time.wait(2000)

                font = pg.font.Font(None, 80)
                txt = font.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, (WIDTH // 2 - 150, HEIGHT // 2))

                pg.display.update()
                pg.time.wait(2000)
                return

        # 衝突：ビーム vs 爆弾
        for i, bomb in enumerate(bombs):
            for j, beam in enumerate(beams):
                if beam is None:
                    continue
                if bomb is None:
                    continue

                if beam.rct.colliderect(bomb.rct):
                    explosions.append(Explosion(bomb.rct))
                    score.score += 1
                    bird.joy()

                    beams[j] = None
                    bombs[i] = Bomb((255, 0, 0), 10)
                    break

        bombs = [b for b in bombs if b is not None]
        beams = [b for b in beams if b is not None]

        for bomb in bombs:
            bomb.update(screen)

        for beam in beams:
            beam.update(screen)

        beams = [b for b in beams if check_bound(b.rct) == (True, True)]

        for exp in explosions:
            exp.update(screen)

        explosions = [e for e in explosions if e.life > 0]

        score.update(screen)

        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
