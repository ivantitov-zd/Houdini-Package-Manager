from __future__ import print_function

from lxml import etree


class PyPanelItem:
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


def interfacesInFile(file_path):
    with open(file_path, 'rb') as file:
        xml_data = file.read()
    panels = []
    try:
        root = etree.fromstring(xml_data)
        for data in root.getiterator('interface'):
            data = data.items()
            panels.append(PyPanelItem(label=data[1][1],
                                      name=data[0][1],
                                      icon=data[2][1]))
    except etree.XMLSyntaxError:
        pass
    return tuple(panels)
