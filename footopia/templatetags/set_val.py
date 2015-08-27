from django import template

register = template.Library()

class SetValNode(template.Node):

    def __init__(self, variable_name, variable_value):
        self.variable_name = variable_name
        self.variable_value = variable_value

    def render(self, context):
        try:
            value = template.Variable(self.variable_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context.dicts[0][self.variable_name] = value
        return u""

def set_val(parser, token):
    """
        {% set <variable_name>  = <variable_value> %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %}")
    return SetValNode(parts[1], parts[3])

register.tag('set', set_val)
