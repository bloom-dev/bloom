import shlex
import re
#------ custom modules
from organizers import Configuration


#---------- Parameters
_param = Configuration()
_param.reserved_categories = {
    '('     : ['(','[','{'],
    ')'     : [')',']','}'],
   'and'    : ['and','*','&'],
   'or'     : ['or','+','|'],
   'not'    : ['not','-']
   }    #If not one of these --> must be a tag
_param.valid_tag_re = "^[A-Za-z0-9_-]*$"   #letters, numbers, '-', and '_'. All others - reserved categories.


#========================================
#  Primary Interface Functions
#========================================
def evaluate(tokens):
    return Expression(tokens).contents
def evaluate_searchstring(searchstr,tags_ids_dict):
    tokens = [lex.Token(name) for name in lex.tokenize(searchstr)]
    tags = [t.type for t in tokens
            if t.type == 'tag']
    set_tag_ids(tags_ids_dict)
    return Expression(tokens).contents
def validate(tokens):
    for tok in tokens:
        if tok.type in _param.reserved_categories.keys():
            pass
        #If name is a valid tag 
        elif re.search(_param.valid_tag_re,tok.name):   #if not 
            pass
        else:
            raise Exception("Invalid token name - {0} contains a forbidden character.".format(tok.name))

#========================================
#  'Work-horse' Functions
#========================================
class Token(object):
    '''Token types may be '(',')','and','or','not','tag'.'''
    def __init__(self,name,contents=None):
        self.type = Token._standardize(name)
        self.name = name
        if contents is not None:
            self.contents = contents
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
        return str(self) == str(other)
    def __contains__(self,item):   #"item in TAG"/"item not in TAG"
        if self.type != 'tag':
            raise TypeError('in <{0}> not valid for tags of type '.format(type(other),self.type))
        return (item in self.contents)
    #-------- Static Function
    @staticmethod
    def _standardize(name):
        #Returns a token type if a valid token, else throws an exception
        for category_name,category_values in _param.reserved_categories.items():
            if name in category_values:
                return category_name
        else:
            return 'tag'
   

class Expression(object):
    '''An object consists of a list of Token() and Expression() objects.
    Any '(' or ')' Token objects will be parsed out and replaced with Expression() objects.
    Use Expression().contents to execute processing. ''' 
    def __init__(self,node_list,sublist=False):
        self.nodes = node_list  #nodes ~ tokens, except may contain other Expressions
        self.type = 'expression'

        self.set_indexes()          #Number/index tokens
        #Replace nested '()' with Expression() objects
        for nested in self.nested():
            self.replace(nested)
    #------------- Work horse functions
    def process(self,token=None):
        '''Assumes all parenthesis have been removed, and replaced with Expressions.
        For 'tag' tokens, does nothing. After processing, there should only be 
        one element remaining in self.nodes - one Token (tag) object.
        '''
        if token is None:
            #Process left-to-right (~doesn't worry about precedence atm)
#            if len(self.nodes) == 1:
#                if self[0].type == 'expression':
#                    self.nodes[0].process()
#                elif self[0].type == 'tag':   #If it is a tag
#                    pass    #Do nothing
#                else:   #It is in ['and','or','not']
#                    raise Exception("Invalid Expression = {0}".format(self.nodes))
            for token in self:
                self.process(token)
                
        else:   #token_number is an integer --> treat as index into self.contents[]
            i = token.ind
            #If a logical statement, do logical replacement
            #Else, do nothing
            if self[i].type in ['and','or','not']:  #If an expression or a tag
                left,oper,right = self[i-1:i+2]
                
                new_set = set_logic(oper.type,left.contents,right.contents)
                #New name is simply a concatentation of the old ones
                new_name = "'"+" ".join([left.name,oper.name,right.name])+"'"
                new_node = Token(new_name,contents=new_set)
                #[] Replace slice left,operator,right --> new_set
                node_slice = self.nodes[left.ind:(right.ind+1)]
                self.replace(node_slice,new_node)
 
    
    #----------- Replacing Sub-Expressions
    def nested(self):
        '''Generator for nested expressions (~parenthesized sub-segments).'''
        while (True):
            depths = self.depths
            max_depth = max(depths)
            #[] Find Next: '(' which are at the max depth still in list
            #    Deepest '(' --> implies it contains no other '('
            for token,depth in zip(self.nodes,depths):
                if token.type == '(' and depth == max_depth:
                    front = token
                    break
            else:   #No '(' remain
                raise StopIteration
            
            #[] Find Next: ')' -- next occuring after front token
            back = Expression.find_next(self[front.ind:],')')
            if back == None:    #If there was no ')' in this expression
                raise Exception("Mismatched parenthesis for: "+str(self.nodes[front.ind:]))                
            
            #[] Get slice of nodes, and turn into an expression
            nested_slice = self.nodes[front.ind:(back.ind+1)]
            yield nested_slice
        
    @property   #Makes: self.depths() <--> self.depths
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
    @property
    def contents(self):
        '''Triggers process()ing on this expression.'''
        if len(self.nodes) == 1:    #if this only consists of one node - such as for (1) already processed expressions, or (2) expressions containing expressions
            if self.nodes[0].type == 'expression':
                return self[0].contents
            else:
                return self[0].contents
        else:
            self.process()
            return self[0].contents        
    def replace(self,node_slice,new_node=None):
        if new_node is None:
            new_node = Expression(node_slice[1:-1]) #Remove first and last element of slice --> parenthesis
        new_node.name = " ".join([node.name for node in node_slice])
        first = node_slice[0].ind
        last = node_slice[-1].ind 
        self[first:(last+1)] = [new_node]
        self.set_indexes()
    #------------- Access & Utility Functions
    def set_indexes(self):
        for i in range(len(self.nodes)):
            self.nodes[i].ind = i
    def get_contents(self):
        return self.contents
    def __str__(self):
        '''Print the string for this object.'''
        names = " ".join(str(token) for token in self.nodes)
        return "'"+names+"'"
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
                return [node.contents for node in self.nodes]
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
    @staticmethod    
    def find_next(haystack,targets):
        if type(targets) is str:
            targets = [targets]
        for elm in haystack:
            if elm.type in targets:
                return elm
        else:
            return None
        
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

def tokenize(in_string):
    lexer = shlex.shlex(in_string) #intelligently splits on spaces or parenthesis/brackets
    return list(lexer)      #lexer ~ iterator/generator. Must list() to instantiate it.
def tokenize(in_string):
    '''Tokenizes `in_string`, intelligenctly splitting on spaces and parenthesis/brackets.
    However, since it uses code from shlex, it does not handle unicode. Therefore,
    unicode strings are converted to ascii (removing any non-ascii characters), tokenized,
    then converted back to unicode.'''
    in_type = type(in_string)   
    if in_type is unicode:
        in_string = in_string.encode('ascii','ignore')
        lexer = shlex.shlex(in_string) #intelligently splits on spaces or parenthesis/brackets
        tokens = [unicode(elm) for elm in lexer]
    elif in_type is str:
        lexer = shlex.shlex(in_string) #intelligently splits on spaces or parenthesis/brackets
        tokens = list(lexer)    #lexer ~ iterator/generator. Must instantiate it (~in this case by converting to list)
    else:
        raise TypeError("tokenize() received input of type '{0}', instead of type unicode or type str (aka ascii).".format(in_type))
    return tokens    


def print_slice(slice):
    print " ".join([str(elm) for elm in slice])
    
def set_tag_ids(tokens,tags_dict):
    ''' tokens: list of Token() objects
        tags_dict: dict of tag names, containing lists of ids.
    '''
    for tok in tokens:
        if tok.type == 'tag':
            tok.contents = tags_dict[tok.name]


#--------- Examples and Debugging Code -------
_testing = {}
_testing['tags'] = {'boobs':set([1,2,3,4,5]),
        'tits':set([4,5,6]),
        'parasite':set([5,7,8,9]),
        'icecream':set([2,4,8,10,11]),
        'wangs':set([2,3,8,9,10,12]),
        'mountains':set([1,4,12,13,14])
        }
_testing['valid'] = [
    'boobs',
    'boobs or (parasite and icecream)',
    '(boobs or parasite) and icecream',
    '(boobs and tits) not (wangs not (tits or mountains))',
    '(boobs and tits) or (wangs not (tits or mountains))',
    '(boobs | parasite} & icecream',
    ]
_testing['invalid'] = [
    '(boobs and tits) not (wangs and (peoples or mountains)',       #mismatched parenthesis ==> should be `or mountains))`.
    'boobs and not tits',           #sequential operators ==> `and not`
    'boobs && tits',                 #invalid operator ==> `&&`
    'wangs |'                       #missing tag ==> `wangs | MISSING`
    ]
_testing['edge'] = [
    'notarealtag',                                          #tag not in DB - should evaluate to empty
    'boobs | invalid'                                       #should evaluate to same as `boobs`
    ]


if __name__ == "__main__":
    #========    Test valid strings
    for searchstr in _testing['valid']:
        try:
            searchstr = unicode(searchstr)          #Convert to unicode for testing.
            token_names = tokenize(searchstr)
            tokens = [Token(name) for name in token_names]
            set_tag_ids(tokens,_testing['tags'])
            root_expr = Expression(tokens)      #Replace '(' ')' with expressions objects (depth-first)
            ids = root_expr.contents
            print("SUCCESS: "+str(root_expr)+" = "+str(ids))
        except Exception as exc:
            print("FAILURE: "+str(root_expr)+" encountered Exception = "+str(exc))
    
    #========    Test invalid strings
    for searchstr in _testing['invalid']:
        try:
            searchstr = unicode(searchstr)          #Convert to unicode for testing.
            token_names = tokenize(searchstr)
            tokens = [Token(name) for name in token_names]
            set_tag_ids(tokens,_testing['tags'])
            root_expr = Expression(tokens)      #Replace '(' ')' with expressions objects (depth-first)
            ids = root_expr.contents
            raise AssertionError
        except AssertionError as exc:
            raise AssertionError("FAILURE: "+searchstr+" did NOT error - this is a problem")
        except Exception as exc:
            print("SUCCESS: Exception: for '"+searchstr+"' -- which is what should happen.")