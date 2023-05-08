from intbase import InterpreterBase, ErrorType
from copy import deepcopy
class ObjectDefinition:
    NO_RETURN_VALUE = "N_R_V"

    def __init__(self, interpreter_obj, methods, fields):
        self.fields = {}
        self.methods = {}


        for method in methods.values():
            self.methods[method.get_name()] = deepcopy(method)
        for field in fields.values():
            self.fields[field.get_name()] = field.get_initial_value()

        self.interpreter_obj = interpreter_obj

    def create_object(self, class_name):
        if class_name not in self.interpreter_obj.get_classes():
            self.interpreter_obj.error(
                ErrorType.TYPE_ERROR, f"Class named {class_name} does not exist"
            )

        class_def = self.interpreter_obj.get_classes()[class_name]
        obj = class_def.instantiate_object()
        return obj

    def call_method(self, method_name, evaluated_args):
        if method_name not in self.methods:
            self.interpreter_obj.error(
                ErrorType.NAME_ERROR, f"Method {method_name} does not exist"
            )

        method = self.methods[method_name]

        if len(evaluated_args) != len(method.parameters):
            self.interpreter_obj.error(
                ErrorType.TYPE_ERROR,
                f"Method {method_name} expected {len(method.parameters)} parameters, but gets only {len(evaluated_args)}",
            )

        # Create a dictionary of param_name: param_value pair
        parameter_values = {
            param_name: param_value
            for param_name, param_value in zip(method.get_parameters(), evaluated_args)
        }

        # Execute the top-level statement
        statement = method.get_top_level_statement()
        result = self.execute_statement(statement, parameter_values)
        if result == self.NO_RETURN_VALUE:
            return
        return result

    def execute_statement(self, statement, parameter_values=None):
        if parameter_values is None:
            parameter_values = {}

        if self.is_print_statement(statement):
            result = self.execute_print(statement, parameter_values)
        elif self.is_set_statement(statement):
            result = self.execute_set_statement(statement, parameter_values)
        elif self.is_input_statement(statement):
            result = self.execute_input_statement(statement, parameter_values)
        elif self.is_call_statement(statement):
            result = self.execute_call_statement(statement, parameter_values)
        elif self.is_while_statement(statement):
            result = self.execute_while_statement(statement, parameter_values)
        elif self.is_if_statement(statement):
            result = self.execute_if_statement(statement, parameter_values)
        elif self.is_return_statement(statement):
            result = self.execute_return_statement(statement, parameter_values)
        elif self.is_begin_statement(statement):
            result = self.execute_all_nested_statements(statement, parameter_values)
        else:
            result = None
        return result

    def is_print_statement(self, statement):
        return (
            isinstance(statement, list)
            and len(statement) != 0
            and statement[0] == InterpreterBase.PRINT_DEF
        )

    def execute_print(self, statement, parameter_values):
        keyword = statement[0]
        expression = statement[1:]
        value = self.evaluate_expression(expression, parameter_values, keyword)
        if isinstance(value, bool):
            value = InterpreterBase.TRUE_DEF if value == True else InterpreterBase.FALSE_DEF
        self.interpreter_obj.output(str(value))

    def is_set_statement(self, statement):
        return (
            isinstance(statement, list)
            and len(statement) != 0
            and statement[0] == InterpreterBase.SET_DEF
        )

    def execute_set_statement(self, statement, parameter_values=None):
        if parameter_values is None:
            parameter_values = {}

        variable_name = statement[1]

        expression = statement[2]
        value = self.evaluate_expression(expression, parameter_values)

        self.set_variable_value(value, variable_name, parameter_values)

    def is_input_statement(self, statement):
        return (
            isinstance(statement, list)
            and len(statement) != 0
            and (
                statement[0] == InterpreterBase.INPUT_STRING_DEF
                or statement[0] == InterpreterBase.INPUT_INT_DEF
            )
        )

    def execute_input_statement(self, statement, parameter_values):
        input_value = self.interpreter_obj.get_input()
        self.set_variable_value(input_value, statement[1], parameter_values)

    def is_call_statement(self, statement):
        return (
            isinstance(statement, list)
            and len(statement) != 0
            and statement[0] == InterpreterBase.CALL_DEF
        )

    def execute_call_statement(self, statement, parameter_values):
        object_name = statement[1]
        if isinstance(object_name, list):
            object_name = self.evaluate_expression(object_name, parameter_values)

        function_name = statement[2] 
        args = statement[3:]
        evaluated_args = [
            self.evaluate_expression(arg, parameter_values) for arg in args
        ]

        # Calling the method with the evaluated arguments
        if object_name == InterpreterBase.ME_DEF:
            return self.call_method(function_name, evaluated_args)
        elif object_name in self.fields:
            if self.fields[object_name] is None:
                self.interpreter_obj.error(
                    ErrorType.FAULT_ERROR, f"{object_name} is a null object reference"
                )
            return self.fields[object_name].call_method(function_name, evaluated_args)
        elif object_name in parameter_values:
            if parameter_values[object_name] is None:
                self.interpreter_obj.error(
                    ErrorType.FAULT_ERROR, f"{object_name} is a null object reference"
                )
            return parameter_values[object_name].call_method(function_name, evaluated_args)
        else:
            object_name.call_method(function_name, evaluated_args)

    def is_while_statement(self, statement):
        return (
            isinstance(statement, list)
            and len(statement) > 0
            and statement[0] == InterpreterBase.WHILE_DEF
        )

    def execute_while_statement(self, statement, parameter_values):
        condition = statement[1]
        body = statement[2]

        result = self.evaluate_expression(condition, parameter_values)

        if not isinstance(result, bool):
            self.interpreter_obj.error(
                ErrorType.TYPE_ERROR,
                f"The condition in the while statement must be a boolean",
            )

        while self.evaluate_expression(condition, parameter_values):
            result = self.execute_statement(body, parameter_values)
            if result is not None:
                return result

    def is_if_statement(self, statement):
        return (
            isinstance(statement, list)
            and len(statement) != 0
            and statement[0] == InterpreterBase.IF_DEF
        )

    def execute_if_statement(self, statement, parameter_values):
        if len(statement) < 3:  # verify the syntax of if statement
            self.interpreter_obj.error(ErrorType.SYNTAX_ERROR)

        condition = statement[1]
        result = self.evaluate_expression(condition, parameter_values)

        if not isinstance(result, bool):
            self.interpreter_obj.error(
                ErrorType.TYPE_ERROR,
                f"The condition in the if statement must be a boolean",
            )

        if result == True:
            return self.execute_statement(
                statement[2], parameter_values
            )  # execute true statements
        elif len(statement) > 3:
            return self.execute_statement(
                statement[3], parameter_values
            )  # execute false statements if exists
        else:
            return

    def is_return_statement(self, statement):
        return (
            isinstance(statement, list)
            and len(statement) > 0
            and statement[0] == InterpreterBase.RETURN_DEF
        )

    def execute_return_statement(self, statement, parameter_values):
        if len(statement) == 1:
            return self.NO_RETURN_VALUE
        return self.evaluate_expression(statement[1], parameter_values)

    def is_begin_statement(self, statement):
        return (
            isinstance(statement, list)
            and len(statement) > 0
            and statement[0] == InterpreterBase.BEGIN_DEF
        )

    def execute_all_nested_statements(self, statements, parameter_values):
        if parameter_values is None:
            parameter_values = {}

        for statement in statements[1:]:
            result = self.execute_statement(statement, parameter_values)
            if result is not None:
                return result

    def evaluate_expression(self, expression, parameter_values, keyword = None):
        if isinstance(expression, str):
            if expression.startswith('"') and expression.endswith('"'):  # String literal
                return expression[1:-1]
            elif expression.isdigit():  # Integer literal
                return int(expression)
            elif isinstance(expression, bool):
                return expression
            elif expression == InterpreterBase.NULL_DEF:
                return None
            elif expression == InterpreterBase.TRUE_DEF:  # Boolean true literal
                return True
            elif expression == InterpreterBase.FALSE_DEF:  # Boolean false literal
                return False
            else:  # Assume the expression is a variable name
                return self.get_variable_value(expression, parameter_values)

        elif isinstance(expression, list):
            operator = expression[0]
            operands = expression[1:]

            if operator == InterpreterBase.NEW_DEF:
                class_name = expression[1]
                if class_name not in self.interpreter_obj.classes:
                    self.interpreter_obj.error(
                        ErrorType.TYPE_ERROR, f"class {class_name} does not exist"
                    )
                new_object = self.create_object(class_name)
                return new_object

            if isinstance(expression, list):
                statement_result = self.execute_statement(expression, parameter_values)
                if statement_result != None:
                    return statement_result

            if isinstance(expression[0], list):
                statement_result = self.evaluate_expression(
                    expression[0], parameter_values
                )
                if statement_result != None:
                    return statement_result

            if operator in ["+", "-", "*", "/", "%"]:
                left_operand = self.evaluate_expression(operands[0], parameter_values)
                right_operand = self.evaluate_expression(operands[1], parameter_values)

                if isinstance(left_operand, str) and left_operand.isdigit():
                    left_operand = int(left_operand)

                if isinstance(right_operand, str) and right_operand.isdigit():
                    right_operand = int(right_operand)

                if type(left_operand) == int and type(right_operand) == int:
                    if operator == "+":
                        return left_operand + right_operand
                    elif operator == "-":
                        return left_operand - right_operand
                    elif operator == "*":
                        return left_operand * right_operand
                    elif operator == "/":
                        return left_operand // right_operand
                    elif operator == "%":
                        return left_operand % right_operand
                elif isinstance(left_operand, str) and isinstance(right_operand, str):
                    if operator == "+":
                        return left_operand + right_operand
                    else:
                        self.interpreter_obj.error(
                            ErrorType.TYPE_ERROR,
                            f"Can't use operator {operator} with value {left_operand} and {right_operand}",
                        )
                else:
                    self.interpreter_obj.error(
                        ErrorType.TYPE_ERROR,
                        f"Can't use operator {operator} with value {left_operand} and {right_operand}",
                    )

            elif operator in ["<", ">", "<=", ">=", "!=", "==", "&", "|"]:
                left_operand = self.evaluate_expression(operands[0], parameter_values)
                right_operand = self.evaluate_expression(operands[1], parameter_values)

                if isinstance(left_operand, str) and left_operand.isdigit():
                    left_operand = int(left_operand)

                if isinstance(right_operand, str) and right_operand.isdigit():
                    right_operand = int(right_operand)

                if isinstance(left_operand, int) != isinstance(right_operand, int):
                    self.interpreter_obj.error(
                        ErrorType.TYPE_ERROR,
                        f"Can't use operator {operator} with value {left_operand} and {right_operand}",
                    )

                if operator == "<":
                    if isinstance(left_operand, bool) or isinstance(
                        right_operand, bool
                    ):
                        self.interpreter_obj.error(
                            ErrorType.TYPE_ERROR,
                            f"Can't use operator {operator} with value {left_operand} and {right_operand}",
                        )
                    return left_operand < right_operand
                elif operator == ">":
                    if isinstance(left_operand, bool) or isinstance(
                        right_operand, bool
                    ):
                        self.interpreter_obj.error(
                            ErrorType.TYPE_ERROR,
                            f"Can't use operator {operator} with value {left_operand} and {right_operand}",
                        )
                    return left_operand > right_operand
                elif operator == "<=":
                    if isinstance(left_operand, bool) or isinstance(
                        right_operand, bool
                    ):
                        self.interpreter_obj.error(
                            ErrorType.TYPE_ERROR,
                            f"Can't use operator {operator} with value {left_operand} and {right_operand}",
                        )
                    return left_operand <= right_operand
                elif operator == ">=":
                    if isinstance(left_operand, bool) or isinstance(
                        right_operand, bool
                    ):
                        self.interpreter_obj.error(
                            ErrorType.TYPE_ERROR,
                            f"Can't use operator {operator} with value {left_operand} and {right_operand}",
                        )
                    return left_operand >= right_operand
                elif operator == "!=":
                    raise_error = False
                    if isinstance(left_operand, (int, bool, str)):
                        if not isinstance(right_operand, (int, bool, str)):
                            raise_error = True
                        if type(left_operand) != type(right_operand):
                            raise_error = True
                    
                    if isinstance(right_operand, (int, bool, str)):
                        if not isinstance(left_operand, (int, bool, str)):
                            raise_error = True
                        if type(left_operand) != type(right_operand):
                            raise_error = True
                    
                    if raise_error:
                        self.interpreter_obj.error(
                            ErrorType.TYPE_ERROR,
                            f"Can't use operator {operator} with value {left_operand} and {right_operand}",
                        )
                    return left_operand != right_operand
                elif operator == "==":
                    raise_error = False
                    if isinstance(left_operand, (int, bool, str)):
                        if not isinstance(right_operand, (int, bool, str)):
                            raise_error = True
                        if type(left_operand) != type(right_operand):
                            raise_error = True
                    
                    if isinstance(right_operand, (int, bool, str)):
                        if not isinstance(left_operand, (int, bool, str)):
                            raise_error = True
                        if type(left_operand) != type(right_operand):
                            raise_error = True
                    
                    if raise_error:
                        self.interpreter_obj.error(
                            ErrorType.TYPE_ERROR,
                            f"Can't use operator {operator} with value {left_operand} and {right_operand}",
                        )
                    return left_operand == right_operand
                elif operator == "&":
                    if not isinstance(left_operand, bool) or not isinstance(right_operand, bool):
                        self.interpreter_obj.error(ErrorType.TYPE_ERROR, f"Can't use operator {operator} with value {left_operand} and {right_operand}")
                    return left_operand & right_operand
                elif operator == "|":
                    if not isinstance(left_operand, bool) or not isinstance(right_operand, bool):
                        self.interpreter_obj.error(ErrorType.TYPE_ERROR, f"Can't use operator {operator} with value {left_operand} and {right_operand}")
                    return left_operand | right_operand

            elif operator == "!":
                operand = self.evaluate_expression(operands[0], parameter_values)
                if isinstance(operand, bool):
                    return True if operand == False else False
                else:
                    self.interpreter_obj.error(ErrorType.TYPE_ERROR)

            elif keyword == InterpreterBase.PRINT_DEF:
                string_value = ""
                for val in expression:
                    if isinstance(val, list):
                        statement_result = self.evaluate_expression(
                            val, parameter_values
                        )
                        if statement_result != None:
                            string_value += str(statement_result)
                    elif not (val.startswith('"') and val.endswith('"')):
                        res = self.evaluate_expression(val, parameter_values)
                        if isinstance(res, bool):
                            res = InterpreterBase.TRUE_DEF if res else InterpreterBase.FALSE_DEF
                        string_value += str(res)
                    else:
                        string_value += val[1:-1]
                return string_value
            else:
                raise ValueError(f"Invalid expression: {expression}")
        else:
            raise ValueError(f"Invalid expression: {expression}")

    def get_variable_value(self, variable_name, parameter_values):
        if variable_name in parameter_values:
            return parameter_values[variable_name]
        elif variable_name in self.fields:
            return self.fields[variable_name]
        else:
            self.interpreter_obj.error(ErrorType.NAME_ERROR)

    def set_variable_value(self, value, variable_name, parameter_values):
        if variable_name not in parameter_values and variable_name not in self.fields:
            self.interpreter_obj.error(ErrorType.NAME_ERROR)

        if variable_name in parameter_values:
            parameter_values[variable_name] = value
        else:
            self.fields[variable_name] = value