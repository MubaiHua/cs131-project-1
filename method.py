class MethodDefinition:
    def __init__(self, name, parameters, statements):
        self.name = name
        self.parameters = parameters
        self.statements = statements

    def get_top_level_statement(self):
        return self.statements

    def get_name(self):
        return self.name

    def get_parameters(self):
        return self.parameters