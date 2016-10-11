from django import template

register = template.Library()

# NOTE: This logic is duplicated in /client/src/javascript/leaderboardtemplate.jade
# If you update it here, remember to make the corresponding change there.
@register.inclusion_tag('sites/grade.html')
def grade(site):
    scan = site.scans.latest('timestamp')
    score = scan.score
    if score > 80:
        grade = 'A'
        class_name = 'grade-a'
    elif score > 60:
        grade = 'B'
        class_name = 'grade-b'
    elif score > 40:
        grade = 'C'
        class_name = 'grade-c'
    elif score > 20:
        grade = 'D'
        class_name = 'grade-d'
    else:
        grade = 'F'
        class_name = 'grade-f'
    return { 'grade': grade, 'class_name': class_name }
