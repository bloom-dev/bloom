import shlex
import re
#------ custom modules
from organizers import Configuration


#REFACTOR:
#So that Expressions are a variety of Token
#... or perhaps Token and Expression are both Nodes
#... and NodeList contains Nodes (~ self.nodes --> self.nodes)





#--------- Examples and Debugging Code -------
tags = {'boobs':set([1,2,3,4,5]),
        'tits':set([4,5,6]),
        'parasite':set([5,7,8,9]),
        'icecream':set([2,4,8,10,11]),
        'wangs':set([2,3,8,9,10,12]),
        'mountains':set([1,4,12,13,14])
        }
ex1 = 'boobs or (parasite and icecream)'
ex2 = '(boobs or parasite) and icecream'
ex3 = '(boobs and tits) not (wangs not (tits or mountains))'
ex4 = '(boobs and tits) or (wangs not (tits or mountains))'
bad3= '(boobs and tits) not (wangs and (peoples or mountains)'


#---------- Parameters
_param = Configuration()
_param.token_categories = [['(','['],
                           [')',']'],
                           ['and','*','&'],
                           ['or','+','|'],
                           ['not','-']] #If not one of these --> must be a tag
_param.logicals = ['and','or','not']
_param.valid_tag_re = "^[A-Za-z0-9_-]*$"   #letters, numbers, '-', and '_'. All others - reserved categories.



class Token(object):
    '''Token types may be '(',')','and','or','not','tag'.
    Two types of creation:
    (1) Standard: creates a token based on input string. Standardizes parenthesis forms and
        operator names (ex. '&'-->'and'), and does error checking on tag names.
    Ex. Token('mountains')
    (2) Combined Tag Lists: used primarily when combining tags after a logical operation. 
        Only used to create tokens of type 'tag' (not the operators or parentheses).
        Specifies name and contents directly. Does not do error checking on name.
    Ex. Token(name='(mountains and hills)',contents=my_tag_list)
    '''
    def __init__(self,token_string=None,name=None,contents=None):
        if token_string is not None:    #Method #1: Standard - create token from input string
            #replaces token_string with the first entry in category
            #    Ex.  '[' --> '(',  '&' --> 'and'
            for category in _param.token_categories:    #If token is in one of the reserved categories
                if token_string in category:    
                    self.type = category[0]         #Standard representation
                    self.name = category[0]         #self.name = token_string
                    return
            else:   #If token is not one of the TokenCategories - IE the 'for' did not break
                if re.match(_param.valid_tag_re,token_string):
                    self.type = 'tag'
                    self.name = token_string
                    
                    if contents is None:
                        self.contents = tags[token_string]         #ONLY USED IN DEBUGING - should be replaced by SQL calls
                    else:
                        self.contents = contents
                    return
                else:   #Invalid string
                    raise Exception("Invalid tag name - {0} contains a forbidden character.".format(token_string))
        elif name is not None and contents is not None: #Method #2 - Combined: 
            self.type = 'tag'
            self.name = name
            self.contents = contents
            return
        else:
            raise Exception("Invalid Token initialization: either specify a single token_string, OR specify a name and contents (by Keywords).")
    def get_contents(self): #Used to provide a generic contents access method between expressions and Tokens
        if self.type =='tag':
            return self.contents
        else:
            raise Exception("Tokens of type {0} do not have contents.".format(self.type))
    def __str__(self):  #str() / print()
        return self.name
    def __repr__(self):
        return str(self.__dict__)
    def __getitem__(self,key):  #translates: Token()['contents']-->Token().contents
        return self.__getattribute__(key)
    def __eq__(self,other):   # Logical equality '==' operator
        return str(self.name) == str(other)
    def __contains__(self,item):   #"item in TAG"/"item not in TAG"
        if self.type != 'tag':
            raise TypeError('in <{0}> not valid for tags of type '.format(type(other),self.type))
        return (item in self.contents)


class Expression(object):
    '''An object consists of a list of Token() and Expression() objects.
    Any '('/')' Token objects will be parsed out and replaced with Expression() objects.
    ''' 
    def __init__(self,node_list,sublist=False):
        self.nodes = node_list
        self.type = 'expression'
        
        self.set_indexes()          #Number/index tokens
        #@deprecated: .set_depths() now extracted as a seperate list inside .replace_expressions()
        #self.set_depths()           #Used to find the 'deepest' sub-Expression
        self.replace_expressions()       #Replaces nested statements with Expression objects
    #------------- Work horse functions
    def process(self,token=None):
        '''Assumes all parenthesis have been removed, and replaced with Expressions.'''
        if token is None:
            #Process left-to-right (~doesn't worry about precedence atm)
            
            if len(self.nodes) == 1:
                if self[0].type == 'expression':
                    self.nodes[0].process()
                elif self[0].type == 'tag':   #If it is a tag
                    pass    #Do nothing
                else:   #It is in ['and','or','not']
                    raise Exception("Invalid Expression = {0}".format(self.nodes))
                     
                 
            for token in self:
                self.process(token)   #This does nothing for 'tag' Tokens()
                #self.process(token.index)
            #Now there should only be one element in self.nodes - one Token object
            if len(self.nodes) != 1:
                raise Exception("self.process() code not working correctly.")
                
        else:   #token_number is an integer --> treat as index into self.contents[]
            i = token.ind
            if self[i].type not in ['and','or','not']:  #If an expression or a tag
                pass #Do nothing
            else:   #If a logical statement
                #Do logical replacement
                left = self[i-1]
                oper = self[i]
                right = self[i+1]
                
                #Expression().get_content() -- will cause that expression to be processed.
                new_set = set_logic(oper.type,left.get_contents(),right.get_contents())
                
                #[] Replace slice left,operator,right --> new_set
                new_name = "'"+" ".join([left.name,oper.name,right.name])+"'"
                new_node = Token(name=new_name,contents=new_set)
                node_slice = self.nodes[left.ind:(right.ind+1)]
                
                self.replace(node_slice,new_node)
 
    
    #----------- Replacing Sub-Expressions
    def replace_expressions(self):
        '''Replace parenthesized expressions with Expression() nodes, depth first.
        Look for parenthesis pairs in the tokens, and replace 
        them with Expression() objects.''' 
        nested = self.next_nested() #Find deepest parenthesis pair
        while nested != None:
            self.replace(nested)
            nested = self.next_nested()
    def next_nested(self,depths=None):
        if depths is None:
            depths = self.depths()
        max_depth = max(depths)
        
        #[] Find Next: '(' which are at the max depth still in list
        #    Deepest '(' --> implies it contains no other '('
        for token,depth in zip(self.nodes,depths):
            if token.type == '(' and depth == max_depth:
                front = token
                break
        else:   #No '(' remain
            return None
        
        #[] Find Next: ')' -- next occuring after front token
        back = find_next(self[front.ind:],')')
        if back == None:    #If there was no ')' in this expression
            raise Exception("Mismatched parenthesis for: "+str(self.nodes[front_index:]))                
        
        #[] Get slice of nodes, and turn into an expression
        #return Expression(self.nodes[(front.ind+1):back.ind])
        nested_slice = self.nodes[front.ind:(back.ind+1)]
        
        return nested_slice
    def depths(self):
        depths = []
        current_depth = 0
        for i,token in enumerate(self.nodes):      #Depth increments on '(', and decrements on ')'
            if token == '(':
                current_depth += 1
            elif token == ')':
                current_depth -= 1
            depths.append( current_depth )
        if current_depth != 0:      #if it doesn't end at depth == 0
            Exception("Unbalanced parenthesis for Expressions = ."+str(self))
        return depths            
    def replace(self,node_slice,new_node=None):
        if new_node is None:
            new_node = Expression(node_slice[1:-1]) #Remove first and last element of slice --> parenthesis
        #new_node.name = new_node.get_name()
        new_node.name = " ".join([node.name for node in node_slice])
        first = node_slice[0].ind
        last = node_slice[-1].ind + 1
        self[first:last] = [new_node]
        self.set_indexes()
    


    
    #------------- Access & Utility Functions
    def set_indexes(self):
        for i in range(len(self.nodes)):
            self.nodes[i].ind = i
    def get_contents(self):
        if len(self.nodes) == 1:    #if this only consists of one node - such as for (1) already processed expressions, or (2) expressions containing expressions
            if self.nodes[0].type == 'expression':
                return self[0].get_contents()
            else:
                return self[0].contents
        else:
            self.process()
            return self[0].contents
    def get_name(self):
        return " ".join(str(token) for token in self.nodes)
    def __str__(self):
        '''Print the string for this object.'''
        #return " ".join(str(token) for token in self.nodes)
        return "'"+self.get_name()+"'"
    def __repr__(self):
        if globals().get('pprint',False):   #if module exists
            return pprint.pformat(self.nodes)
        else:
            return "["+",\n".join(repr(token) for token in self.nodes)+"]"
    def __iter__(self):
        return iter(self.nodes)
    #------- Expression['item'] indexing --
    def __getitem__(self,key):  #myTokens['depths']
        if type(key) == slice or type(key) == int:  #slice indexing
            return self.nodes[key]
        elif type(key) == str:
            if key in ['depths','depth']:
                return self.depths()
            elif key in ['content','contents']:
                return [node.get_contents() for node in self.nodes]
            else:
                return [token.__dict__.get(key,None)        #Use 'None' as default value if key does not exist in token 
                    for token in self.nodes]
        else:
            raise KeyError("Invalid key: {0} for {1}".format(repr(key),self.__class__.__name__))
    def __setitem__(self,key,value):
        if type(key) == slice:
            self.nodes[key.start:key.stop:key.step] = value
        elif type(key) == int:
            self.nodes[key] = value
        else:
            raise KeyError("Invalid key: {0} for {1}".format(repr(key),self.__class__.__name__))
    def __delitem__(self,key):
        if type(key) == slice or type(key) == int:
            del self.nodes[key]
        elif type(key) == str:
            for i in range(len(self.nodes)):
                del self.nodes[i][key]
        else:
            raise KeyError("Invalid key: {0} for {1}".format(repr(key),self.__class__.__name__))

#=====================================
#  Utility Functions
#=====================================
def set_logic(operation,left,right):
    #operation: and/or/not Token
    #left/right: Token or Expression
    if operation == 'and':
        return (left & right)
    elif operation == 'or':
        return (left | right)
    elif operation == 'not':
        return (left - right)
    else:
        raise Exception("You should never see this set logic error.")

def find_next(haystack,targets):
    if type(targets) is str:
        targets = [targets]
        
    for elm in haystack:
        if elm in targets:
            return elm
    else:
        return None

def tokenize_strings(in_strings):
    lexer = shlex.shlex(in_strings) #intelligently splits on spaces or parenthesis/brackets
    return list(lexer)

def print_slice(slice):
    print " ".join([str(elm) for elm in slice])
    


    
if __name__ == "__main__":
    token_strings = tokenize_strings(ex3)
    tokens = [Token(token_str) for token_str in token_strings]
    root_expr = Expression(tokens)      #Replace '(' ')' with expressions objects (depth-first)
    
    root_expr.process()                 #Evaluate - recursively calculating expressions objects
    repr(root_expr)
    print(root_expr)
    print(root_expr.get_contents())

    token_strings = get_token_strings(ex4)
    tokens = [Token(token_str) for token_str in token_strings]
    root_expr = Expression(tokens)      #Replace '(' ')' with expressions objects (depth-first)
    
    root_expr.process()                 #Evaluate - recursively calculating expressions objects
    repr(root_expr)
    print(root_expr)
    print(root_expr.get_contents())