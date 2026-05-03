#!/usr/bin/env python3
"""Chrome Dino Game - CLI Edition"""

import curses
import random
import sys
import time

WIDTH = 120
GROUND_Y = 18
GRAVITY = 1.2
JUMP_FORCE = -6
MIN_INTERVAL = 15
MAX_INTERVAL = 25

DINO = [
    "   █▄▄",
    "▄▄▄█",
    "█  █",
]

CACTI = [
    ["▄▄", "██"],
    ["▄▄", "██", "██", "██"],
]


class Dino:
    def __init__(self, x, ground):
        self.x = x
        self.ground = ground
        self.h = len(DINO)
        self.w = len(DINO[0])
        self.y = ground - self.h
        self.vy = 0
        self.jumping = False

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.vy = JUMP_FORCE

    def update(self):
        if self.jumping:
            self.vy += GRAVITY
            self.y += self.vy
            if self.y >= self.ground - self.h:
                self.y = self.ground - self.h
                self.vy = 0
                self.jumping = False

    def rect(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)


class Obstacle:
    def __init__(self, x, art):
        self.x = x
        self.art = art
        self.h = len(art)
        self.w = len(art[0])
        self.y = GROUND_Y - self.h

    def update(self):
        self.x -= 2

    def rect(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)


def collide(a, b):
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def draw_art(stdscr, x, y, art, w=WIDTH, color=0):
    for i, line in enumerate(art):
        cy = int(y + i)
        if 0 <= cy < curses.LINES:
            visible = line[:max(0, w - int(x))]
            try:
                stdscr.addstr(cy, max(0, int(x)), visible, curses.color_pair(color))
            except curses.error:
                pass


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_RED, -1)
    try:
        curses.init_color(8, 1000, 600, 0)
        curses.init_pair(6, 8, -1)
    except curses.error:
        curses.init_pair(6, curses.COLOR_YELLOW, -1)
    stdscr.nodelay(1)
    stdscr.timeout(40)

    dino = Dino(15, GROUND_Y)
    obstacles = []
    clouds = []
    score = 0
    high_score = 0
    frame = 0
    game_over = False
    timer = 0
    speed = 2
    ducking = False

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break

        if game_over:
            if key == ord(' '):
                dino = Dino(15, GROUND_Y)
                obstacles.clear()
                clouds.clear()
                score = 0
                frame = 0
                timer = 0
                speed = 2
                game_over = False
            stdscr.clear()
            msg = "GAME OVER"
            stdscr.addstr(GROUND_Y // 2 - 1, (WIDTH - len(msg)) // 2, msg, curses.color_pair(5))
            msg = "Press SPACE to restart | Q to quit"
            stdscr.addstr(GROUND_Y // 2 + 1, (WIDTH - len(msg)) // 2, msg, curses.color_pair(1))
            stdscr.addstr(0, 0, f"Score: {score}  High: {high_score}", curses.color_pair(4))
            stdscr.refresh()
            continue

        if key == ord(' '):
            dino.jump()

        dino.update()

        for obs in obstacles[:]:
            obs.update()
            if obs.x + obs.w < 0:
                obstacles.remove(obs)
                score += 1

        for c in clouds[:]:
            c[0] -= 1
            if c[0] + 8 < 0:
                clouds.remove(c)

        if random.random() < 0.015 and len(clouds) < 3:
            clouds.append([WIDTH, random.randint(2, 7)])

        timer -= 1
        if timer <= 0:
            art = random.choice(CACTI)
            obstacles.append(Obstacle(WIDTH, art))
            timer = random.randint(MIN_INTERVAL, MAX_INTERVAL)

        dr = dino.rect()
        for obs in obstacles:
            if collide(dr, obs.rect()):
                game_over = True

        if score > high_score:
            high_score = score

        if score > 0 and score % 50 == 0:
            speed = min(4, 2 + score // 50)

        stdscr.clear()

        for c in clouds:
            draw_art(stdscr, int(c[0]), c[1], ["  ▄▄▄  ", " ▄▄▄▄▄ "], color=3)

        for obs in obstacles:
            draw_art(stdscr, obs.x, obs.y, obs.art, color=2)

        stdscr.addstr(GROUND_Y, 0, "█" * WIDTH, curses.color_pair(6))

        draw_art(stdscr, dino.x, dino.y, DINO, color=1)

        stdscr.addstr(0, 0, f"Score: {score}", curses.color_pair(4))
        stdscr.addstr(0, 50, f"High: {high_score}", curses.color_pair(4))

        frame += 1
        stdscr.refresh()
        time.sleep(0.03)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
