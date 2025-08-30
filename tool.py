import json
import requests
import env
import yunhuse
import mistune
from mistune.plugins import table


def m_h(word):#已烂尾
    renderer = mistune.HTMLRenderer()
    markdown=mistune.create_markdown(plugins=['table', 'footnotes','url', 'task_lists','strikethrough','footnotes'])
    html_word=markdown(word)
    return html_word


# markdown = create_markdown(plugins=['table', 'footnotes','url','math', 'task_lists','strikethrough','footnotes'])