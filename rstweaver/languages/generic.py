
from rstweaver import WeaverLanguage

class Generic(WeaverLanguage):
    
    def __init__(self, **other_options):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'file'
        },
        **other_options
        )
    
    def highlight_lang(self):
        return 'txt'

