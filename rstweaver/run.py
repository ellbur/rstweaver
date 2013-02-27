
from docutils.core import publish_parts, publish_string
from docutils.parsers.rst import directives
from docutils.parsers import rst
import docutils

from context import get_weaver_context, WeaverContext
from languages import all_languages
from css import structure_css
import re
import os
import shutil
import optparse # Yeah baby
from subprocess import Popen
from tempfile import mkstemp

import rstload

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

def rst_to_doc(source, languages, wd=None, css=True, full=False, output_format='html',
        clear_cache=False, inverted=False, stylesheet=None):
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
        clear_cache   -- Clear the cache before running
    
    Returns:
        HTML as a string
    '''
    context = WeaverContext(
        wd = wd,
        languages = languages,
        clear_cache = clear_cache
    )
    
    rdirs = context.directive_dict()
    rdirs['load'] = rstload.LoadDirective
    parser = rst.Parser(
        run_directives = rdirs
    )
 
    if inverted:
        source = invert(source)
 
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
            
    elif output_format == 'pdf':
        settings = dict()
        if stylesheet != None:
            _, blah = mkstemp(suffix='.tex', dir='.')
            shutil.copy(stylesheet, blah)
            settings['stylesheet_path'] = blah
        
        fulltext = publish_string(
            source,
            writer_name = 'latex',
            parser = parser,
            settings_overrides = settings
        )
        print(fulltext)
        fd, path = mkstemp(suffix='.tex', dir='.')
        with os.fdopen(fd, 'w') as hl:
            hl.write(fulltext)
            hl.close()
        if Popen(['rubber', '--inplace', '--pdf', path]).wait() != 0:
            raise Exception('Failed to run rubber')
        
        if stylesheet != None:
            os.unlink(blah)
        
        pdf_path = re.sub(r'\.tex$' , '.pdf', path)
        with open(pdf_path, 'rb') as hl:
            fulltext = hl.read()
        os.unlink(path)
        os.unlink(pdf_path)
        return fulltext
            
    else:
        fulltext = publish_string(
            source,
            writer_name = output_format,
            parser = parser
        )
 
    if output_format == 'html':
        fulltext = fulltext.encode('utf-8')
        
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

def invert(source):
    lines = re.findall(r'[^\n]*\n', source)
    state = 'comment'
    output = ''
    
    for line in lines:
        if line.startswith('#!'):
            continue
        
        if state == 'comment':
            if line.startswith('#'):
                output += re.sub(r'^\# ?', '', line)
            elif len(line.strip()) > 0:
                state = 'code'
                output += '\n.. py::\n\n'
                output += '    ' + line
            else:
                output += '\n'
        else:
            if line.startswith('#'):
                state = 'comment'
                output += '\n'
                output += re.sub(r'^\# ?', '', line)
            else:
                output += '    ' + line
    
    print(output)
    return output

