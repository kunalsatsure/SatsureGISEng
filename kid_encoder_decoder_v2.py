import re 

def encode_khasraid(a:str,b:str,c:str,sep:str = '') -> str:
    """
    a : patthar
    b : murabba
    c : kila

    to encode [patthar, murabba, kila] to 18 digit khasara_number "020903420050002500"
    """

    if a.find('/') == -1:
        a += '/0'

    if b.find('/') == -1:
        b += '/0'

    if c.find('/') == -1:
        c += '/0'
        
    a_nchars = 8
    b_nchars = 6
    c_nchars = 4

    aa = [i.rjust(4, "0") for i in a.split('/')]
    bb = [i.rjust(3, "0") for i in b.split('/')]
    cc = [i.rjust(2, "0") for i in c.split('/')]

    aaa = ''.join(aa)
    bbb = ''.join(bb)
    ccc = ''.join(cc)

    a = aaa if len(aaa) >= a_nchars else '0'.join(aa)
    b = bbb if len(bbb) >= b_nchars else '0'.join(bb)
    c = ccc if len(ccc) >= c_nchars else '0'.join(cc)

    a = a.rjust(a_nchars, "0")
    b = b.rjust(b_nchars, "0")
    c = c.rjust(c_nchars, "0")

    return sep.join([a,b,c])

def decode_khasraid(kid:str) -> list[str]:
    """
    kid : khasra number str(18 digit)

    to decode a khasra number "020903420050002500" to [patthar, murabba, kila]
    """
    parts = [[kid[0:4] , kid[4:8]], [kid[8:11] , kid[11:14]], [kid[14:16] , kid[16:18]]]
    for i, part in enumerate(parts):
        for j, p in enumerate(part):
            try:
                parts[i][j] = str(eval(p))
            except:
                parts[i][j] = str(eval(re.sub(r'^[0]+','',p)))

    return ['/'.join(i).replace('/0','') for i in parts]
