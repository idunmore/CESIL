# CESIL Plus - Computer Education in Schools Instruction Lanaguage
#              Interpreter w/ optional Extensions
#
# Copyright (C) 2020-2023, Ian Michael Dunmore
#
# License: https://github.com/idunmore/CESIL/blob/master/LICENSE

import enum
import re
import click
from typing import Self, Callable
from dataclasses import dataclass

# Constants

# CESIL identifiers/labels consist of up to 6 uppercase alphanumeric
# characters, starting with a letter (e.g. A12345)
IDENTIFIER_PATTERN = re.compile('^[A-Z][A-Z0-9]{0,5}')

# CESIL integers are signed 24-bit values from -8388608 to +8388607
VALUE_MAX = 8388607
VALUE_MIN = -8388608

# CESIL comments begin with a *, but on punched-cards from coding sheets
# can also start with (, ** and *C
COMMENT_PREFIX = ['*', '(', '**', '*C']

# The data section in a CESIL program starts with a % on a new line
START_DATA_SECTION = '%'

# The overall listing, including data section, is terminated with "*"
END_FILE = '*'

# Instruction Tuple Indexes
FUNCTION_PTR = 0
OPERAND_TYPE = 1

# DEBUG Strings
STACK_EMPTY = 'Empty'
ACC_FLAG_NONE = 'None'
ACC_FLAG_NEG = 'Neg'
ACC_FLAG_ZERO = 'Zero'

# Punched Card Column Positions
LABEL_COL_START = 0
INSTRUCTION_COL_START = 8
OPERAND_COL_START = 16

# Classes

class OpType(enum.Enum):
    '''Operand Types'''
    NONE = 0
    LABEL = 1
    LITERAL = 2
    LITERAL_VAR = 3
    VAR = 4
    
@dataclass
class CodeLine:
    '''Represents the processable elements of line of CESIL code'''
    label: str
    instruction: str
    operand: str
    line_number: int = 0

class CESILException(Exception):
    '''Base CESIL generic exception (syntax or runtime)'''
    def __init__(self: Self, line_number: int, message: str, code: object):
        self.line_number = line_number
        self.message = message
        self.code = code
    
    def print(self: Self):
        print('Error: {0} at line {1}: {2}'.
            format(self.message, self.line_number, self.code))

class CESIL():
    '''CESIL Interpreter, Debugger & CESIL Program Instance'''

    def instruction(mnemonic: str, op_type: OpType, is_plus: bool) -> object:
        '''Decorator for designating instance methods as CESIL instructions.'''
        def _decorator(func: Callable) -> object:
            # Mnemonic is the CESIL instruction name, which may be different
            # to the Python function name (to avoid reserved word conflicts)
            func.__mnemonic = mnemonic            
            func.__op_type = op_type
            func.__is_plus = is_plus            
            return func
        return _decorator    
    
    def __init__(self: Self, is_plus: bool, debug_level: int):
        '''Initialize new CESIL instance.'''
        # CESIL Instructions
        self._instructions = {}

        # CESIL Program Elements
        self._program_lines = []
        self._data_values = []
        self._labels = {}
        self._variables = {}

        # Pure CESIL Execution State
        self._accumulator = 0
        self._instruction_ptr = 0
        self._data_ptr = 0
        self._current_line = None
        # "Plus" Execution State
        self._stack = []
        self._call_stack = []

        # File/program status and flags/values
        self._debug_level = debug_level
        self._is_text = True
        self._is_plus = is_plus
        self._branch = False
        self._halt_execution = False

        self._register_instructions()        

    def load(self: Self, filename: str, source_format: str):        
        '''Loads program file, observing TEXT/PUNCH CARD formatting'''
        is_code_section = True
        line_number = 0
        instruction_index = 0

        # Determine if we're parsing text file format or punch card
        self._is_text = True if source_format[0].casefold() == 't' else False

        with open(filename, 'r') as reader:
            for line in reader:
                line_number += 1
                # Skip blank lines and comments.
                if self._is_blank(line) or self._is_comment(line):
                    continue

                if is_code_section == True:           
                    # Transition from Code to Data?
                    if self._is_data_start(line):
                        is_code_section = False
                    else:
                        # Process Code Line
                        self._process_code_line(line, instruction_index,
                            line_number)
                        instruction_index += 1
                else:
                    # We're in the Data Section so process line as data values      
                    self._process_data_line(line)
    
    def run(self: Self):
        '''Executes the current CESIL program.'''
        # Iterate the "program" ...
        self._instruction_ptr = 0
        while self._instruction_ptr < len(self._program_lines):
            # Output debug info, if enabled - for line ABOUT to execute!
            if self._debug_level > 0:
                self._debug_out(self._debug_level)

            # Get line to execute, and execute it ...
            self._current_line = self._program_lines[self._instruction_ptr]
            self._instructions[self._current_line.instruction][FUNCTION_PTR]()
            # Handle accumulator overflow           
            if not self._is_legal_integer(self._accumulator):
                raise CESILException(
                    self._current_line.line_number,
                    'Accumulator overlow; value out of range',
                    self._accumulator
                )

            # If halt is set, we quit exectuion immediately.
            if self._halt_execution: break

            # If branch is set, the instruction_ptr has changed, so we go
            # back to the start of the exectution loop without incrementing it.
            if self._branch:
                self._branch = False
                continue           
            
            # Nothing else has changed the execution path, so move to the
            # next instruction
            self._instruction_ptr += 1   

    def _process_code_line(
            self: Self, line: str, instruction_index: int, line_number: int):
        '''Process a line of source code, and add it to the Program'''
        # Parse the raw source line
        code_line = self._parse_code_line(line, line_number)

        # Add the label, if present, with its instruction pointer
        if code_line.label != None: 
            self._labels[code_line.label] = instruction_index

        # Variable? (A legal IDENTIFIER that ISN'T a LABEL)
        if (self._is_legal_identifier(code_line.operand) and                       
            self._instructions[code_line.instruction][OPERAND_TYPE] ==
            OpType.LITERAL_VAR
           ):
            # Add the variable and initialize it                          
            self._variables[code_line.operand] = 0

        # Add a code line to the program if there's an instruction
        if code_line.instruction != None:
            code_line.line_number = line_number
            self._program_lines.append(code_line)

    def _process_data_line(self: Self, line: str):
        '''Adds any data on this line to our data values.'''                    
        if line[0] != END_FILE: 
            for data in line.split():
                self._data_values.append(int(data)) 
            
    def _parse_code_line(self: Self, line: str, line_number: int) -> CodeLine:
        '''Parse line of code, accounting for TEXT/CARD formatting'''
        parts = self._get_line_parts(line, line_number)
        current_part = 0
        last_part = len(parts) -1
        label = None
        instruction = None
        operand = None

        if self._is_legal_identifier(parts[current_part]):
            # We have a label ...
            label = parts[current_part]
            if current_part < last_part: current_part +=  1
            
        if self._is_instruction(parts[current_part]):
            # We have an instruction
            instruction = parts[current_part]            
            op_type = self._instructions[instruction][OPERAND_TYPE]           

            # Get the Operand if there is one.
            if op_type != OpType.NONE:
                if current_part < last_part: current_part += 1
                potential_operand = parts[current_part]
                
                if op_type == OpType.LITERAL:
                    # Only applies to PRINT, which needs special handling.
                    # Put SPLIT parts back together for PRINT "" strings                    
                    while current_part < last_part:
                        current_part += 1
                        potential_operand += ' ' + parts[current_part]

                    # Strip Quotes and any trailing comment.
                    operand = potential_operand[potential_operand.find('"')+1:
                                potential_operand.rfind('"')]
                else:
                    # Validate and get the label, literal or variable
                    operand = self._get_lab_lit_var(
                        op_type, potential_operand, line_number)

        return CodeLine(label, instruction, operand)

    def _get_line_parts(self: Self, line: str, line_number: int) -> list[str]:
        '''Split line into parts based on TEXT/CARD formatting'''
        if self._is_text:
            return line.split()
        else:
            return self._split_punch_card_line(line, line_number)        

    def _get_lab_lit_var(
            self: Self, op_type: OpType, potential_operand: str,
            line_number: str) -> int | str:
        '''Validates a label, literal or operand, and returns it
        in the appropriate format if valid.'''
        operand = None
        # If LABEL, then it's easy.
        if (op_type == OpType.LABEL
            and self._is_legal_identifier(potential_operand)):
                operand = potential_operand
        elif op_type == OpType.LITERAL_VAR or op_type == OpType.VAR:
            # If a LITERAL, convert to an integer.
            if self._is_legal_identifier(potential_operand):
                operand = potential_operand                    
            elif self._is_legal_integer(potential_operand):
                operand = int(potential_operand)
            else:   
                raise CESILException(
                    line_number, 'Illegal operand', potential_operand)                        

        return operand

    def _split_punch_card_line(
            self: Self, line: str, line_number: int) -> list[str]:
        '''Splits code line based on PUNCH CARD column settings'''
        parts = []
        length = len(line)

        if length <= INSTRUCTION_COL_START:
            # Only a label on this line:
            parts.append(line.strip())
        elif length <= OPERAND_COL_START:
            # Instruction, with or without label
            parts.append(line[LABEL_COL_START:INSTRUCTION_COL_START].strip())
            parts.append(line[INSTRUCTION_COL_START:OPERAND_COL_START].strip())
        else:
            # Instruction and operand, with or without label
            parts.append(line[LABEL_COL_START:INSTRUCTION_COL_START].strip())
            parts.append(line[INSTRUCTION_COL_START:OPERAND_COL_START].strip())

            # If the operand is a string, make sure that's all we extract
            operand = line[OPERAND_COL_START:].strip()
            if operand[0] == '"':
                # This is a string, so find the next " character.
                end_quote = operand.find('"', 1)
                if end_quote > 0:
                    operand = operand[0:end_quote]
                else:
                    raise CESILException(
                        line_number, 'Unterminated String', operand)

            parts.append(operand)
            
        return parts

    def _get_real_value(self: Self, operand: int | str) -> int:
        '''Resolves actual Operand value from a LITERAL or VARIABLE'''
        if self._is_legal_identifier(operand):
            return int(self._variables[operand])
        else:
            return int(operand)  
    
    def _is_legal_integer(self: Self, value: int) -> bool:
        '''Bounds checks "value" as a legal INTEGER (24-bit, signed)'''
        try:
            num = int(value)
            return (num >= VALUE_MIN and num <= VALUE_MAX)
        except:
            return False

    def _is_comment(self: Self, line: str) -> bool:
        '''Determines if "line" is a CESIL comment'''
        return len(line) > 0 and line[0] in COMMENT_PREFIX
    
    def _is_blank(self: Self, line: str) -> bool:
        '''Determines if "line" is BLANK in CESIL terms'''
        return True if len(line.strip()) == 0 or line == '\n' else False

    def _is_legal_identifier(self: Self, identifier: str) -> bool:
        '''Determines if the "identifier" is legal in CESIL'''
        if self._is_instruction(identifier):
            # Instructions are RESERVED words and NOT legal identifiers!
            return False
        else:
            return re.fullmatch(
                IDENTIFIER_PATTERN, str(identifier)) is not None
    
    def _is_instruction(self: Self, instruction: str) -> bool:
        '''True if "instruction" is a valid CESIL/Plus instruction'''
        return instruction in self._instructions
    
    def _is_data_start(self: Self, line: str) -> bool:
        '''True if "line" indicates the start of the "Data Section"'''
        return len(line) > 0 and line[0] == START_DATA_SECTION

    def _register_instructions(self: Self):
        '''Registers decorated Python methods as CESIL Instructions'''
        # Inspect functions (callable methods) through class attributes ...
        functions = [atr for atr in dir(CESIL) if callable(getattr(self, atr))]
        for function_name in functions:
            function = getattr(self, function_name)           
            # CESIL function only if decorated w/ @instruction (has __mnemonic)                      
            if getattr(function, '_CESIL__mnemonic', None) != None:
                # Only add "PLUS" instructions if in PLUS mode
                if function.__is_plus and not self._is_plus: continue

                self._instructions[function.__mnemonic] = (
                    function, function.__op_type)
                
    # Debugger Methods

    def _debug_out(self: Self, level: int):
        '''Debug Output'''
        # Just exit if we're not in debug mode ...
        if level == 0: return

        # Summary output: accumulator value, flags, top stack value, code
        line = self._program_lines[self._instruction_ptr]
        label = str(line.label if line.label is not None else '')
        operand = self._debug_get_formatted_operand(line)
        top_of_stack = self._debug_get_top_of_stack()    
        flags = self._debug_get_accumulator_flags()
    
        summary_format = 'DEBUG:\t[Accumlator: {0:>10}] [Flags: {1:>4}]'
        summary_format += ' [Stack Top: {2:>10s}] -> {3:<8}{4:<8} {5}'
        print(summary_format.format(self._accumulator, flags, top_of_stack,
                label, line.instruction, operand), end='')
                
        # Add Verbose output?
        if level >= 3: self._ouput_stack_variable_detail()

        # Pause for [Enter]?
        if level == 2 or level == 4:
            # This results in a new-line from the [Enter] key ...
            input()
        else:
            # ... otherwise we need to output our own new-line.
            print('')

    def _debug_get_top_of_stack(self: Self) -> int | str:
        ''' # Gets the current top of the stack, 'Empty' if no items'''       
        if len(self._stack) > 0:
            return str(self._stack[len(self._stack)-1])
        else:
            return STACK_EMPTY
      
    def _debug_get_accumulator_flags(self: Self) -> str:
        '''Gets Accumulator State Flag: (ZERO, NEG or none)'''
        if self._accumulator == 0:
            return ACC_FLAG_ZERO
        elif self._accumulator < 0:
            return ACC_FLAG_NEG
        else:
            return ACC_FLAG_NONE
        
    def _ouput_stack_variable_detail(self: Self):
        '''Outputs details for STACK and VARIABLE values.'''        
        print('\n\n\t[Stack:                ] [Variable :    Value]')
        
        # Which list has more items in it, the stack or the variable list?
        longest_list = max(len(self._stack), len(self._variables))
        index = 0
        while index < longest_list:
            stack_item = stack_pos = ''
            variable_name = variable_value = var_str = ''

            # Do current stack item, if there is one.
            if index < len(self._stack):
                stack_idx = (len(self._stack) - index) -1
                stack_item = self._stack[stack_idx]
                if stack_idx == len(self._stack) -1:
                    stack_pos = '-> (Top)'
                elif stack_idx == 0:
                    stack_pos = '-> (Bottom)'
        
            stack_str = '{0:>13} {1:<11}'.format( stack_item, stack_pos)
            
            # Do next variable, if there is one.        
            if index < len(self._variables):
                variable_name = list(self._variables)[index - 1]
                variable_value = self._variables[variable_name]
                var_str = '{0:>6} : {1:>8}'.format( variable_name,
                                                    variable_value)
        
            print('{0:>31}  {1:>20}'.format(stack_str, var_str))
            index += 1    
    
    def _debug_get_formatted_operand(self: Self, line: str) -> int | str:
        '''# Extracts and formats an operand for DEBUG output'''
        operand = ''
        if line.operand is not None:
            # Wrap string/PRINT literals in "" for debug display
            print_fmt = '"{0}"' if line.instruction == 'PRINT' else '{0}'
            operand = print_fmt.format(line.operand)

        return operand

    # CESIL Instructions

    @instruction("HALT", OpType.NONE, False)    
    def _halt(self: Self):
        '''Halts program execution'''
        self._halt_execution = True

    @instruction("IN", OpType.NONE, False)
    def _in_cesil(self: Self):
        '''Inputs the next DATA ITEM and puts it in the ACCUMULATOR'''
        self._accumulator = int(self._data_values[self._data_ptr])
        self._data_ptr += 1

    @instruction("OUT", OpType.NONE, False)
    def _out(self: Self):
        '''Ouputs ACCUMULATOR value, without ending the LINE'''
        # End the line if we are in debug mode
        new_line = '\n' if self._debug_level > 0 else ''
        print(self._accumulator, end=new_line)

    @instruction("LOAD", OpType.LITERAL_VAR, False)
    def _load_cesil(self: Self):
        '''Loads value of OPERAND (LITERAL or VARIABLE) into the ACCUMULATOR'''
        self._accumulator = self._get_real_value(self._current_line.operand)

    @instruction("STORE", OpType.VAR, False) 
    def _store(self: Self):
        '''Stores value of ACCUMULATOR into VARIABLE'''
        if self._is_legal_identifier(self._current_line.operand):
            self._variables[self._current_line.operand] = self._accumulator

    @instruction("LINE", OpType.NONE, False)
    def _line(self: Self):
        '''Move to a new LINE (EOL)'''
        print('')

    @instruction("PRINT", OpType.LITERAL, False)
    def _print_cesil(self: Self):
        '''Prints LITERAL on the current LINE'''
        # End the line if we are in debug mode
        new_line = '\n' if self._debug_level > 0 else ''
        print(self._current_line.operand, end=new_line)

    @instruction("ADD", OpType.LITERAL_VAR, False)
    def _add(self: Self):
        '''Adds OPERAND to ACCUMULATOR'''
        self._accumulator += self._get_real_value(self._current_line.operand)

    @instruction("SUBTRACT", OpType.LITERAL_VAR, False)
    def _subtract(self: Self):
        '''Subtacts OPERAND from ACCUMULATOR'''
        self._accumulator -= self._get_real_value(self._current_line.operand)

    @instruction("MULTIPLY", OpType.LITERAL_VAR, False)
    def _multiply(self: Self):
        '''Multiplies ACCUMULATOR by OPERAND'''
        self._accumulator *= self._get_real_value(self._current_line.operand)

    @instruction("DIVIDE", OpType.LITERAL_VAR, False)
    def _divide(self: Self):
        '''Divides ACCUMULATOR by OPERAND'''
        self._accumulator /= self._get_real_value(self._current_line.operand)

    @instruction("JUMP", OpType.LABEL, False)
    def _jump(self: Self):
        '''Jumps to the INSTRUCTION at LABEL'''
        self._instruction_ptr = self._labels[self._current_line.operand]
        self._branch = True

    @instruction("JIZERO", OpType.LABEL, False)
    def _jizero(self: Self):
        '''Jumps to the INSTRUCTION at LABEL if the ACCUMULATOR is ZERO'''
        if self._accumulator == 0:
            self._instruction_ptr = self._labels[self._current_line.operand]
            self._branch = True
    
    @instruction("JINEG", OpType.LABEL, False)
    def _jineg(self: Self):
        '''Jumps to the INSTRUCTION at LABEL if the ACCUMULATOR is NEGATIVE'''
        if self._accumulator < 0:
            self._instruction_ptr = self._labels[self._current_line.operand]
            self._branch = True

    # CESIL Plus Instructions

    @instruction("MODULO", OpType.LITERAL_VAR, True)
    def _modulo(self: Self):
        '''Modulo division of ACCUMULATOR by OPERAND; ACCUMULATOR = REMAINDER'''
        self._accumulator %= self._get_real_value(self._current_line.operand)

    @instruction("RETURN", OpType.NONE, True)
    def _return_cesil(self: Self):
        '''Returns from SUBROUTINE to INSTRUCTION after JUMPSR/JSIZERO/JSINEG'''
        self._instruction_ptr = self._call_stack.pop()

    @instruction("JUMPSR", OpType.LABEL, True)
    def _jumpsr(self: Self):
        '''Jumps to the SUBROUTINE at LABEL'''
        self._call_stack.append(self._instruction_ptr)
        self._instruction_ptr = self._labels[self._current_line.operand]
        self._branch = True

    @instruction("JSIZERO", OpType.LABEL, True)
    def _jsizero(self: Self):
        '''Jumps to the SUBROUTINE at LABEL if the ACCUMULATOR is ZERO'''
        if self._accumulator == 0:
            self._call_stack.append(self._instruction_ptr)
            self._instruction_ptr = self._labels[self._current_line.operand]
            self._branch = True

    @instruction("JSINEG", OpType.LABEL, True)
    def _jsineg(self: Self):
        '''Jumps to the SUBROUTINE at LABEL if the ACCUMULATOR is NEGATIVE'''
        if self._accumulator < 0:
            self._call_stack.append(self._instruction_ptr)
            self._instruction_ptr = self._labels[self._current_line.operand]
            self._branch = True

    @instruction("POP", OpType.NONE, True)
    def _pop(self: Self):
        '''Pops the top value off the STACK and into the ACCUMULATOR'''
        self._accumulator = self._stack.pop()

    @instruction("PUSH", OpType.NONE, True)
    def _push(self: Self):
        '''Pushes the ACCUMULATOR value onto the top of the STACK'''
        self._stack.append(self._accumulator)

# Command Line Interface 
@click.command()
@click.option('-s', '--source',
    type=click.Choice(['t', 'text', 'c', 'card'], case_sensitive=False),
    default='text', show_default=True, help='Text or punched Card input.')
@click.option('-d', '--debug',
    type=click.Choice(['0', '1', '2', '3', '4'], case_sensitive=False),
        default='0', show_default=True, help='Debug mode/verbosity level.')
@click.option('-p', '--plus', is_flag=True, default=False,
    help='Enables "plus" mode language extensions.')
@click.version_option('0.9.2')
@click.argument('source_file', type=click.Path(exists=True))
def cesilplus(source: str, debug: int, plus: bool, source_file: str):
    """CESILPlus - CESIL Interpreter (w/ optional language extentions).
    
    \b
      CESIL: Computer Eduction in Schools Instruction Language

      "Plus" language extensions add a STACK and SUBROUTINE support to
    the language, enabled with the -p | --plus options.  Extensions are
    DISABLED by default.

      "Plus" Mode - Extension instructions:

    \b
        MODULO  operand - MODULO division of ACCUMULATOR by operand
                          (sets ACCUMULATOR to REMAINDER)
        
        PUSH            - PUSHes the ACCUMULATOR value on to STACK
        POP             - POPs top value from STACK into the ACCUMULATOR
        
        JUMPSR  label   - Jumps to SUBROUTINE @ label
        JSIZERO label   - Jumps to SUBROUTINE @ label if ACCUMULATOR = 0
        JSINEG  label   - Jumps to SUBROUTINE @ label if ACCUMULATOR < 0
        RETURN          - Returns from SUBROUTINE and continues execution
    """
        
    try:        
        cesil_interpreter = CESIL(plus, int(debug))
        cesil_interpreter.load(source_file, source)
        cesil_interpreter.run()
    except CESILException as err:
        err.print()

# Run!
if __name__ == '__main__':
    cesilplus() 