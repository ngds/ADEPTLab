class Token:
    def __init__(self, word, pos, length, tag=-1):
        self.word = word
        self.pos = pos
        self.length = length
        self.tag = tag
    def __str__(self):
        return str(self.word) + ": position " + str(self.pos) + ", length " + str(self.length) + ", tag " + str(self.tag)