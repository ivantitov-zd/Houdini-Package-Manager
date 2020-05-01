from __future__ import print_function

from xml.etree import ElementTree


class ShelfItem:
    def __init__(self, label, name, icon):
        self.__label = label
        self.__name = name
        self.__icon = icon

    def label(self):
        return self.__label

    def name(self):
        return self.__name

    def icon(self):
        return self.__icon


def definitionsInFile(file_path):
    tools = []
    try:
        tree = ElementTree.parse(file_path)
        for elem in tree.getroot().iter('tool'):
            tools.append(ShelfToolItem(label=elem.get('label'),
                                       name=elem.get('name'),
                                       icon=elem.get('icon')))
    except (IOError, ElementTree.ParseError):
        pass
    return tuple(tools)
