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
    """
    :param child: The child node on first level
    :return: dictionary of IDs
    """
    # Get all child elements of the link
    children_of_child = d(child).children()

    # Links can have four types of arrow states:
    # 0: no arrows at all
    # 1: ID1 <-  ID2
    # 2: ID1 ->  ID2
    # 3: ID1 <-> ID2
    arrowstate = d(child).attr('arrowstate')
    # Store the IDs in a dictionary
    linked_nodes = {'arrowstate': arrowstate}

    # to postfix the IDs
    counter = 1
    # Iterate over the child elements...
    for n in children_of_child:
        # ... looking for nodes
        if d(n).attr('xsi:type') == 'node':
            # put them in the list
            linked_nodes['id' + str(counter)] = d(n).text()
            counter += 1
    return linked_nodes


def get_urlresources_if_any(n):
    urlresource = d(n).children('resource')
    if urlresource and urlresource.attr('xsi:type') == 'URLResource':
        text = '#### Quelle ####\n\n'
        text += '* ' + urlresource.children('property').attr('value') + '\n\n'
        return text
    else:
        return ''


def build_headline_for_links(link, node_dictionary):
    """
    Builds the headline for linked nodes
    :param link: HTML object
    :param node_dictionary: dictionary with IDs and arrow state
    :return: String
    """
    if int(node_dictionary['arrowstate']) == 1:
        return '### %s --%s--> %s ###\n\n' % (
            get_label_for_linked_node(node_dictionary['id2']),
            get_label_for_link(link),
            get_label_for_linked_node(node_dictionary['id1'])
        )

    if int(node_dictionary['arrowstate']) == 2:
        return '### %s --%s--> %s ###\n\n' % (
            get_label_for_linked_node(node_dictionary['id1']),
            get_label_for_link(link),
            get_label_for_linked_node(node_dictionary['id2'])
        )

    if int(node_dictionary['arrowstate']) == 3:
        return '### %s <--%s--> %s ###\n\n' % (
            get_label_for_linked_node(node_dictionary['id1']),
            get_label_for_link(link),
            get_label_for_linked_node(node_dictionary['id2'])
        )

    if int(node_dictionary['arrowstate']) == 0:
        return '### %s --%s-- %s ###\n\n' % (
            get_label_for_linked_node(node_dictionary['id1']),
            get_label_for_link(link),
            get_label_for_linked_node(node_dictionary['id2'])
        )
    else:
        return ''



def get_label_for_linked_node(id):
    """
    Reads the label text for the linked node
    :param id: the ID of the linked node
    :return: String
    """
    label = d('#' + id).attr('label')
    return label


def get_label_for_link(l):
    """
    Reads the label text of a node
    :param l: html object
    :return: String
    """
    return d(l).attr('label')


for t in children:
    label = d(t).attr('label')
    child_type = d(t).attr('xsi:type')

    # Get all the nodes
    if child_type == 'node':
        notes = d(t).children('notes')
        file += '### %s ###\n\n' % label
        if notes:
            file += d(notes).text() + '\n\n'
        resources = get_urlresources_if_any(t)
        if resources != '':
            file += resources

    # Get all the links
    if child_type == 'link':
        n_dictionary = get_linked_nodes(t)
        notes = d(t).children('notes')
        if label:
            file += build_headline_for_links(t, n_dictionary)
        if notes:
            file += d(notes).text() + '\n\n'

f.write(file)
f.close()
