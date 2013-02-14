'''
Created on 2013/01/08

@author: SuzukiRyota
'''

from ply.ply import lex, yacc
import PathTree as pt

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
        self.root = pt.Program()
        self.asgn_count = 0
        self.cond_count = 0
        self.block_count = 1

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
        cond = ' '.join([str(e) for e in p[1:]])
        self.root.add_assignment(pt.Assignment(self.cond_count, cond))
        self.cond_count += 1

    def p_expression(self, p):
        '''
        expression : expression PLUS term
            | expression MINUS term
            | term
        '''
        print 'expression'

    def p_term(self, p):
        '''
        term : term TIMES factor
            | term DIV factor
            | factor
        '''
        print 'term'

    def p_factor(self, p):
        '''
        factor : LPAREN expression RPAREN
            | INTEGER
            | VARIABLE
        '''
        print 'factor'

    def p_if_statement(self, p):
        '''
        if_statement : LPAREN condition RPAREN QUESTION block COLON block
        '''
        print 'if_statement', p[2]

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
