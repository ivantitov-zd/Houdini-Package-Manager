from typing import Union


class Token(object):
    def __new__(cls, source) -> 'Token':
        if isinstance(source, Token):
            return source
        else:
            return super(Token, cls).__new__(cls)

    def __init__(self, source: str) -> None:
        if isinstance(source, Token):
            return

        self.__raw = source
        if source.isdigit():
            self.__value = int(source)
        else:  # source.isalpha()
            self.__value = str(source).strip().lower()

    @property
    def raw(self) -> str:
        return self.__raw

    @property
    def value(self) -> str | int:
        return self.__value

    def __repr__(self) -> str:
        return 'Token("{0}")'.format(self.raw)

    def __str__(self) -> str:
        return self.__raw

    def __eq__(self, other: Union['Token', int, str]) -> bool:
        if isinstance(other, Token) and isinstance(other.value, int):
            return self.value == other.value
        elif isinstance(other, int) and isinstance(self.value, int):
            return self.value == other
        elif isinstance(self.value, str):
            if isinstance(other, Token) and isinstance(other.value, str) \
                    or isinstance(other, str):
                other = Token(other)
                return self.value == other.value
        return NotImplemented

    def __ne__(self, other: Union['Token', int, str]) -> bool:
        if isinstance(other, Token) and isinstance(other.value, int):
            return self.value != other.value
        elif isinstance(self.value, int) and isinstance(other, int):
            return self.value != other
        elif isinstance(self.value, str):
            if isinstance(other, Token) and isinstance(other.value, str) \
                    or isinstance(other, str):
                other = Token(other)
                return self.value != other.value
        return NotImplemented

    def __lt__(self, other: Union['Token', int, str]) -> bool:
        if isinstance(other, Token) and isinstance(other.value, int):
            return self.value < other.value
        elif isinstance(self.value, int) and isinstance(other, int):
            return self.value < other
        elif isinstance(self.value, str):
            if isinstance(other, Token) and isinstance(other.value, str) \
                    or isinstance(other, str):
                other = Token(other)
                self_len = len(self.value)
                other_len = len(other.value)
                for i in range(min(self_len, other_len)):
                    self_char = self.value[i]
                    other_char = other.value[i]
                    if self_char < other_char:
                        return True
                return False
        return NotImplemented

    def __gt__(self, other: Union['Token', int, str]) -> bool:
        if isinstance(other, Token) and isinstance(other.value, int):
            return self.value > other.value
        elif isinstance(self.value, int) and isinstance(other, int):
            return self.value > other
        elif isinstance(self.value, str):
            if isinstance(other, Token) and isinstance(other.value, str) \
                    or isinstance(other, str):
                other = Token(other)
                self_len = len(self.value)
                other_len = len(other.value)
                for i in range(min(self_len, other_len)):
                    self_char = self.value[i]
                    other_char = other.value[i]
                    if self_char > other_char:
                        return True
                return False
        return NotImplemented


def parseVersion(version_string: str) -> tuple[tuple[Token, ...], tuple[Token, ...], str]:
    """Returns ((<number_tokens>), (<qualifier_tokens>), <build_metadata>)"""
    # Find end of the redundant characters at the beginning
    start_index = -1
    for index, char in enumerate(version_string):
        if char.isdigit():
            start_index = index
            break

    if start_index == -1:
        return
    # Cut redundant characters at the beginning
    version_string = version_string[start_index:]

    # Get build metadata substring and cut it
    try:
        plus_index = version_string.index('+')
        build_metadata = version_string[plus_index + 1:].strip()
        version_string = version_string[:plus_index]
    except ValueError:
        build_metadata = ''

    # Get qualifier substring and cut it
    try:
        hyphen_index = version_string.index('-')
        qualifier_string = version_string[hyphen_index + 1:]
        version_string = version_string[:hyphen_index]
    except ValueError:
        qualifier_string = ''

    num_tokens = []
    buffer = ''
    for char in version_string:
        if char.isdigit():
            buffer += char
        else:
            num_tokens.append(Token(buffer))
            buffer = ''
    if buffer:
        num_tokens.append(Token(buffer))

    qualifier_tokens = []
    if qualifier_string:
        buffer = ''
        for char in qualifier_string:
            if char.isalpha() or char.isdigit():
                buffer += char
            else:
                qualifier_tokens.append(Token(buffer))
                buffer = ''
        if buffer:
            qualifier_tokens.append(Token(buffer))

    return tuple(num_tokens), tuple(qualifier_tokens), build_metadata


class Version(object):
    def __new__(cls, source: Union['Version', str]) -> 'Version':
        if isinstance(source, Version):
            return source
        else:
            return super(Version, cls).__new__(cls)

    def __init__(self, source: Union['Version', str]) -> None:
        if isinstance(source, Version):
            return

        self.__raw = source
        self.__num_tokens, self.__qualifier_tokens, _ = parseVersion(source)
        first_nonzero_index = -1
        for index, token in enumerate(reversed(self.__num_tokens), 0):
            if token != 0:
                first_nonzero_index = index
                break
        if first_nonzero_index > 0:
            self.__num_tokens = self.__num_tokens[:-first_nonzero_index]

    @property
    def raw(self) -> str:
        return self.__raw

    @property
    def num_tokens(self) -> tuple[Token, ...]:
        return self.__num_tokens

    @property
    def qualifier_tokens(self) -> tuple[Token, ...]:
        return self.__qualifier_tokens

    def __repr__(self) -> str:
        return 'Version("{0}")'.format(self.__raw)

    def __str__(self) -> str:
        return self.__raw

    def __eq__(self, other) -> bool:
        if isinstance(other, (str, Version)):
            other = Version(other)
            return self.num_tokens == other.num_tokens and \
                self.qualifier_tokens == other.qualifier_tokens
        else:
            return NotImplemented

    def __ne__(self, other) -> bool:
        other = Version(other)
        return self.num_tokens != other.num_tokens or \
            self.qualifier_tokens != other.qualifier_tokens

    def __lt__(self, other) -> bool:
        other = Version(other)
        self_len = len(self.__num_tokens)
        other_len = len(other.num_tokens)
        other_tokens = other.num_tokens
        if self == other:
            return False
        for i in range(min(self_len, other_len)):
            self_value = self.__num_tokens[i]
            other_value = other_tokens[i]
            if self_value == other_value:
                continue
            elif self_value < other_value:
                return True
            elif self_value > other_value:
                return False
        if self_len < other_len:
            return True
        elif self_len > other_len:
            return False

        self_len = len(self.__qualifier_tokens)
        other_len = len(other.qualifier_tokens)
        other_tokens = other.qualifier_tokens
        if self_len > other_len:
            return True
        elif self_len < other_len:
            return False
        for i in range(min(self_len, other_len)):
            self_value = self.__qualifier_tokens[i]
            other_value = other_tokens[i]
            if self_value == other_value:
                continue
            elif self_value < other_value:
                return True
        return False

    def __gt__(self, other) -> bool:
        other = Version(other)
        self_len = len(self.__num_tokens)
        other_len = len(other.num_tokens)
        other_tokens = other.num_tokens
        if self == other:
            return False
        for i in range(min(self_len, other_len)):
            self_value = self.__num_tokens[i]
            other_value = other_tokens[i]
            if self_value == other_value:
                continue
            elif self_value > other_value:
                return True
            elif self_value < other_value:
                return False
        if self_len > other_len:
            return True
        elif self_len < other_len:
            return False

        self_len = len(self.__qualifier_tokens)
        other_len = len(other.qualifier_tokens)
        other_tokens = other.qualifier_tokens
        if self_len < other_len:
            return True
        elif self_len > other_len:
            return False
        for i in range(min(self_len, other_len)):
            self_value = self.__qualifier_tokens[i]
            other_value = other_tokens[i]
            if self_value == other_value:
                continue
            elif self_value > other_value:
                return True
        return False

    def __le__(self, other):
        other = Version(other)
        return self == other or self < other

    def __ge__(self, other):
        other = Version(other)
        return self == other or self > other


class VersionRange(object):
    def __init__(self, low_version: Version | None = None, high_version: Version | None = None) -> None:
        if low_version is None:
            self.low_version = Version('0')
        else:
            self.low_version = low_version

        if high_version is None:
            self.high_version = Version('9999')
        else:
            self.high_version = high_version

    @classmethod
    def fromPattern(cls, pattern: str) -> 'VersionRange':
        pattern = pattern.strip()
        if pattern == '*':
            low_version = Version('0')
            high_version = Version('999999')
        elif len(pattern) > 1 and pattern.endswith('+'):
            low_version = Version(pattern[:-1])
            high_version = Version('999999')
        elif len(pattern) > 1 and pattern.endswith('-'):
            low_version = Version('0')
            high_version = Version(pattern[:-1])
        elif len(pattern) > 3 and pattern.count('-') == 1:
            low_version, high_version = pattern.split('-')
        else:
            raise ValueError('Invalid version range pattern')
        return cls(low_version, high_version)

    def __str__(self) -> str:
        return 'Version Range [{0};{1}]'.format(self.low_version, self.high_version)

    def __repr__(self) -> str:
        return 'VersionRange({0}, {1})'.format(self.low_version.__repr__(),
                                               self.high_version.__repr__())

    def __contains__(self, item: Union[str, Version, 'VersionRange']) -> bool:
        if isinstance(item, (str, Version)):
            version = Version(item)
            return self.low_version <= version <= self.high_version
        elif isinstance(item, VersionRange):
            pass

    def __eq__(self, other) -> bool:
        if isinstance(other, Version):
            return other in self
        elif isinstance(other, VersionRange):
            pass
        else:
            raise TypeError


class VersionPattern(object):
    def __init__(self, pattern: str) -> None:
        self.__raw = str(pattern)

        self.__include = []
        self.__exclude = []

        for token in pattern.split():
            if len(token) > 1 and token.startswith('^'):
                self.__exclude.append(VersionRange.fromPattern(token[1:]))
            else:
                self.__include.append(VersionRange.fromPattern(token))

    @property
    def raw(self) -> str:
        return self.__raw

    def __contains__(self, item: Union[str, Version, VersionRange, 'VersionPattern']) -> bool:
        if isinstance(item, (str, Version)):
            version = Version(item)
            return version in self.__include and \
                version not in self.__exclude
        elif isinstance(item, VersionRange):
            pass
        elif isinstance(item, VersionPattern):
            pass

    def __eq__(self, other: Union[str, Version, VersionRange, 'VersionPattern']) -> bool:
        if isinstance(other, Version):
            return other in self
        elif isinstance(other, VersionPattern):
            pass
        else:
            raise TypeError


if False:
    assert Version('2.7') < '3.3'
    assert Version('3.3.0') == '3.3'
    assert Version('6') < Version('10')
    assert '10.2.305' in VersionRange.fromPattern('6-10.3')
    assert '18.5' in VersionPattern('18+')
    assert '17' not in VersionPattern('18+')
    assert Version('0.3-beta') == Version('0.3.0-beta')
    assert Version('0.4-beta') > Version('0.4-alpha')
    assert Version('0.4-beta.alpha') < Version('0.4-alpha')
    print('All ok')
