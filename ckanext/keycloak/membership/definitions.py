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

    @staticmethod
    def from_str(s):
        s = s.lower().strip()
        if s == "member":
            return CkanCapacityExtended.Member
        elif s == "editor":
            return CkanCapacityExtended.Editor
        elif s == "admin":
            return CkanCapacityExtended.Admin
        elif s == "dataset":
            return CkanCapacityExtended.Dataset
        else:
            raise ValueError(s)


class DatasetCollaborationCleanupMode(IntEnum):
    Disabled = 0
    Restricted = 1
    Complete = 2

    def __str__(self):
        return self.name.lower()

    @staticmethod
    def from_str(s):
        s = s.lower().strip()
        if s == "disabled":
            return DatasetCollaborationCleanupMode.Disabled
        elif s == "restricted":
            return DatasetCollaborationCleanupMode.Restricted
        elif s == "complete":
            return DatasetCollaborationCleanupMode.Complete
        else:
            raise ValueError(s)

