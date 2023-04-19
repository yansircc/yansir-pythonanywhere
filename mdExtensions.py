from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree

class HighlightInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('span')
        el.set('style', 'color: #ebc345')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)

class HighlightExtension(Extension):
    def extendMarkdown(self, md):
        HIGHLIGHT_PATTERN = r'!!(.*?)!!'
        md.inlinePatterns.register(HighlightInlineProcessor(HIGHLIGHT_PATTERN, md), 'highlight', 175)
