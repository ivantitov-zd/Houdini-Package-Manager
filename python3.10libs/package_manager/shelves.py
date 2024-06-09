# coding: utf-8

from __future__ import print_function

from xml.etree import ElementTree


class ShelfItem(object):
    def __init__(self, label: str, name: str) -> None:
        self.__label = label
        self.__name = name

    def label(self) -> str:
        return self.__label

    def name(self) -> str:
        return self.__name


def shelvesInFile(file_path: str) -> tuple[ShelfItem, ...]:
    shelves = []
    try:
        tree = ElementTree.parse(file_path)
        for elem in tree.getroot().iter('toolshelf'):
            shelves.append(ShelfItem(label=elem.get('label'),
                                     name=elem.get('name')))
    except (IOError, ElementTree.ParseError):
        pass
    return tuple(shelves)


class ShelfToolItem(object):
    def __init__(self, label: str, name: str, icon: str) -> None:
        self.__label = label
        self.__name = name
        self.__icon = icon

    def label(self) -> str:
        return self.__label

    def name(self) -> str:
        return self.__name

    def icon(self) -> str:
        return self.__icon


def toolsInFile(file_path: str) -> tuple[ShelfToolItem, ...]:
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
