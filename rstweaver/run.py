
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

def rst_to_html(source, css=True, full=False):
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
    for lang in all_languages:
        register_weaver_language(lang)
 
    parts = publish_parts(
        source,
        writer_name = 'html'
    )
    docutils_css = parts['stylesheet']
    
    language_prefix = ''
    for lang in weaver_languages:
        language_prefix += lang.html_prefix()

    fulltext = parts['fragment']

    if css:
        fulltext = (
              docutils_css
            + structure_css
            + language_prefix
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
 
    return fulltext


