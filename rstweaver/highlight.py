
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import _get_ttype_class
import re
from docutils import nodes
from uuid import uuid4

def highlight_as(code, lang):
    # You don't want to know.
    if lang == 'c':
        hack = re.sub(r'\d', '', uuid4().hex)
        left_space  = re.search(r'^(\s*)', code).group(1)
        right_space = re.search(r'(\s*)$', code).group(1)
        tokens = list(pygments.lex(code.strip()+'\n\n'+hack, get_lexer_by_name(lang)))[:-1]
        
        for n in reversed(range(len(tokens))):
            ttype, text = tokens[n]
            if hack not in text and text.strip() != '':
                tokens[n] = ttype, text.rstrip()
                break
            
        def make_nodes():
            yield nodes.inline(left_space, left_space)
            for ttype, text in tokens[:n+1]:
                yield nodes.inline(text, text, classes=[
                    _get_ttype_class(ttype)
                ])
            yield nodes.inline(right_space, right_space)
        return list(make_nodes())
    
    else:
        left_space  = re.search(r'^(\s*)', code).group(1)
        right_space = re.search(r'(\s*)$', code).group(1)
        inner_code = code.lstrip().rstrip()
        tokens = list(pygments.lex(inner_code, get_lexer_by_name(lang)))[:-1]
        
        def make_nodes():
            yield nodes.inline(left_space, left_space)
            for ttype, text in tokens:
                yield nodes.inline(text, text, classes=[
                    _get_ttype_class(ttype)
                ])
            yield nodes.inline(right_space, right_space)
        return list(make_nodes())
        

