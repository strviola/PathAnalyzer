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
    flag_root = 'root'
    flag_true = 'true'
    flag_false = 'false'

    def __init__(self, **yacc_args):
        self.lexer = Lexer()
        self.yacc_args = yacc_args
        self.parser = yacc.yacc(module=self, **yacc_args)
        self.root = 'Something error'
        self.asgn_count = 0
        self.cond_count = 0
        self.block_count = 1
        self.asgn_buffer = []
        self.stmt_buffer = []
        self.block_temp = None
        self.stmt_temp = None
        self.block_temp_true = None
        self.block_temp_false = None
        self.if_flag = self.flag_root
        self.condition = ''

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
        self.root = pt.Program(self.block_temp)
        print self.root
        # program operation

    def p_block(self, p):
        '''
        block : BLOCKSTART statement_array BLOCKEND
        '''
        print 'block'
        p[0] = p[2]
        temp_block = pt.Block(self.stmt_buffer)
        print self.stmt_buffer
        if self.if_flag == self.flag_root:
            self.block_temp = temp_block
            print 'block_temp'
        elif self.if_flag == self.flag_true:
            self.block_temp_true = temp_block
            print 'b true'
            self.if_flag = self.flag_false
        elif self.if_flag == self.flag_false:
            self.block_temp_false = temp_block
            print 'b_false'
            self.if_flag = self.flag_root
        self.stmt_buffer = []

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
        self.stmt_buffer.append(self.stmt_temp)

    def p_assignment(self, p):
        '''
        assignment : VARIABLE ASSIGN expression
        '''
        print 'assignment'
        stmt = ' '.join([str(e) for e in p[1:]])
        self.stmt_temp = pt.Assignment(self.asgn_count, stmt)
        self.asgn_count += 1

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
        self.stmt_buffer.append(pt.IfStatement(self.cond_count, self.condition,
            self.block_temp_true, self.block_temp_false))

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
        self.condition = ' '.join(str(s) for s in p[1:])
        self.if_flag = self.flag_true

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
    t_yacc = Parser(write_tables=False, debug=False).parse(input_text)
