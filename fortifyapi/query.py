class Condition:
    def __init__(self, typ, name, value):
        self.typ = typ
        self.name = name
        self.value = value

    def __str__(self):
        if isinstance(self.value, str):
            return f"{self.name}:\"{self.value}\""
        return f"{self.name}:{self.value}"


class AndCondition(Condition):
    def __init__(self, name, value):
        super().__init__(',', name, value)


class Query:

    def __init__(self, query_obj=None):
        self.__queries = []
        if query_obj:
            for k, v in query_obj.items():
                self.query(k, v)

    def query(self, name, value):
        self.__queries.append(AndCondition(name, value))
        return self

    def generate(self):
        ret = ''
        if len(self.__queries) > 0:
            ret += str(self.__queries[0])
        if len(self.__queries) > 1:
            for e in self.__queries[1:]:
                ret += f"{e.typ}{e}"
        return ret

    def __str__(self):
        return self.generate()
