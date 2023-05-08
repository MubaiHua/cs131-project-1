from bparser import BParser, StringWithLineNumber
from intbase import InterpreterBase, ErrorType
from classes import ClassDefinition

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)  # call InterpreterBase’s constructor
        self.classes = {}

    def get_classes(self):
        return self.classes

    def run(self, program):
        result, parsed_program = BParser.parse(program)  # parse the program
        if not result:
            return  # error with parsing

        self.add_classes(parsed_program)
        class_def = self.classes[super().MAIN_CLASS_DEF]  # get the main class
        main_obj = class_def.instantiate_object()
        main_obj.call_method(super().MAIN_FUNC_DEF, [])

    def add_classes(self, parsed_program):
        has_main_class = False  # check if main class exist

        for class_decleration in parsed_program:
            class_name = class_decleration[1]
            if class_name in self.classes:
                super().error(
                    ErrorType.TYPE_ERROR, f"Duplicate class name {class_name}"
                )  # handle duplicate class name

            if class_name == super().MAIN_CLASS_DEF:
                has_main_class = True

            self.classes[class_name] = ClassDefinition(
                class_name, class_decleration[1:], self
            )  # create a new class

        if not has_main_class:  # if main class doesn't exist
            super().error(ErrorType.SYNTAX_ERROR, "There must be an Main class")


def read_txt_file(file_path):
    """
    Reads a text file and returns each line as a list of strings.

    Parameters:
        file_path (str): The path to the text file.

    Returns:
        list: A list of strings, where each string is a line from the text file.
    """
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
    return lines


# # Testing the interpreter
# interpreter = Interpreter()
# brewin_program = read_txt_file(
#     "/home/mubai/CS131/cs131-project-1/program.txt"
# )  # Provide a valid Brewin program here
# interpreter.run(brewin_program)
