""" Parser and converter for VUE Concept Maps
    The intention is to convert the contents of the
    map to a markdown file in order to get a structured
    print of the annotations and notes of nodes and links.

    Author: Axel Dürkop <axel.duerkop@tu-harburg.de>
    Date: 2015-05-10
"""

from pyquery import PyQuery as pq
from lxml import etree

# Store the generated Markdown here
file = ''

f = open('./parsed.markdown', 'w')

# I use the HTML-Parser to catch the xsi:type attributes
# which does not work with XML parser
d = pq(filename='./ConceptMap.vue', parser='html')
# Get all children of the map
children = d('child')


def get_linked_nodes(child):
    # Get all child elements of the link
    children_of_child = d(child).children()
    # Store the IDs in a list
    linked_nodes = []

    # Iterate over the child elements...
    for n in children_of_child:
        # ... looking for nodes
        if d(n).attr('xsi:type') == 'node':
            # put them in the list
            linked_nodes.append(d(n).text())
    # print the list
    # print(linked_nodes)
    return linked_nodes


def get_text_of_linked_nodes(node_list):
    labels = []
    for n in node_list:
        node = d('#' + n).attr('label')
        labels.append(node)
    return labels


for t in children:
    label = d(t).attr('label')
    child_type = d(t).attr('xsi:type')

    # Get all the nodes
    if child_type == 'node':
        notes = d(t).children('notes')
        file += '### %s ###\n\n' % label
        if notes:
            file += d(notes).text() + '\n\n'

    # Get all the links
    if child_type == 'link':
        n_list = get_linked_nodes(t)
        end, start = get_text_of_linked_nodes(n_list)
        notes = d(t).children('notes')
        if label:
            file += '### %s %s %s ###\n\n' % (start, label, end)
        if notes:
            file += d(notes).text() + '\n\n'

f.write(file)
f.close()


