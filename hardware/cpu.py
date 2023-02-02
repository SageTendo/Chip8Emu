import random

from hardware.memory import Memory
from utils import sprites

PC_OFFSET = 0x200


class CPU:
    memory = Memory()
    registers = [0x0] * 0x10
    indexReg = 0x0
    stack = []
    delayTimer = 0x0
    soundTimer = 0x0
    speed = 16
    pc = PC_OFFSET

    def __init__(self, screen, keyboard, speaker):
        self.paused = False
        self.keyboard = keyboard
        self.screen = screen
        self.speaker = speaker
        sprites.load_sprites(self.memory)

    def load_program(self, program):
        for i, val in enumerate(program):
            self.memory[PC_OFFSET + i] = val

    def update_timers(self):
        if self.delayTimer > 0:
            self.delayTimer -= 1

        if self.soundTimer > 0:
            self.soundTimer -= 1

    def fetch_instruction(self):
        instruction = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2
        return instruction

    def cycle_cpu(self):
        for i in range(0, self.speed):
            if not self.paused:
                opcode = self.fetch_instruction()
                self.decode_and_execute_instruction(opcode)

        if not self.paused:
            self.update_timers()

    def decode_and_execute_instruction(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        addr = (opcode & 0x0FFF)
        const_8 = (opcode & 0x00FF)
        const_4 = (opcode & 0x000F)

        match (opcode & 0xF000):
            # process opcodes with the same starting value
            case 0x0000:
                if opcode == 0x00E0:
                    self.screen.clear()
                elif opcode == 0x00EE:
                    self.pc = self.stack.pop()
            case 0x8000:
                match (opcode & 0xF00F):
                    case 0x8000:
                        self.registers[x] = self.registers[y]
                    case 0x8001:
                        self.registers[x] |= self.registers[y]
                    case 0x8002:
                        self.registers[x] &= self.registers[y]
                    case 0x8003:
                        self.registers[x] ^= self.registers[y]
                    case 0x8004:
                        result = self.registers[x] + self.registers[y]
                        if result > 0xFF:
                            self.registers[0xF] = 1
                        else:
                            self.registers[0xF] = 0
                        self.registers[x] = result & 0xFF
                    case 0x8005:
                        result = self.registers[x] - self.registers[y]
                        if self.registers[x] > self.registers[y]:
                            self.registers[0xF] = 1
                        else:
                            self.registers[0xF] = 0
                        self.registers[x] = result & 0xFF
                    case 0x8006:
                        shifted_out = self.registers[x] & 0x1
                        self.registers[x] >>= 1
                        self.registers[0xF] = shifted_out
                    case 0x8007:
                        result = self.registers[y] - self.registers[x]
                        if self.registers[y] > self.registers[x]:
                            self.registers[0xF] = 1
                        else:
                            self.registers[0xF] = 0
                        self.registers[x] = result & 0xFF
                    case 0x800E:
                        # FIXME: Carry error
                        shifted_out = self.registers[x] & 0x80
                        self.registers[x] = (self.registers[x] << 1) & 0xFF
                        self.registers[0xF] = shifted_out
            case 0xE000:
                if (opcode & 0xF0FF) == 0xE09E:
                    if self.keyboard.key_pressed(self.registers[x]):
                        self.pc += 2
                elif (opcode & 0xF0FF) == 0xE0A1:
                    if not self.keyboard.key_pressed(self.registers[x]):
                        self.pc += 2
            case 0xF000:
                match (opcode & 0xF0FF):
                    case 0xF00A:
                        self.paused = True
                    case 0xF01E:
                        # TODO
                        self.indexReg += self.registers[x]
                        if self.indexReg > 0xFFF:
                            self.registers[0xF] = 1
                        self.indexReg &= 0xFFF
                    case 0xF007:
                        self.registers[x] = self.get_delay()
                    case 0xF015:
                        self.set_delay_timer(x)
                    case 0xF018:
                        self.set_sound_timer(x)
                    case 0xF029:
                        # FIXME:
                        self.indexReg = self.registers[x]
                    case 0xF033:
                        number = self.registers[x]
                        self.memory[self.indexReg] = number // 100  # Hundreds
                        self.memory[self.indexReg + 1] = (number // 10) % 10  # Tens
                        self.memory[self.indexReg + 2] = number % 10  # Ones
                    case 0xF055:
                        for i in range(0, x + 1):
                            self.memory[self.indexReg + i] = self.registers[i]
                    case 0xF065:
                        for i in range(0, x + 1):
                            self.registers[i] = self.memory[self.indexReg + i]

            # individual instructions
            case 0x1000:
                self.pc = opcode & 0x0FFF
            case 0x2000:
                self.stack.append(self.pc)
                self.pc = (opcode & 0x0FFF)
            case 0x3000:
                if self.registers[x] == const_8:
                    self.pc += 2
            case 0x4000:
                if self.registers[x] != const_8:
                    self.pc += 2
            case 0x5000:
                if self.registers[x] == self.registers[y]:
                    self.pc += 2
            case 0x6000:
                self.registers[x] = const_8
            case 0x7000:
                self.registers[x] += const_8
                self.registers[x] &= 0xFF
            case 0x9000:
                if self.registers[x] != self.registers[y]:
                    self.pc += 2
            case 0xA000:
                self.indexReg = addr
            case 0xB000:
                self.pc = addr + self.registers[x]
            case 0xC000:
                self.registers[x] = (random.randint(0, 255) & const_8)
            case 0xD000:
                x_coord = self.registers[x]
                y_coord = self.registers[y]
                self.registers[0xF] = 0
                self.draw(x_coord, y_coord, const_4)

    def draw(self, x, y, height):
        width = 8
        for row in range(height):
            sprite = self.memory[self.indexReg + row]

            for col in range(width):
                x_pos = (x + col) % self.screen.WIDTH
                y_pos = (y + row) % self.screen.HEIGHT
                if (sprite & 0x80) > 0:
                    if self.screen.get_pixel(x_pos, y_pos) == self.screen.WHITE:
                        self.screen.set_pixel(x_pos, y_pos, self.screen.BLACK)
                        self.registers[0xF] = 1
                    else:
                        self.screen.set_pixel(x_pos, y_pos, self.screen.WHITE)
                        self.registers[0xF] = 0
                sprite <<= 1

    def get_delay(self):
        return self.delayTimer

    def get_key(self, x):
        pressed_key = self.keyboard.key_down()
        while not pressed_key:
            pressed_key = self.keyboard.key_down()
        self.registers[x] = pressed_key

    def set_delay_timer(self, x):
        self.delayTimer = self.registers[x]

    def set_sound_timer(self, x):
        self.soundTimer = self.registers[x]
        self.speaker.play()
