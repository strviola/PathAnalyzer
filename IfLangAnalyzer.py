'''
Created on 2013/01/08

@author: SuzukiRyota
'''

from ply.ply import lex, yacc

fname = 'triangle_program.txt'


class Lexer:
    tokens = [# braces
              'BLOCKSTART', 'BLOCKEND', 'LPAREN', 'RPAREN',
              # if-statement symbols
              'QUESTION', 'COLON', 'SEMICOLON',
              # condition operators
              'EQUAL', 'BIGGER', 'LESS',
              'BIGGEREQUAL', 'LESSEQUAL', 'NOTEQUAL',
              # arithmetic operators
              'PLUS', 'MINUS', 'TIMES', 'DIV',
              # etc.
              'ASSIGN', 'VARIABLE', 'INTEGER',
              ]

    # token specification
    t_BLOCKSTART = '{'
    t_BLOCKEND = '}'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_QUESTION = r'\?'
    t_COLON = ':'
    t_SEMICOLON = ';'
    t_EQUAL = '=='
    t_BIGGER = '>'
    t_LESS = '<'
    t_BIGGEREQUAL = '>='
    t_LESSEQUAL = '<='
    t_NOTEQUAL = '!='
    t_PLUS = r'\+'
    t_MINUS = '-'
    t_TIMES = r'\*'
    t_DIV = '/'
    t_ASSIGN = '='
    t_VARIABLE = r'[a-zA-Z_]\w*'
    
    def t_INTEGER(self, t):
        r'(0|-?[1-9]\d*)'
        t.value = int(t.value)
        return t

    # special members
    t_ignore = ' \t\r\f\v'

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1
        self.line_head_pos = t.lexpos + 1

    def t_error(self, t):
        print 'Bad Character "%s"' % t.value[0]
        t.lexer.skip(1)

    # important functions
    def __init__(self):
        self.lex = lex.lex(object=self)
        self.line_head_pos = 0

    def input(self, text):
        self.lex.input(text)

    def token(self):
        return self.lex.token()

    def test(self, text):
        self.input(text)
        while True:
            token = self.token()
            if not token:
                print 'End of text'
                break
            print token, self.line_head_pos


class Parser:
    tokens = Lexer.tokens
    variables = {}

    def __init__(self, **yacc_args):
        self.lexer = Lexer()
        self.yacc_args = yacc_args
        self.parser = yacc.yacc(module=self, **yacc_args)
        self.flag = True

    def parse(self, source_text):
        return self.parser.parse(input=source_text, lexer=self.lexer)

    def p_error(self, t):
        raise SyntaxError('Syntax error at line %d: %s "%s"'
                          % (t.lineno, t.type, str(t.value)))

    # BNF rules
    def p_program(self, p):
        '''
        program : block
        '''
        print 'program'
        p[0] = p[1]

    def p_block(self, p):
        '''
        block : BLOCKSTART statement_array BLOCKEND
        '''
        print 'block'
        p[0] = p[2]
        self.flag = not self.flag

    def p_statement_array(self, p):
        '''
        statement_array : statement SEMICOLON statement_array
            | statement SEMICOLON
            | empty
        '''
        print 'statement_array'
        p[0] = p[1]

    def p_empty(self, p):
        '''
        empty :
        '''
        pass

    def p_statement(self, p):
        '''
        statement : assignment
            | if_statement
        '''
        print 'statement'
        p[0] = p[1]

    def p_assignment(self, p):
        '''
        assignment : VARIABLE ASSIGN expression
        '''
        print 'assignment'
        if self.flag:
            p[0] = p[3]
            self.variables[p[1]] = p[3]
            print self.variables
        else:
            print 'Flag is False'

    def p_expression(self, p):
        '''
        expression : expression PLUS term
            | expression MINUS term
            | term
        '''
        print 'expression'
        if len(p) == 4:
            if p[2] == '+':  # expression + term
                p[0] = p[1] + p[3]
            elif p[2] == '-':  # expression - term
                p[0] = p[1] - p[3]
        else:  # term
            p[0] = p[1]

    def p_term(self, p):
        '''
        term : term TIMES factor
            | term DIV factor
            | factor
        '''
        print 'term'
        if len(p) == 4:
            if p[2] == '*':  # term * factor
                p[0] = p[1] * p[3]
            elif p[2] == '/':  # term / factor
                p[0] = p[1] / p[3]
        else:  # factor
            p[0] = p[1]

    def eval_var(self, arg):
        '''
        Evaluate the variable.
        '''
        if isinstance(arg, int):
            return arg
        elif isinstance(arg, str):
            return self.variables[arg]
        else:
            raise TypeError

    def p_factor(self, p):
        '''
        factor : LPAREN expression RPAREN
            | INTEGER
            | VARIABLE
        '''
        print 'factor'
        if len(p) == 4:  # '(' expression ')'
            p[0] = p[2]
        else:  # INTEGER or VARIABLE
            p[0] = self.eval_var(p[1])

    def p_if_statement(self, p):
        '''
        if_statement : LPAREN condition RPAREN QUESTION block COLON block
        '''
        print 'if_statement', p[2]
        if p[2]:  # boolean value is true
            p[0] = p[5]  # first block
        else:  # false
            p[0] = p[7]  # second block

    def p_condition(self, p):
        '''
        condition : expression EQUAL expression
            | expression BIGGER expression
            | expression LESS expression
            | expression BIGGEREQUAL expression
            | expression LESSEQUAL expression
            | expression NOTEQUAL expression
        '''
        print 'condition'
        if p[2] == '==':
            p[0] = p[1] == p[3]
        elif p[2] == '>':
            p[0] = p[1] > p[3]
        elif p[2] == '<':
            p[0] = p[1] < p[3]
        elif p[2] == '>=':
            p[0] = p[1] >= p[3]
        elif p[2] == '<=':
            p[0] = p[1] <= p[3]
        elif p[2] == '!=':
            p[0] = p[1] != p[3]
        else:
            raise Exception('Invalid character %s' % p[2])
        self.flag = p[0]
        print self.flag

if __name__ == '__main__':
    input_text = ''
    for line in open(fname, 'r'):
        input_text += line
    print 'Program to analyze:\n', input_text
    print 'LEX test:'
    t_lex = Lexer()
    t_lex.test(input_text)
    print
    print 'YACC test:'
    import pprint
    t_yacc = Parser(write_tables=False, debug=False).parse(input_text)
    pprint.pprint(t_yacc)
