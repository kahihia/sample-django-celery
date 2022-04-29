from django import template

register = template.Library()


@register.filter
def addClass(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter
def isRadioInput(value):
    return value.field.widget.input_type in ['checkbox', 'radio']

@register.filter
def isFileInput(value):
    return value.field.widget.input_type in ['file', 'image']