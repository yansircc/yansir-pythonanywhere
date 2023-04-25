from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import urllib.request

class HighlightInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('span')
        el.set('class', 'anki-highlight')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)

class HighlightExtension(Extension):
    def extendMarkdown(self, md):
        HIGHLIGHT_PATTERN = r'!!(.*?)!!'
        md.inlinePatterns.register(HighlightInlineProcessor(HIGHLIGHT_PATTERN, md), 'highlight', 175)

class HideInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('span')
        #el.set('class', 'anki-hide')
        # el.set('onclick', 'this.classList.remove("anki-hide")')
        el.set('class', 'ak-cover')
        el.set('onclick', 'if(this.style.color == "rgb(0, 0, 0)"){this.style.color = "#F4EDB3";}else{this.style.color = "#000000";}')
        el.set('style', 'color: rgb(244, 237, 179);')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)

class HideExtension(Extension):
    def extendMarkdown(self, md):
        HIDE_PATTERN = r'\?\?(.*?)\?\?'
        md.inlinePatterns.register(HideInlineProcessor(HIDE_PATTERN, md), 'hide', 175)

class latexInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('script')
        el.set('src', 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-MML-AM_CHTML')
        return el, m.start(0), m.end(0)

class latexExtension(Extension):
    def extendMarkdown(self, md):
        LATEX_PATTERN = r'\$\$(.*?)\$\$'
        md.inlinePatterns.register(latexInlineProcessor(LATEX_PATTERN, md), 'latex', 175)