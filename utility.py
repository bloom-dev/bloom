import json
import xml.etree.ElementTree as ElementTree
import collections
import re
import difflib
import os

def replacements(in_string,old_substrings,new_substrings):
    """Replaces multiple substrings in 'in_string'"""
    for (old,new) in zip(old_substrings,new_substrings):
        in_string = in_string.replace(old, new)
    return in_string

def convert_to_string(data):
    if isinstance(data, unicode):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_to_string, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_to_string, data))
    else:
        return data

def read_json(file_name):
    #note: to turn resultant dictionary into local variables (inside the calling function)
    #have the calling function execute: locals().update(_conf) 
    config = json.load(open(file_name))
    return convert_to_string(config)

def cast_as_list(x):
    if isinstance(x,list):
        return x
    else:
        return [x]
    
def intersection(a, b):
    return list(set(a) & set(b))

def begins_with(haystack,needle):
    return haystack[:len(needle)] == needle
            


def filter_positive(many_haystacks,many_needles):
    '''Return any element of haystacks which contains 
    *at*least*one* element of needles. 
    '''
    return [haystack for haystack in haystacks for needle in needles if needle in haystack]
    #for needle in many_needles:
    #    many_haystacks = [haystack for haystack in many_haystacks if needle in haystack]
    #return many_haystacks

def filter_negative(many_haystacks,many_needles):
    '''Return any element (hay) of many_haystacks which contains 
    *none* of the elements from many_needles.'''
    return [haystack for haystack in haystacks for needle in needles if not needle in haystack]
    #for needle in many_needles:
    #    many_haystacks = [haystack for haystack in many_haystacks if not needle in haystack]
    #return many_haystacks


def cut(haystack,needle):
    return re.sub(needle,"",haystack) 


def cutter(haystack,needles):
    ''' Kludg-y iterative version of cut(). Old, now deprecated in favor of meta_map(cut,haystack,needles).'''
    if hasattr(needles,"__iter__"):
        for word in needles:
            haystack = cut(haystack,word)
    else:
        haystack = cut(haystack,word)
    return haystack



def create_empty(n, constructor=list):
    '''Returns a generator for creating a set number of empty objects.
    To make a list of lists
    >>> result = list(create(10))
    To make a list of empty dicts
    >>> result = list(create(20, dict))
    To make a tuple of empty Foos,
    >>> result = list(create(30, Foo))
    '''
    for _ in xrange(n):
        yield constructor()

class Debug(object):
    '''Just a C-style struct object used simply to group debugging variables.'''
    def __init__(self,flag=True):
        self.flag = flag
    def __nonzero__(self):
        return self.flag

def xml_to_dict(t):
    '''
    Translates XML (from package ElementTree) into a Python dictionary
    This cannot handle XML tags with attributes. (<TAG ATTRIBUTE="...">TEXT</TAG>)
    >>> tree = ElementTree.parse('../config_vars.xml')
    >>> root = tree.getroot()
    >>> _config = xml_to_dict(root)
    '''
    children = list(t)
    
    if not list(children):
        #It has no children --> now provide it's text data
        d = {t.tag: t.text}
    else:
        #Has children
        d = {t.tag : map(xml_to_dict, children)}
    #d.update(('@' + k, v) for k, v in t.attrib.iteritems())
    return d

def read_xml(xml_file_path):
    '''
    This was added by OJP (not the author of the , as a very basic example of use.
    >>> tree = ElementTree.parse('../config_vars.xml')
    >>> root = tree.getroot()
    >>> _config = XmlDictConfig(root)
    '''
    tree = ElementTree.parse(xml_file_path)
    root = tree.getroot()
    xmldict = xml_to_dict(root)
    return xmldict
def read_xml_config(xml_file_path):
    tree = ElementTree.parse(xml_file_path)
    root = tree.getroot()
    children = list(root)
    _config = {}
    for child in children:
        _config[child.tag] = child.text
    return _config 


#-------------- Customized XML config file readers
def merge_dicts(L):
    return dict((k,v) for d in L for (k,v) in d.items())
def xml2dict(t):
    #@todo: if all children are named by consecutive integers, begining with <1> or <0>, then turn it to a list
    children = list(t)
    
    if not list(children):
        #It has no children --> now provide it's text data
        d = {t.tag: t.text}
    else:
        #Has children
        d = {t.tag : merge_dicts(map(xml2dict, children))}
        #if all(re.match('i[0-9]+$',ind) for ind in d.keys()):    #if the tags are all named <i0>, <i1> etc
        
        
    #d.update(('@' + k, v) for k, v in t.attrib.iteritems())
    return d
def import_xml_config(xml_file_path):
    '''An improved method of importing xml config files.
    Details and requirements: 
    (1) no two children of the same parent have the same tag name.
    (2) The outermost tag (usually <configuration>) will be removed.
    '''
    
    tree = ElementTree.parse(xml_file_path)
    root = tree.getroot()
    xmldict = xml2dict(root)
    return xmldict.values()[0]      #remove outermost tag (usually '<config>'
def dict2xml(D,xml_string="",depth=0):
    '''Convert moderately complicated dictionaries to XML strings. Ignores xml attributes. 
    Supports contents which are themselves dicts, lists, tuples, strings, numbers, and maybe more.
    >>> sample = {  'a': 'a contents',
                    'b': {'c': 'c contents',
                          'd': {'d1':'d1 contents', 
                                'd2':'d2 contents'},    },
                    'e': range(3),
                    'f': {'f1':123}    }
    >>> sample_xml = dict2xml(sample)
    '''
    for k,v in D.items():
        #[] Open tag
        xml_string += "{pad}<{name}>".format(pad="\t"*depth,name=k)
        
        #[] Iterate through children, or add contents
        if hasattr(v,"__iter__"): #if child is an iterable container (tuple,list, dict, set, but NOT string)
            if not isinstance(v,collections.Mapping):   #if it is not a dict, or dict-like
                v = dict(("i"+str(i),elm) for i,elm in enumerate(v))
                #v = dict(enumerate(v))      #turn into a dict, using index #s as keys
            xml_string += "\n"
            xml_string = dict2xml(v,xml_string,depth+1)
            #[] Close tag: with padding
            xml_string += "{pad}</{name}>\n".format(pad="\t"*depth,name=k)
        else:
            #[] Close tag: If closing without inner iteration -- do not add padding
            xml_string += "{content}</{name}>\n".format(content=v,name=k)
    return xml_string    
#---------



def read_json_config(json_file_path):
    json_dict = read_json(json_file_path)
    return json_dict.itervalues().next()    #remove root node
    

def check_enumerated(subject,valid_list):
    return any(subject == x for x in valid_list)

def lcs(s1,s2):
    '''Calculates the longest common substring shared by inputs.
    Returns (loc_in_s1,loc_in_s2,sz_of_match,match_string)'''
    sm = difflib.SequenceMatcher()
    sm.set_seqs(s1, s2) 
    (i,j,sz) = sm.find_longest_match(0, len(s1), 0, len(s2))
    #note: s1[i:i+sz] is equal to s2[j:j+sz]
    return (i,j,sz,s1[i:i+sz])

def get_by_keys(mydict,key_list):
    #this would be best handled by dictionary comprehensions - which only appear in Python 2.7
    #... and I'm using 2.6
    return dict([(k,v) for k,v in mydict.iteritems() if k in key_list])
    
def map_inclusive(elm,map_dict):
    if elm in map_dict.keys():
        return map_dict[elm]
    else:
        return elm

def pretty_view(obj):
    '''Used during console debugging. 
    Prints the __dict__ variable of an object,
    with each entry on a seperate line.
    >>> obj={'column': 'drug_name',
             'page_id': 'Name',
             'page_tag': 'td',
             'table': 'drug'}
    >>> print(pretty_view(obj))
    {'column': 'drug_name'
     'page_id': 'Name'
     'page_tag': 'td'
     'table': 'drug'}
    '''
    #Ex.  
    if hasattr(obj,"__dict__"):
        return "\n".join(str(obj.__dict__).split(","))
    else:
        return None
    
def detail(obj,filt = lambda attr: True):
    '''Similar to pretty_view(obj), but provides a small amount of information
    on contents of each attribute.
        filt: applied to the name of the attribute.
    Example:
    >>> obj={'column': 'drug_name','page_id': 'Name','page_tag': 'td','table': 'drug'}
    >>> detail(obj)                            #Prints all attributes
    >>> detail(obj,lambda x: "__" not in x)    #Prints all public attributes
    '''
    max_len = 20
    #Get attribute,type,snippet of content
    for attr_name in dir(obj):
        try:
            if filt(attr_name):
                attr = obj.__getattribute__(attr_name)
                attr_type = cut(str(type(attr)),'<type ')
                attr_snippet = str(attr) #take first 20 characters
                print("{0: <20} - {1: <20} - {2: <20}".format(attr_name[0:max_len],
                                                              attr_type[0:max_len],
                                                              attr_snippet[0:max_len]))
        except Exception as exc:
            print(exc)  #Do not raise exceptions


def add_attributes(obj,new_attributes):
    '''Adds attributes of obj, taking key value pairs from dict 'new_attr'.
    setting obj.key=value'''
    for key,value in new_attributes.items():
        #obj.key=value    #doesn't work for some reason
        obj.__dict__[key] = value
    return obj
def merge_objects(obj,**kwargs):
    '''Adds kwargs to attributes of obj.'''
    for key,value in kwargs.items():
        obj.__setattr__(key,value)
    return obj


def is_empty(param):
    return (not param) and (param is not False)

def get_attributes(class_instance):
    return dict([(name,attr) for name, attr in class_instance.__dict__.items()
            if not name.startswith("__") 
            and not callable(attr)])
    
def get_method_names(class_instance):
    return [method for method in dir(class_instance) if callable(getattr(class_instance, method))]

def obj_to_dict(class_instance):
    seq = []
    for name, attr in class_instance.__dict__.items():
        if not name.startswith("__") and not callable(attr):
            if hasattr(attr,"__dict__"):    #if more complexity is nested
                nested = obj_to_dict(attr)
                seq += [(name,nested)]
            else:
                seq += [(name,attr)]
    return dict(seq)

def map_sequence(seq,map_dict,inclusive_flag=True):
    '''Maps values of seq via map_dict. If elements of seq are not
    in the keys of map_dict, sets that value based on inclusive_flag:
    True  --> do not change elm
    False --> remove elm
    else  --> set elm == inclusive_flag
    '''
    if inclusive_flag is True:
        return [map_dict[elm] if (elm in map_dict.keys()) else elm 
                for elm in seq]
    elif inclusive_flag is False:
        return [map_dict[elm] 
                for elm in seq 
                if elm in map_dict.keys()]
    else:
        return [map_dict[elm] if (elm in map_dict.keys()) else inclusive_flag
            for elm in seq]

def force_end(in_string,suffix):
    '''Forces a string to have a specific suffix.'''
    if not in_string.endswith(suffix):
        in_string += suffix
    return in_string

def ensure_dir(dir_name):
    '''Check if a directory name (relative or absolute path) exists.
    If not, makes it. Windows and linux compatible.'''
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

def ensure_iterable(obj):
    if not hasattr(obj,"__iter__"):
        return [obj]
    return obj

def describe(in_object,output_type=str):
    #@todo: expand this to (1) act recursively, so as to also print sub-objects which are named __dict__,
    #        (2) this recursion should show up in the str() printing as extra indention
    #        (3) a max_depth parameter should be accepted (default: max_depth=2)
    def get_traits(val):
        elm_type = val.__class__.__name__
        try:
            elm_len = len(val)
        except:
            elm_len = None 
        return (elm_type,elm_len)
    
    indent_whitespace = "  " 
    obj_traits = []
    obj_traits.append((None,get_traits(in_object)))
    
    if hasattr(in_object,"__dict__"):
        for key,val in in_object.__dict__.items():
            obj_traits.append((key,get_traits(val)))
    
    if output_type == str:
        out_str = ""
        for i,(name,traits) in enumerate(obj_traits):
            if i != 0:
                out_str += indent_whitespace
            out_str += "key: '{0:>18}', type={1:>12}, len={2:>12}\n".format(name,traits[0],traits[1])               #{0:>12} ~~ align to 12 spaces

        return out_str 
    else:
        return output_type(obj_traits)      #tested for : list,tuple,dict
        



def partial_format(in_string,*format_args,**format_dict):
    ''' Similar to "STRING".format(TAGS), but does not require all {tag}s in the string to be in TAGS.
    Caution: This function does NOT error if given format tags which do not exist in in_string.
    >>> mystr = "I have {a} blank {b} inside {c} borders. But not {d} enough."
    >>> partial_format(mystr,dict(a="too",b="format tags",d="quite"))
    '''
    for i,new_value in enumerate(format_args):               #Replace the numbered format tags - {0},{1}, etc
        in_string = in_string.replace('{'+str(i)+'}',new_value)
        
    for tag_name,new_value in format_dict.items():           #Replace the named format tags - {name}
        in_string = in_string.replace('{'+tag_name+'}',new_value)
    return in_string

def find_next(haystack,target):
    for i,elm in enumerate(haystack):
        if elm == target:
            return i,elm
    else:
        return None
        
def find_indices(haystack,target):
    accumulator = []
    for i,elm in enumerate(haystack):
        if elm == target:
            accumulator.append(i)

#============= IN PROGRESS
def meta_map(haystacks,needles,func):
    '''
    Examples:
    fruits = ['American plum','African mango','Beach plum','Cocoplum','American persimmon','Passion fruit']
    contains = lambda haystack,needle: haystack if needle in haystack else None
    contained = lambda haystack,needle: needle if needle in haystack else None
    
    meta_filter(,)
    '''
    if isinstance(func,str):
        if func == "contains":
            func = lambda haystack,needle: haystack if needle in haystack else None
        elif func == "contained":
            func = lambda haystack,needle: needle if needle in haystack else None
        elif (func == "fitler_positive") or (func == "filter positive"):
            func = lambda haystack,needle: haystack if needle in haystack else None
        elif (func == "fitler_negative") or (func == "filter negative"):
            func = lambda haystack,needle: haystack if needle not in haystack else None
        else:
            raise Exception("Unrecognized ")
    #Ensure inputs are iterable containers (strings are not, for this purpose) 
    if not hasattr(haystacks,"__iter__"):
        haystacks = [haystacks]
    if not hasattr(needles,"__iter__"):
        needles = [needles]
    return [func(haystack,needle) for haystack in haystacks for needle in needles]
    
def abstracted_selector_mapping(input_obj,iterator,boolean_filter,selector):
    '''
    input_obj: ex. input_obj.haystack = [...], input_obj.needles = [...]
                    input_obj.extra_details = ...
    iterator: determines how to iterate through combinations of input_obj.
        Ex. product, linear, pairs, etc. of the traits.
    boolean_filter: accepts a 'combination' returned by the iterator function.
    selector: determines what information about the 'combination' is to be returned.
    '''
    #Even more abstracted:
    #    Adds 'calculator' before boolean_filter. Basically:
    #    for combination in iterator(input_obj):
    #        result = calculator(combination)
    #        if boolean_filter(result):
    #            yield selector(combination,result)
    for combination in iterator(input_obj):
        if boolean_filter(combination):
            yield selector(combination)
#============= FUTURE FUNCTIONS    
#def prettify_xml(xml_string):
#''' >>> print(prettify_xml(dict2xml(myDict))) '''
#def projection(pre_image,projection_map):
#  returns only those elements of pre_image who have an index or key
#  which is also an index/key of project_map
#    
#.... basically return the elements of projection_map who have keys in pre_image
#.... with some legwork to support this for lists and dicts.
#
#... Question: what do I actually want to do with elements of pre_image whose keys
# are NOT In project_map?  Leave them alone or drop them?


