from intbase import InterpreterBase, ErrorType

class FieldDefinition:
    def __init__(self, name, initial_value):
        self.name = name
        if initial_value == InterpreterBase.TRUE_DEF:
            self.initial_value = True
        elif initial_value == InterpreterBase.FALSE_DEF:
            self.initial_value = False
        elif initial_value == InterpreterBase.NULL_DEF:
            self.initial_value = None
        elif isinstance(initial_value, str) and (
            initial_value.startswith('"') and initial_value.endswith('"')
        ):
            self.initial_value = initial_value[1:-1]

    def get_name(self):
        return self.name

    def get_initial_value(self):
        return self.initial_value