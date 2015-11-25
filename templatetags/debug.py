import pdb as dbg
from django.template import Library, Node
register = Library()

class PdbNode(Node):
    def render(self, context):
        dbg.set_trace()
        return ''

@register.tag
def pdb(parser, token):
    return PdbNode()
