
from rstweaver import WeaverLanguage
from subprocess import Popen, PIPE, STDOUT
import operator

class R(WeaverLanguage):
    
    def __init__(self, **other_options):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'R',
            WeaverLanguage.session:        'sweave'
        },
        **other_options
        )
    
    def run(self, path, wd):
        pass
    
    def start_session(self):
        return RSession(self.context)
    
    def highlight_lang(self):
        return 'r'
    
class RSession(WeaverSession):
    
    def __init__(self, context):
        self.context = context
        from rpy2.robjects import r
        
        r('''
            run.weaver = function(text) {
                options(keep.source=T)
                parsed = parse(text = text)
                
                texts = as.character(attr(parsed, 'wholeSrcref'))
                exprs = lapply(texts, function(t) parse(text = t))
                vals = lapply(exprs, eval.or.message)
                vis  = sapply(vals, function(v) v$visible)
                vals = lapply(vals, function(v) v$value)
                
                list(
                    texts = texts,
                    vals  = vals,
                    vis   = vis
                )
            }

            eval.or.message = function(exp) {
                attributes(exp) = NULL
                if (identical(exp, expression())) {
                    list(value=NULL, visible=FALSE)
                }
                else {
                    withVisible(tryCatch(
                        eval(exp, .GlobalEnv),
                        error = function(e) e
                    ))
                }
            }
        ''')
    
    def run(self, input):
        context.no_cache()
        texts, vals, vis = r.run_weaver(input)
        
        assert len(texts) == len(vals) == len(vis)
        
        texts = [str(text) for text in texts]
        vals  = [str(vals[k] if vis[k] else None) for k in range(len(vals))]
        
        return [(texts[k], vals[k]) for k in range(len(vals))]

