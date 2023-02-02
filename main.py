import sys
import pygame
from hardware.cpu import CPU
from hardware.keyboard import Keyboard
from hardware.screen import Screen
from hardware.speaker import Speaker


def read_rom_file(file):
    return open(file, 'rb').read()


def handle_event():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            keyboard.key_down(event)
            cpu.paused = False

        if event.type == pygame.KEYUP:
            keyboard.key_up(event)


if __name__ == '__main__':
    filename = 'roms/INVADERS'
    rom_data = read_rom_file(file=filename)

    screen = Screen()
    keyboard = Keyboard()
    speaker = Speaker()
    cpu = CPU(screen=screen, keyboard=keyboard, speaker=speaker)
    cpu.load_program(rom_data)
    # cpu.memory[0x1FF] = 4
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        handle_event()
        cpu.cycle_cpu()
        screen.refresh()
