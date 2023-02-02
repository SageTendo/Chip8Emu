class Memory:
    """
    x000 to x1FF := CHIP-8 interpreter (512 Bytes)
    x200 to xE9F := ROM loading (3232 Bytes)
    xEA0 to xEFF := Internal operations [call stack, misc variable] (96 Bytes)
    xF00 to xFFF := Display refresh (256 Bytes)
    """

    class UnderflowError(ArithmeticError):
        pass

    memory = [0x0] * 0x1000

    def __setitem__(self, addr: hex, data: hex):
        if data > 0xFF:
            raise Exception("Data exceeds 1 Byte")
        if data < -0x7F:
            raise self.UnderflowError(f"Data: {data} at location: {addr}")
        self.memory[addr] = data

    def __getitem__(self, addr: hex):
        return self.memory[addr]

    def __sizeof__(self):
        return len(self.memory)

    def __len__(self):
        return self.__sizeof__()
