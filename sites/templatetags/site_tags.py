from django import template

register = template.Library()


@register.inclusion_tag('sites/grade.html')
def grade(scan):
    return {
        'grade': scan.grade['grade'],
        'class_name': scan.grade['class_name']
    }
