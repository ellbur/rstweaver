
from rstweaver import WeaverLanguage
from docutils import nodes

class Generic(WeaverLanguage):
    
    def __init__(self, **other_options):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'file'
        },
        **other_options
        )
    
    def highlight(self, code):
        return [nodes.inline(code, code)]

