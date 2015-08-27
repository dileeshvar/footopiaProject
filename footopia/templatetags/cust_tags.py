from django.template import Library

register = Library()

@register.filter
def get_range( value, start = 0 ):
  """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
  """
  return [v + start for v in range(value)]

@register.filter  
def compare_date(d1, d2):
	return d1 > d2