import time

import pygame.mixer


class Speaker:
    pygame.mixer.init()
    pygame.mixer.music.load('resources/beep.mp3')

    @staticmethod
    def play():
        pygame.mixer.music.play()

    @staticmethod
    def stop():
        pygame.mixer.music.stop()


if __name__ == '__main__':
    speaker = Speaker()
    speaker.play()
    time.sleep(1)
