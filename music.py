import pygame, random


class Music():
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.mixer.init()
        self.music_on = True
        self.music_effects = True
        self.ping = pygame.mixer.Sound('snd/pong.wav')
        self.ping.set_volume(0.2)
        if self.music_on:
            self.playMenu()
        self.fail = pygame.mixer.Sound('snd/fail.wav')
        self.fail.set_volume(0.5)
        self.next = pygame.mixer.Sound('snd/nextlvl.wav')
        self.next.set_volume(0.5)

    def playMenu(self):
        pygame.mixer.music.load('snd/menu.wav')
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play()

    def playGame(self):
        pygame.mixer.music.load('snd/play.mp3')
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.1)

    def playPunch(self):
        pygame.mixer.music.load('snd/punch.wav')
        pygame.mixer.music.play()

    def playFail(self):
        pygame.mixer.Sound.play(self.fail)

    def playNext(self):
        pygame.mixer.Sound.play(self.next)

    def playBounce(self):
        pygame.mixer.Sound.play(self.ping)
