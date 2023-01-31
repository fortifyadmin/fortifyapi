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
        """
         When retrieving a list of resources it is possible to filter and sort that list using query parameters.
         For example, `/api/v1/projects?q=createdBy:admin&orderby=id` will return the list of projects that were
         created by "admin" sorted by the "id" (by default they're sorted by name).

        The query itself is field name + value pair that filters results, and the Query object helps generate the values.
        The available query parameters are:
        For example:
        ```
        q = Query().query("name", "Unit Test Python")
        for project in client.projects.list(q=q, orderby='id'):
        ```

        :param query_obj: A dict to seed this query
        :type query_obj: dict
        """
        self.__queries = []
        if query_obj:
            for k, v in query_obj.items():
                self.query(k, v)

    def query(self, name, value):
        """
        Add to the query

        :param name: Name
        :param value: Value
        :return: self for chaining
        :rtype: :py:class:`query.Query`
        """
        self.__queries.append(AndCondition(name, value))
        return self

    def generate(self):
        """
        Generate the query string to use with the `q` parameter

        :return: the query string
        :rtype: str
        """
        ret = ''
        if len(self.__queries) > 0:
            ret += str(self.__queries[0])
        if len(self.__queries) > 1:
            for e in self.__queries[1:]:
                ret += f"{e.typ}{e}"
        return ret

    def __str__(self):
        return self.generate()
