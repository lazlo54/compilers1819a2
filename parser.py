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
		name = letter + plex.Rep(letter|num)
		space = plex.Any(' \n\t')

		Keyword = plex.Str('print','PRINT')
		binary= plex.Rep1(digit)

		equals = plex.Str( '=')
		andop = plex.Str('&')
		orop = plex.Str('|')
		xorop = plex.Str('^')
		parethensys1 = plex.Str('(')
		parethensys2 = plex.Str(')')
		self.varList={}
		self.lexicon = plex.Lexicon([
            (Keyword, 'PRINT_TOKEN'),
			(name, 'ID_TOKEN'),             #name = letter + plex.Rep(letter|digit)
			(binary, 'BINARY_NUM'),
			(equals, '='),
			(andop, plex.TEXT),
			(orop, plex.TEXT),
			(xorop, plex.TEXT),
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
        elif self.la == 'PRINT_TOKEN': #first,follow set: id,print
            self.match('PRINT_TOKEN')
            self.expr()
        else: #Error
            raise ParseError('Expected id or print')
    
    def expr(self):
        if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY_NUM' : #first set: ( , id , binary number
            self.term()
            self.term_tail()
        elif self.la == ')' or self.la == 'ID_TOKEN' or self.la == None or self.la == 'PRINT_TOKEN' : #follow set: ) , id , print , None
            return self.term()
        else: #Error
            raise ParseError('Expected a parethensys,an id or a binary number')
            
    def term_tail(self):
        if self.la == '^': #first set: token xor
            self.match('^')
            self.term()
            self.term_tail()
        elif self.la == ')' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None: #follow set: ),id,print
            return
        else: #Error
            raise ParseError('Expected an opperation')
            
    def term(self):
        if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY_NUM': #first set: (,id,binary number
            self.factor()
            self.factor_tail()
        else: #Error
            raise ParseError('Expected a parethensys, an id or a binary number')
            
    def factor_tail(self):
        if self.la == '|' : #first set: token or
            self.match('|')
            self.factor()
            self.factor_tail()
        elif self.la == ')' or self.la == '^' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None: #follow set: ) , xor , id ,print
            return
        else: #Error
            raise ParseError('Expected an opperation')
            
    def factor(self):
        if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY_NUM' : #first set: ( , id , binary number
            self.atom()
            self.atom_tail()
        else: #Error
            raise ParseError('Expected an parethensys, an opperation or a binary number')
            
    def atom_tail(self):
        if self.la == '&' : #first set: and token
            self.match('&')
            self.atom()
            self.atom_tail()
        elif self.la == ')' or self.la == '|' or self.la == '^' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None: #follow set: ) , or , xor , id ,print
            return
        else: #Error
            raise ParseError('Expected an opperation')
            
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
            raise RunError("no value")
        elif self.la == 'BINARY_NUM' :
            binary_num = self.text
            self.match('BINARY_NUM')
            return binary_num
        else: #Error
            raise ParseError('Expected parethensys, id or a binary number')

parser = MyParser()

with open('input.txt', 'r') as fp:
	parser.parse(fp)
