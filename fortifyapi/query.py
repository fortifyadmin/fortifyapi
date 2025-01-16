class Condition:
    def __init__(self, typ, name, value):
        self.typ = typ
        self.name = name
        self.value = value

    def __str__(self):
        if isinstance(self.value, str):
            return f"{self.name}:\"{self.value}\""
        return f"{self.name}:{self.value}"


class AddCondition(Condition):
    def __init__(self, name, value):
        super().__init__(',', name, value)


class AndCondition(Condition):
    def __init__(self, name, value):
        super().__init__('+and+', name, value)


class OrCondition(Condition):
    def __init__(self, name, value):
        super().__init__('+or+', name, value)


class Query:

    def __init__(self, query_obj=None):
        """
        Query object for Fortify API.

        Examples:
            ?q=key:"value"
            q=Query().query('key', 'value')

            ?q=key:"value"+or+key:"value2"
            q=Query().query('key', 'value').or_query('key', 'value2')

            ?q=key:"val*"+and+key:"*ue"
            q=Query().query('key', 'val*').and_query('key', '*ue')

            ?q=key:"value1",otherkey:"othervalue"
            q=Query().query('key', 'value1').query('otherkey', 'othervalue')

        """

        self.__queries = []
        if query_obj:
            for k, v in query_obj.items():
                self.query(k, v)

    def query(self, name, value):
        self.__queries.append(AddCondition(name, value))
        return self

    def and_query(self, name, value):
        self.__queries.append(AndCondition(name, value))
        return self

    def or_query(self, name, value):
        self.__queries.append(OrCondition(name, value))
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
