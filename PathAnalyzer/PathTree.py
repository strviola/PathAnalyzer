class Program:
    def __init__(self):
        self.block = Block(0)

    def add_statement(self, stmt):
        self.block.statements.append(stmt)

    def to_executional_path(self):
        pass  # TODO: implement


class Block:
    def __init__(self, number):
        self.number = number
        self.statements = []

    def __str__(self):
        return '\n'.join([str(x) for x in self.statements])


class IfStatement:
    def __init__(self, number, condition, block_true, block_false):
        self.number = number
        self.condition = condition
        self.block_true = block_true
        self.block_false = block_false

    def __str__(self):
        return ('I%d: (%s)\n{%s}{%s}' % (self.number, self.condition,
                str(self.block_true), str(self.block_false)))

class Assignment:
    def __init__(self, number, body):
        self.number = number
        self.body = body

    def __str__(self):
        return 'A%d: %s' % (self.number, self.body)
