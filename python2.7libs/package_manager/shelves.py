from lxml import etree


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
    with open(file_path, 'rb') as file:
        xml_data = file.read()
    root = etree.fromstring(xml_data)
    shelves = []
    for data in root.getiterator('tool'):
        data = data.items()
        shelves.append(ShelfItem(label=data[1][1],
                                 name=data[0][1],
                                 icon=data[2][1]))
    return tuple(shelves)
