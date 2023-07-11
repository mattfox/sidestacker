from django import template

register = template.Library()

BUTTON_CLASSES = {
    '1': "btn-primary",
    '2': "btn-danger",
}
ICON_CLASS = {
    '1': "bi-1-circle",
    '2': "bi-2-circle",
}
ICON_CLASS_FILL = {
    '1': "bi-1-circle-fill",
    '2': "bi-2-circle-fill",
}


@register.filter
def button_class(player):
    """Return the Bootstrap button class to use for this player."""
    return BUTTON_CLASSES[player]


@register.filter
def icon_class(player):
    """Return the Bootstrap icon class to use for this player."""
    return ICON_CLASS[player]


@register.filter
def icon_class_fill(player):
    """Return the Bootstrap filled icon class to use for this player."""
    return ICON_CLASS_FILL[player]



