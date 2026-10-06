#!python3
# -*- coding: utf-8 -*-
r"""
Definitions
"""

from enum import IntEnum


class CkanCapacityExtended(IntEnum):
    Dataset = 2
    Member = 3
    Editor = 4
    Admin = 6

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, s):
        if isinstance(s, cls):
            return s
        if s is None:
            return None
        s = str(s).lower().strip()
        if s == "member":
            return cls.Member
        elif s == "editor":
            return cls.Editor
        elif s == "admin":
            return cls.Admin
        elif s == "dataset":
            return cls.Dataset
        else:
            raise ValueError(f"Unknown capacity: {s}")

    def __lt__(self, other):
        if isinstance(other, str):
            try:
                other = self.from_str(other)
            except ValueError:
                return NotImplemented
        return super().__lt__(other)

    def __le__(self, other):
        if isinstance(other, str):
            try:
                other = self.from_str(other)
            except ValueError:
                return NotImplemented
        return super().__le__(other)

    def __gt__(self, other):
        if isinstance(other, str):
            try:
                other = self.from_str(other)
            except ValueError:
                return NotImplemented
        return super().__gt__(other)

    def __ge__(self, other):
        if isinstance(other, str):
            try:
                other = self.from_str(other)
            except ValueError:
                return NotImplemented
        return super().__ge__(other)

    def __eq__(self, other):
        if isinstance(other, str):
            try:
                other = self.from_str(other)
            except ValueError:
                return False
        return super().__eq__(other)


class DatasetCollaborationCleanupMode(IntEnum):
    Disabled = 0
    Restricted = 1
    Complete = 2

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, s):
        if isinstance(s, cls):
            return s
        s = str(s).lower().strip()
        if s == "disabled":
            return cls.Disabled
        elif s == "restricted":
            return cls.Restricted
        elif s == "complete":
            return cls.Complete
        else:
            raise ValueError(f"Unknown cleanup mode: {s}")

