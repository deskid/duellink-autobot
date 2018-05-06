# coding=utf-8
import datetime
import logging
import os
from time import sleep

import pyautogui
from PIL import Image
from transitions import Machine, State

import adb

logging.basicConfig()
adbTool = adb.ADB()

WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920

DUEL_LISTS = os.listdir("images/face")


def screenshot():
    tmp_file = '.screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))
    adbTool.screenShot(tmp_file)
    sleep(1)
    im = Image.open(tmp_file)
    im.load()
    os.unlink(tmp_file)
    return im


def tap(x, y):
    print ">>> tap %s %s" % (x, y)
    adbTool.tap(x, y)


def slide_right():
    print ">>> slide right"
    adbTool.swipe(WINDOW_WIDTH - 100, WINDOW_HEIGHT / 2, 100, WINDOW_HEIGHT / 2)


def slide_left():
    print ">>> slide left"
    adbTool.swipe(100, WINDOW_HEIGHT / 2, WINDOW_WIDTH - 100, WINDOW_HEIGHT / 2)


def locate_image(part_image):
    screen = screenshot()
    loc = pyautogui.locate(part_image, screen, confidence=0.7, grayscale=True, step=1)

    if loc is None:
        return -1, -1
    else:
        loc = pyautogui.center(loc)
        return loc[0], loc[1]


def log_position(x, y, tag=""):
    position = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
    print (tag + " at " + position)


class Game(object):
    states = [
        State(name='init'),
        State(name='start', on_enter='search_duelist'),
        State(name='conversation', on_enter='search_skip_conversation_btn'),
        State(name='auto_duel_model_choose', on_enter='search_auto_duel_btn'),
        State(name='game_playing', on_enter='search_game_finished_btn'),
        State(name='game_end', on_enter='search_confirm_reward_btn'),
        State(name='reward_confirm', on_enter='search_back_to_main_scene_btn'),
        State(name='end', on_enter='switch_to_new_screen')
    ]

    def __init__(self):
        self.machine = Machine(model=self, states=Game.states, initial='init')

        self.machine.add_transition(trigger='failed', source='*', dest='end')

        self.machine.add_transition(trigger='next', source='start', dest='conversation')

        self.machine.add_transition(trigger='next', source='conversation',
                                    dest='auto_duel_model_choose')

        self.machine.add_transition(trigger='next', source='auto_duel_model_choose',
                                    dest='game_playing')

        self.machine.add_transition(trigger='next', source='game_playing', dest='game_end')

        self.machine.add_transition(trigger='next', source='game_end',
                                    dest='reward_confirm')

        self.machine.add_transition(trigger='next', source='reward_confirm',
                                    dest='end')

        self.machine.add_transition(trigger='next', source='end', dest='start')

    def start(self):
        while True:
            print "========== game start! ============"
            self.to_start()
            sleep(1)

    def search_and_click_image(self, image, max_count=1):
        retry_count = 0
        while retry_count < max_count:
            x, y = locate_image(image)
            if x != -1:
                tap(x, y)
                print ("click image :" + image)
                return True
            else:
                retry_count += 1
        return False

    def search_duelist(self):
        print "[ search dueler of duelist ]"
        if not self.is_start:
            return
        for duelist in DUEL_LISTS:
            if self.search_and_click_image("images/face/" + duelist):
                print ("find player :" + duelist)
                self.next()
                return
        self.failed()

    def search_skip_conversation_btn(self):
        print "[ skip dueler begin conversation ]"
        target = 'images/control/skip.png'
        is_playing = True
        while is_playing:
            if self.search_and_click_image(target):
                is_playing = False
                self.next()

    def search_auto_duel_btn(self):
        print "[ choose auto duel mode ]"
        target = 'images/control/autoduel.png'
        is_playing = True
        while is_playing:
            if self.search_and_click_image(target):
                is_playing = False
                self.next()

    def search_game_finished_btn(self):
        print "[ game playing ]"
        target = 'images/control/ok.png'
        is_playing = True
        while is_playing:
            if self.search_and_click_image(target):
                is_playing = False
                self.next()

    def search_confirm_reward_btn(self):
        print "[ game end and confirm reward ]"
        target = 'images/control/next.png'
        is_playing = True
        while is_playing:
            if self.search_and_click_image(target):
                is_playing = False
                self.next()

    def search_back_to_main_scene_btn(self):
        print "[ back to main scene and skip end conversation ]"
        target = 'images/control/next.png'
        is_playing = True
        while is_playing:
            if self.search_and_click_image(target):
                is_playing = False

        target = 'images/control/skip.png'
        is_playing = True
        while is_playing:
            if self.search_and_click_image(target):
                is_playing = False
                self.next()

    def switch_to_new_screen(self):
        print "[ switch to next scene ]"
        sleep(2)
        slide_left()
        self.next()


if __name__ == '__main__':
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 1

    game = Game()
    game.start()
