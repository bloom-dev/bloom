import shlex
import re
#------ custom modules
from organizers import Configuration
from utility import find_next


#-------- 

#--------- Examples and Debugging Code -------
tags = {'boobs':[1,2,3,4,5],
        'tits':[4,5,6],
        'parasite':[5,7,8,9],
        'icecream':[2,4,8,10,11],
        'wangs':[2,3,8,9,10,12],
        'mountains':[1,4,12,13,14]
        }
ex1 = 'boobs or (parasite and icecream)'
ex2 = '(boobs or parasite) and icecream'
ex3 = '(boobs and tits) or not (wangs and not (tits or mountains))'
ex4 = '(boobs and tits) or not (wangs and not "tits or mountains")'
bad3= '(boobs and tits) or (wangs and (peoples or mountains)'


#---------- Parameters
_param = Configuration()
_param.token_categories = [['(','['],
                           [')',']'],
                           ['and','*','&'],
                           ['or','+','|'],
                           ['not','-']] #If not one of these --> must be a tag
_param.valid_tag_re = "^[A-Za-z0-9_-]*$"   #letters, numbers, '-', and '_'


class Token(object):
    def __init__(self,token_string):
        for category in _param.token_categories:    #If token is in one of the reserved categories
            if token_string in category:
                self.type = category[0]         #Standard representation
                self.name = category[0]
                break
        else:   #If token is not one of the TokenCategories - IE the 'for' did not break
            if re.match(_param.valid_tag_re,token_string):
                self.type = 'tag'
                self.name = token_string
                self.contents = tags[token_string]    #ONLY USED IN DEBUGING
            else:   #Invalid string
                raise Exception("Invalid tag name - contains a forbidden character.")
    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self.__dict__)
    def __eq__(self,other):   # '==' operator
        return str(self) == str(other)

#
class Node(Token):
    def __init__(self,token_string):
        Token.__init__(self,token_string)
        if self.type in ['and','or','not']:
            self.left
            self.right

class NodeList(object):
    def __init__(self,token_list,sublist=False):
        self.tokens = token_list
        if sublist is False:        #sublists do not need depths calculated
            self.find_depths()
        #Number/index tokens
        for i in range(len(self.tokens)):
            self.tokens[i].index = i
    #------------- Work horse functions
    def set_depths(self):
        current_depth = 0
        for i,token in enumerate(self.tokens):
            self.tokens[i].depth = current_depth
            if token == '(':
                current_depth += 1
            elif token == ')':
                current_depth -= 1
        if current_depth != 0:      #if it doesn't end at depth == 0
            Exception("Unbalanced parenthesis.")
    def find_innermost_nest(self):
        max_depth = max(self['depth'])
        #[] Find '(' which are at the max depth still in list
        front_parens = [token for token in self.tokens
                        if token.type == '('
                        and token.depth == max_depth]
        
        #find_next(self['type'][front:],')'),
        back_parens = []
        for front in front_parens:
            #Look for closest subsequent ')'
            for token in self.tokens[front.index:]:   #The slice from the '(' to the end
                if token.type == ')':
                    back_parens.append( token )
            else:   #if a back token was not found
                raise Exception("Mismatched parenthesis for: "+str(self.tokens[front.index:]))
                
        for i,token in enumerate(self.tokens):
            if (token.type == '(') and (token.depth == max_depth):
                front = i
                break
        
    #------------- Utility Functions
    def __str__(self):
        return " ".join(str(token) for token in self.tokens)
    def __repr__(self):
        if globals().get('pprint',False):   #if module exists
            return pprint.pformat(self.tokens)
        else:
            return "["+",\n".join(repr(token) for token in self.tokens)+"]"
    def __getitem__(self,key):  #myTokens['depths']
        accumulator = []
        for token in self.tokens:
            try:
                accumulator.append( token.__getattribute__[key] )
            except:
                accumulator.append( None )
        return accumulator
    def names(self):
        return [token.name for token in self.tokens]
    def types(self):
        return [token.type for token in self.tokens]
    def depths(self):
        depths = []
        for token in self.tokens:
            try:
                depths.append( token.depth )
            except:
                depths.append( -1 )
        return depths
            
        



def get_token_strings(in_strings):
    lexer = shlex.shlex(in_strings)
    return list(lexer)
    
if __name__ == "__main__":
    token_strings = get_token_strings(ex3)
    tokens = [Token(token_str) for token_str in token_strings]
    raw_token_list = NodeList(tokens)
    innermost = raw_token_list.get_innermost_
    #[] Replace subexpression
    
    print(raw_token_list)