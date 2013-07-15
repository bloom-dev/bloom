

def find_seq(seq,first,last,after=0,before=-1):
    '''
    >>> seq = ['a','(','b','c',')','d']
    >>> F,L = find_seq(seq,'(',')')
    >>> seq[F:L]
    ['(', 'c', 'd', 'e',')']
    '''
    first_index = find_next(seq,first,after,before)
    if first_index == []:
        return None,None
    else:
        last_index = find_next(seq,last,after+first_index,before)
        if last_index == []:
            return None,None
        return first_index,last_index

def get_seq(seq,first,last,after=0,before=-1):
    F,L = find_seq(seq,first,last,after,before)
    return seq[F:L+1]

    
def find_next(seq,val,after=0,before=-1):
    if before < 0:  #convert negative indexes to positive
        before = len(seq) + before + 1
    res = [i for i in find(seq,val)
                if i >= after
                and i <= before]
    if res == []:
        return []
    else:
        return res[0]

def find_last(seq,val,after=0,before=-1):
    if before < 0:  #convert negative indexes to positive
        before = len(seq) + before + 1
    res = [i for i in find(seq,val)
                if i >= after
                and i <= before]
    if res == []:
        return []
    else:
        return res[-1]
    

def find(seq,val):
    return [i for i,elm in enumerate(seq)
        if elm == val]
