import plex

class RunError(Exception):
    pass
class ParseError(Exception):
    pass

class MyParser:
    def __init__(self):
        letter = plex.Range('azAZ')
        num = plex.Range('09')
        digit = plex.Range('01')
        andop = plex.Str('and')
        orop = plex.Str('or')
        xorop = plex.Str('xor')
        name = letter + plex.Rep(letter|num)
        space = plex.Any(' \n\t')
        Keyword = plex.Str('print','PRINT')
        binary= plex.Rep1(digit)
        equals = plex.Str( '=')
        parethensys1 = plex.Str('(')
        parethensys2 = plex.Str(')')
        self.varList={}
        self.lexicon = plex.Lexicon([
            (Keyword, 'PRINT_TOKEN'),
            (andop, plex.TEXT),
            (orop, plex.TEXT),
            (xorop, plex.TEXT),
            (name, 'ID_TOKEN'),             #name = letter + plex.Rep(letter|digit)
            (binary, 'BINARY_NUM'),
            (equals, '='),
            (parethensys1, '('),
            (parethensys2, ')'),
            (space, plex.IGNORE)			
        ])

    def createScanner(self,fp):
        self.scanner = plex.Scanner(self.lexicon,fp)
        self.la,self.text = self.next_token()
    
    def next_token(self):
        return self.scanner.read()


    def match(self,token):
        if self.la == token:
            self.la,self.text=self.next_token()
        else:
            raise ParseError("found {} instead of {}".format(self.la,token))
            

    def parse(self,fp):
        self.createScanner(fp)
        self.stmt_list()
        
    def stmt_list(self):
        if self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' : #first set: id,print
            self.stmt()
            self.stmt_list()
        elif self.la == None: #follow set: None
            return
        else: #Error
            raise ParseError('Expected id or print')
            
    def stmt(self):
        if self.la == 'ID_TOKEN': #first,follow set: id,print
            varname = self.text
            self.match('ID_TOKEN')
            self.match('=')
            e = self.expr()
            
            self.varList[varname] = e
            return {'type' : '=', 'text' : varname, 'expr' : e}
        elif self.la == 'PRINT_TOKEN': #first,follow set: id,print
            self.match('PRINT_TOKEN')
            e = self.expr()
            print('= {:b}'.format(e))
            return {'type' : 'print' , 'expr' : e}
        else: #Error
            raise ParseError('Expected id or print')
    
    def expr(self):
        if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY_NUM' : #first set: ( , id , binary number
            t = self.term()
            while self.la == 'xor':
                self.match('xor')
                t2 = self.term()
                print('xor : {:b} ^ {:b} '.format(t,t2))
                t = t^t2
            if self.la == ')' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
                return t
            raise ParseError('Expected xor operator')
        else: #Error
            raise ParseError('Expected a parethensys,an id or a binary number')
            
    def term(self):
        if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY_NUM': #first set: (,id,binary number
            f = self.factor()
            while self.la == 'or':
                self.match('or')
                f2 = self.factor()
                print('or : {:b} or {:b} '.format(f,f2))
                f = f|f2
            if self.la == ')' or self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
                return f
            raise ParseError('Expected | operator')
        else: #Error
            raise ParseError('Expected a parethensys, an id or a binary number')
            
    def factor(self):
        if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY_NUM' : #first set: ( , id , binary number
            a = self.atom()
            while self.la == 'and':
                self.match('and')
                a2 = self.atom()
                print('and : {:b} and {:b} '.format(a,a2))
                a = a&a2
            if self.la == ')' or self.la == 'or' or self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
                return a
            raise ParseError('Expected & operator')
        else: #Error
            raise ParseError('Expected an parethensys, an opperation or a binary number')
            
    def atom(self):
        if self.la == '(' : #first set: ( , id , binary number
            self.match('(')
            e = self.expr()
            self.match(')')
            return(e)
        elif self.la == 'ID_TOKEN' :
            varname = self.text
            self.match('ID_TOKEN')
            if varname in self.varList:
                return self.varList[varname]
            raise RunError("no variable name")
        elif self.la == 'BINARY_NUM' :
            binary_num = int(self.text,2)
            self.match('BINARY_NUM')
            return (binary_num)
        else: #Error
            raise ParseError('Expected parethensys, id or a binary number')
    
parser = MyParser()

with open('input.txt', 'r') as fp:
    parser.parse(fp)
