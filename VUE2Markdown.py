#! /usr/bin/python3.4

""" Converter for VUE Concept Maps
    Converts the contents of a VUE concept map to a markdown file
    by printing the notes of nodes and links.

    This script makes use of the PyQuery library
    (https://pypi.python.org/pypi/pyquery/1.2.9)

    :author: Axel Dürkop <axel.duerkop@tu-harburg.de>
    :date: 2015-05-10
"""

import os
import re
from pyquery import PyQuery as pq

# Filename of the VUE document
vue_filename = 'ConceptMap.vue'
# Filename of output Markdown file
markdown_filename = 'parsed.markdown'
# Headline of the document
document_headline = 'Concept Map Webtechnologien'
# Filename of the PDF file generated from the map
pdfmap_filename = 'ConceptMap.pdf'
# Caption below the figure of the map
caption_pdfmap = 'Concept Map'

# I use the HTML-Parser to catch the xsi:type attributes
# This seems not to work with the XML parser!
d = pq(filename='./ConceptMap.vue', parser='html')


def clean_text(dirty_string):
    """
    First of all cleans line breaks from notes with regex
    :return: String The cleaned text
    """
    regex = re.compile(r'(%nl;)+')
    return regex.sub('\n\n', dirty_string)


def get_linked_nodes(child):
    """
    Build a dictionary with IDs and arrow direction
    for linkes nodes
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
            # put them in the dictionary
            linked_nodes['id' + str(counter)] = d(n).text()
            counter += 1
    return linked_nodes


def get_urlresources_if_any(n):
    """
    Builds a string for the URL resources of a node
    :param n: Node object
    :return: String Formatted string with the URL
    """
    urlresource = d(n).children('resource')
    if urlresource and urlresource.attr('xsi:type') == 'URLResource':
        text = '#### Quelle im Netz ####\n\n'
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
    if int(node_dictionary['arrowstate']) == 0:
        return '### %s --%s-- %s ###\n\n' % (
            get_label_for_linked_node(node_dictionary['id1']),
            get_label_for_link(link),
            get_label_for_linked_node(node_dictionary['id2'])
        )

    if int(node_dictionary['arrowstate']) == 1:
        return '### *%s --%s--> %s* ###\n\n' % (
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
    else:
        return ''


def get_label_for_linked_node(id):
    """
    Reads the label text for a linked node
    :param id: the ID of the linked node
    :return: String
    """
    label = d('#' + id).attr('label')
    return label


def get_label_for_link(l):
    """
    Reads the label text of a node
    :param l: Node object
    :return: String
    """
    return d(l).attr('label')


def get_pdf_of_map():
    """
    Checks if a PDF of the map exists
    :return: Boolean
    """
    if os.path.exists(pdfmap_filename):
        return True
    else:
        return False


def main():
    # Store the generated Markdown here
    file = '# %s #\n\n' % document_headline

    # Open target file
    f = open(markdown_filename, 'w')

    # Get all children of the map
    children = d('child')

    # Iterate over the nodes and links
    for t in children:
        label = d(t).attr('label')
        child_type = d(t).attr('xsi:type')

        # Get all the nodes
        if child_type == 'node':
            notes = d(t).children('notes')
            file += '## %s ##\n\n' % label
            if notes:
                file += d(notes).text() + '\n\n'
            resources = get_urlresources_if_any(t)
            if resources != '':
                file += resources

        # Get all the links
        if child_type == 'link':
            # Get the dictionary with ids and arrow direction
            n_dictionary = get_linked_nodes(t)
            # Get notes of the link
            notes = d(t).children('notes')
            if label:
                file += build_headline_for_links(t, n_dictionary)
            else:
                file += ''
            if notes:
                file += d(notes).text() + '\n\n'
            else:
                file += ''

    if get_pdf_of_map():
        pdf_string = '\n\n![%s](%s)\n\n' % (caption_pdfmap, pdfmap_filename)
        file += pdf_string

    file = clean_text(file)

    f.write(file)
    f.close()
    return 0

if __name__ == '__main__':
    main()

