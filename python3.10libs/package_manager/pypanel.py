from xml.etree import ElementTree


class PyPanelItem:
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


def interfaces_in_file(file_path: str) -> tuple[PyPanelItem, ...]:
    panels = []
    try:
        tree = ElementTree.parse(file_path)
        for elem in tree.getroot().iter('interface'):
            panels.append(PyPanelItem(label=elem.get('label'),
                                      name=elem.get('name'),
                                      icon=elem.get('icon')))
    except (OSError, ElementTree.ParseError):
        pass
    return tuple(panels)
