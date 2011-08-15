
from docutils.core import publish_parts, publish_string
from docutils.parsers.rst import directives
from docutils.parsers import rst

from context import get_weaver_context, WeaverContext
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
    
    weaver_context = get_weaver_context()
    language = language(context = weaver_context)
    
    weaver_context.register_global_directives()
    weaver_context.register_language_directives(language)
    weaver_context.languages.append(language)
    weaver_languages.append(language)
    
def register_all_languages():
    '''
    Registers all languages included in the rstweaver distribution.
    
    They will then take effect when doing reST processing.
    '''
    for lang in all_languages:
        register_weaver_language(lang)

def rst_to_doc(source, languages, wd=None, css=True, full=False, output_format='html'):
    '''
    Convert the reST input source to the output format.
    
    If the output is html, this will include some CSS in <style> tags.
    
    Parameters:
        source        -- reST input
        languages     -- List of weaver languages to use
        wd            -- Place to put auxilary output (like generated source files)
        css           -- Include <style> tags
        full          -- Include <html>, <body> etc
        output_format -- passed to publish_parts as writer_name
    
    Returns:
        HTML as a string
    '''
    context = WeaverContext(
        wd = wd,
        languages = languages
    )
    parser = rst.Parser(
        run_directives = context.directive_dict()
    )
 
    if output_format == 'html' and (css or not full):
        parts = publish_parts(
            source,
            writer_name = output_format,
            parser = parser
        )

        if css:
            docutils_css = parts['stylesheet']
            css_html = (
                  docutils_css
                + style_tags(weaver_css(context))
            )
        else:
            css_html = ''
        
        if full:
            fulltext = (
                  parts['head_prefix']
                + parts['head']
                + css_html
                + parts['body_prefix']
                + parts['html_body']
                + parts['body_suffix']
            )
            
        else:
            fulltext = (
                  css_html
                + parts['fragment']
            )
            
    else:
        fulltext = publish_string(
            source,
            writer_name = output_format,
            parser = parser
        )
 
    return fulltext

def weaver_css(context):
    '''
    Return a string containing raw CSS related to weaver pages.
    '''
    language_css = ''
    for lang in context.languages:
        language_css += lang.css()
 
    return structure_css + language_css

def style_tags(text):
    return '<style type="text/css">{0}</style>'.format(text)

