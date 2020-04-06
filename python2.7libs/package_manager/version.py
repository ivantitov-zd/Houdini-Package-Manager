import re


class Token:
    pass


class Version:
    def __new__(cls, *args, **kwargs):
        if isinstance(args[0], Version):
            return args[0]
        return super(Version, cls).__new__(cls)

    def __init__(self, source):
        self.__raw = str(source)
        self.__tokens = tuple(map(lambda pair: int(pair[1]), re.findall(r'(^\D)?(\d+)', self.__raw)))  # |\w+
        first_nonzero_index = -1
        for index, token in enumerate(reversed(self.__tokens), 0):
            if token != 0:
                first_nonzero_index = index
                break
        if first_nonzero_index > 0:
            self.__tokens = self.__tokens[:-first_nonzero_index]

    @property
    def raw(self):
        return self.__raw

    @property
    def tokens(self):
        return self.__tokens

    def __repr__(self):
        return 'Version("{}")'.format(self.__raw)

    def __str__(self):
        return self.__raw

    def __eq__(self, other):
        if isinstance(other, (str, Version)):
            other = Version(other)
            return self.tokens == other.tokens
        else:
            return NotImplemented

    def __ne__(self, other):
        other = Version(other)
        return self.tokens != other.tokens

    def __lt__(self, other):
        other = Version(other)
        self_len = len(self.__tokens)
        other_len = len(other.tokens)
        other_tokens = other.tokens
        if self == other:
            return False
        for i in range(min(self_len, other_len)):
            self_value = self.__tokens[i]
            other_value = other_tokens[i]
            if self_value == other_value:
                continue
            elif self_value < other_value:
                return True
            elif self_value > other_value:
                return False
        if self_len < other_len:
            return True
        else:
            return False

    def __gt__(self, other):
        other = Version(other)
        self_len = len(self.__tokens)
        other_len = len(other.tokens)
        other_tokens = other.tokens
        if self == other:
            return False
        for i in range(min(self_len, other_len)):
            self_value = self.__tokens[i]
            other_value = other_tokens[i]
            if self_value == other_value:
                continue
            elif self_value > other_value:
                return True
            elif self_value < other_value:
                return False
        if self_len > other_len:
            return True
        else:
            return False

    def __le__(self, other):
        other = Version(other)
        return self == other or self < other

    def __ge__(self, other):
        other = Version(other)
        return self == other or self > other

    def increment(self, component):
        pass

    def __add__(self, other):
        pass

    def __iadd__(self, other):
        pass


class VersionRange:
    def __init__(self, low_version=None, high_version=None):
        if low_version is None:
            self.low_version = Version('0')
        else:
            self.low_version = low_version

        if high_version is None:
            self.high_version = Version('9999')
        else:
            self.high_version = high_version

    @classmethod
    def fromPattern(cls, pattern):
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

    def __str__(self):
        return 'Version Range [{0};{1}]'.format(self.low_version, self.high_version)

    def __repr__(self):
        return 'VersionRange({0}, {1})'.format(self.low_version.__repr__(),
                                               self.high_version.__repr__())

    def __contains__(self, item):
        if isinstance(item, (str, Version)):
            version = Version(item)
            return self.low_version <= version <= self.high_version
        elif isinstance(item, VersionRange):
            pass

    def __eq__(self, other):
        if isinstance(other, Version):
            return other in self
        elif isinstance(other, VersionRange):
            pass
        else:
            raise TypeError


class VersionPattern:
    def __init__(self, pattern):
        self.__include = []
        self.__exclude = []

        for token in pattern.split():
            if len(token) > 1 and token.startswith('^'):
                self.__exclude.append(VersionRange.fromPattern(token[1:]))
            else:
                self.__include.append(VersionRange.fromPattern(token))

    def __contains__(self, item):
        if isinstance(item, (str, Version)):
            version = Version(item)
            return version in self.__include and \
                   version not in self.__exclude
        elif isinstance(item, VersionRange):
            pass
        elif isinstance(item, VersionPattern):
            pass

    def __eq__(self, other):
        if isinstance(other, Version):
            return other in self
        elif isinstance(other, VersionPattern):
            pass
        else:
            raise TypeError


if __name__ == '__main__':
    assert Version('2.7') < '3.3'
    assert Version('3.3.0') == '3.3'
    assert Version('6') < Version('10')
    assert '10.2.305' in VersionRange.fromPattern('6-10.3')
    assert '18.5' in VersionPattern('18+')
