from intbase import InterpreterBase, ErrorType

class FieldDefinition:
    def __init__(self, name, initial_value):
        self.name = name
        if initial_value == InterpreterBase.NULL_DEF:
            initial_value = None
        elif initial_value == InterpreterBase.TRUE_DEF:
            initial_value = True
        elif initial_value == InterpreterBase.FALSE_DEF:
            initial_value = False
        elif isinstance(initial_value, str) and (
            initial_value.startswith('"') and initial_value.endswith('"')
        ):
            initial_value = initial_value[1:-1]
        self.initial_value = initial_value

    def get_name(self):
        return self.name

    def get_initial_value(self):
        return self.initial_value