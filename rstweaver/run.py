
from docutils.core import publish_parts
from docutils.parsers.rst import directives

from context import WeaverContext
from languages import all_languages
from css import structure_css

weaver_languages = [ ]

def register_weaver_language(language):
    '''
    Add a language to the list of languages. reST directives will
    be added automatically.
    
    See WeaverLanguage.
    
    Parameters:
        language -- A WeaverLanguage
    '''
    context = WeaverContext(language)
    
    for directive in context.directives():
        directives.register_directive(directive.name, directive)
    
    weaver_languages.append(language)
    
def register_all_languages():
    '''
    Registers all languages included in the rstweaver distribution.
    
    They will then take effect when doing reST processing.
    '''
    for lang in all_languages:
        register_weaver_language(lang)

def rst_to_doc(source, css=True, full=False, output_format='html'):
    '''
    Convert the reST input source to an HTML fragment, ie no
    <html>, <body> etc.
    
    This will include some CSS in <style> tags.
    
    Parameters:
        source -- reST input
        css    -- Include <style> tags
        full   -- Include <html>, <body> etc
    
    Returns:
        HTML as a string
    '''
    register_all_languages()
 
    parts = publish_parts(
        source,
        writer_name = output_format
    )
    if output_format == 'html':
        fulltext = parts['fragment']

        if css:
            docutils_css = parts['stylesheet']
            fulltext = (
                  docutils_css
                + style_tags(weaver_css())
                + fulltext
            )
        
        if full:
            fulltext = (
                  parts['head_prefix']
                + parts['head']
                + parts['body_prefix']
                + fulltext
                + parts['body_suffix']
            )
    else:
        if full:
            fulltext = parts['whole']
        else:
            fulltext = parts['body']
 
    return fulltext

def weaver_css():
    '''
    Return a string containing raw CSS related to weaver pages.
    '''
    language_css = ''
    for lang in all_languages:
        language_css += lang.css()
 
    return structure_css + language_css

def style_tags(text):
    return '<style type="text/css">{0}</style>'.format(text)

