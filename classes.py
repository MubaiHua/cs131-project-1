from intbase import InterpreterBase, ErrorType
from fields import FieldDefinition
from method import MethodDefinition
from object import ObjectDefinition

class ClassDefinition:
    def __init__(self, name, class_decleration, interpreter_obj):
        self.name = name
        self.methods = {}
        self.fields = {}
        self.interpreter_obj = interpreter_obj
        self.initiate_class(class_decleration)

    def get_methods(self):
        return self.methods

    def get_fields(self):
        return self.fields

    def initiate_class(self, class_declaration):
        has_main_func = False  # check whether a main method exist in class Main

        for item in class_declaration:
            if item[0] == InterpreterBase.FIELD_DEF:
                field_name = item[1]
                if field_name in self.fields:
                    self.interpreter_obj.error(
                        ErrorType.NAME_ERROR,
                        f"Field name {field_name} already exist in class {self.name}",
                    )  # check for duplicate field name
                initial_value = item[2]
                self.fields[field_name] = FieldDefinition(field_name, initial_value)

            elif item[0] == InterpreterBase.METHOD_DEF:
                method_name = item[1]
                if method_name == InterpreterBase.MAIN_FUNC_DEF:
                    has_main_func = True
                if method_name in self.methods:
                    self.interpreter_obj.error(
                        ErrorType.NAME_ERROR,
                        f"Method name {method_name} already exist in class {self.name}",
                    )  # check for duplicate method name
                parameters = item[2]
                statements = item[3]
                self.methods[method_name] = MethodDefinition(
                    method_name, parameters, statements
                )

        if self.name == InterpreterBase.MAIN_CLASS_DEF and not has_main_func:
            self.interpreter_obj.error(
                ErrorType.SYNTAX_ERROR, "Main Class must have a main method"
            )

    def instantiate_object(self):
        return ObjectDefinition(self.interpreter_obj, self.methods, self.fields)
