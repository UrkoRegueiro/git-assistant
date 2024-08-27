

#############################################################################
#############################################################################

def load_html_template():
    with open('crew/html_template.html', 'r') as file:
        html_template = file.read()

    return html_template
