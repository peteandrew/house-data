import pygame
import os
import time
import requests
import json
from datetime import datetime

os.environ["SDL_FBDEV"] = "/dev/fb1"

pygame.init()

pygame.mouse.set_visible(0)

size = width, height = 320, 240
screen = pygame.display.set_mode(size)

font = pygame.font.Font(None, 45)
font_tiny = pygame.font.Font(None, 20)


def fetch_temp(id):
    t = None

    try:
        r = requests.get('http://192.168.0.147:5000/temps/' + str(id))
        if r.status_code == 200:
            t = r.json()
    except requests.exceptions.ConnectionError:
        pass

    return t


def render_temp_text(t, label, pos):
    if t is None:
        disp_text = label + ': no data'
        text = font.render(disp_text, 0, (255, 0, 0))
        screen.blit(text, pos)
    else:
        now = datetime.utcnow()
        time = datetime.strptime(t['time'], "%Y-%m-%d %H:%M:%S")
        dt = now - time
        mins = dt.total_seconds() / 60

        if mins > 10:
            colour = (0, 100, 255)
        else:
            colour = (255, 255, 255)

        disp_text = label + ': %.2fC' % t['temp']
        text = font.render(disp_text, 0, colour)
        screen.blit(text, pos)
        disp_text = str(t['time']) + '  ' + str(t['rssi'])
        text = font_tiny.render(disp_text, 0, (120, 120, 200))
        screen.blit(text, (pos[0], pos[1]+32))


delay_count = 3
t1 = None
t2 = None
t3 = None
t4 = None

while True:
    if delay_count == 3:
        t1 = fetch_temp(1)
        t2 = fetch_temp(2)
        t3 = fetch_temp(3)
        t4 = fetch_temp(4)

        delay_count = 0

    screen.fill((0,0,0))

    render_temp_text(t1, 'Kitchen', (10, 0))
    render_temp_text(t2, 'Upstairs', (10, 55))
    render_temp_text(t3, 'Outside', (10, 110))
    render_temp_text(t4, 'Coldframe', (10, 165))

    pygame.display.flip()

    time.sleep(10)
    delay_count += 1
