#!python3
# -*- coding: utf-8 -*-
r"""
Definitions which were not found in CKAN
"""

from enum import IntEnum


class CkanCapacity(IntEnum):
    Member = 3
    Editor = 4  # only for collaborators of a package
    Admin = 6   # only for members of a group

    def __str__(self):
        return self.name.lower()

    @staticmethod
    def from_str(s):
        s = s.lower().strip()
        if s == "member":
            return CkanCapacity.Member
        elif s == "editor":
            return CkanCapacity.Editor
        elif s == "admin":
            return CkanCapacity.Admin
        else:
            raise ValueError(s)
