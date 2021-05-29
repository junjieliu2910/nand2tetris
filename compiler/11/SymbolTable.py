from enum import Enum


class Kind(Enum):
    NONE = 0
    STATIC = 1
    FIELD = 2
    ARG = 3
    VAR = 4


class SymbolTable:
    """
    For each class, build a specific symbol table for fields at class scope
    And for each class method, build a corresponding subroutine symbol table
    Use dict to represent symbol table
    """
    def __init__(self):
        """
        Stored as {"identifier_name": ["type_name", kind, index]}
        """
        self.class_table = {}
        self.subroutine_table = {}
        self.var_count = {
            Kind.STATIC: 0,
            Kind.FIELD: 0,
            Kind.ARG: 0,
            Kind.VAR: 0
        }

    def startSubroutine(self):
        self.subroutine_table.clear()
        self.var_count[Kind.ARG] = 0
        self.var_count[Kind.VAR] = 0

    def define(self, name, s_type, kind):
        """
        Static or field variable has class scope
        Arg and var variable has subroutine scope
        name: string
        s_type: string
        kind: kind
        """
        if kind in (Kind.STATIC, Kind.FIELD):
            self.class_table[name] = [s_type, kind, self.var_count[kind]]
            self.var_count[kind] += 1
        elif kind in (Kind.VAR, kind.ARG):
            self.subroutine_table[name] = [s_type, kind, self.var_count[kind]]
            self.var_count[kind] += 1

    def nameExist(self, name):
        if name in self.subroutine_table:
            return True
        if name in self.class_table:
            return True
        return False

    def getEntry(self, name):
        if name in self.subroutine_table:
            return self.subroutine_table[name]
        if name in self.class_table:
            return self.class_table[name]
        return None

    def varCount(self, kind):
        return self.var_count[kind]

    def kindOf(self, name):
        kind = Kind.NONE
        if name in self.class_table:
            _, kind, _ = self.class_table[name]
        if name in self.subroutine_table:
            _, kind, _ = self.subroutine_table[name]
        return kind

    def typeOf(self, name):
        c_type = ""
        if name in self.class_table:
            c_type, _, _ = self.class_table[name]
        if name in self.subroutine_table:
            c_type, _, _ = self.subroutine_table[name]
        return c_type

    def indexOf(self, name):
        index = -1
        if name in self.class_table:
            _, _, index = self.class_table[name]
        if name in self.subroutine_table:
            _, _, index = self.subroutine_table[name]
        return index
