# CESIL

A [CESIL](https://en.wikipedia.org/wiki/CESIL) interpreter written in Python, intended as a "Language Preservation" project.

CESIL is the Computer Education in Schools Instruction Language.  It was developed as an introductory instructional language, targeted at British secondary school students (ages 11 to 16).  It was developed by [International Computers Limited](https://en.wikipedia.org/wiki/International_Computers_Limited) ([ICL](https://en.wikipedia.org/wiki/International_Computers_Limited)), a sort of "British version of IBM", as part of the "Computer Education in Schools" (CES) project, and was introduced in 1974.

## CESIL & CESIL "Plus"

In addition to the original, standard, CESIL instruction set, this version implements what I call CESIL "Plus".  This is *my* extension of the original CESIL language.  It is not "official" nor "standard" in anyway.  It consists of seven new instructions (50% of the original total), which incorporate new features, that my CESIL implementation (optionally) adds to the official language.

There are two modes of operation:

-   **Standard**  - Default mode; matches the original implementation of the CESIL language.

-   **Plus**  - Optional; adds instructions for a stack, subroutines and modulo division.

"Plus" mode is enabled by use of the `-p` or `--plus` options; the default behavior only observes the original CESIL instructions.  In "Plus" mode, the following additional features/instructions are available:

- A **stack** capability, and the instructions to support its use: `PUSH` and `POP` (see "[Stack_test.ces](https://github.com/idunmore/CESIL/blob/master/examples/Stack_test.ces)").

 - **Subroutine** support; expands the simple branch/jump capabilities of CESIL with the ability to jump to, or "call" a new point of execution, and then *return* to the original point of execution (see "[Sub_test.ces](https://github.com/idunmore/CESIL/blob/master/examples/Sub_test.ces)").

  Adds the instructions: `JUMPSR`, `JSIZERO`, `JSINEG` and `RETURN`.

 - **Modulo division**; a new `MODULO` instruction that leaves the remainder of a division in the ACCUMULATOR.

 ## Installing

* Install Python 3.11.1 or later (may work with earlier versions, provided they have built-in type-hint support, but not tested).
* Clone the repository, **or** download [src/CESIL.py](https://github.com/idunmore/CESIL/blob/master/src/CESIL.py) and [requirements.txt](https://github.com/idunmore/CESIL/blob/master/requirements.txt)
* Run the following command (in the directory you downloaded the above into):

> 
    pip install -r requirements.txt
    
Run:

    python3 CESIL.py --version

You should see something like:

    CESIL.py, version 0.9.3

If not, either you don't have Python installed correctly (most likely this is a path issue) or the dependencies (per requirements.txt) did not install.

## Usage

Usage is simple:

    python3 CESIL.py filename

This will run the CESIL program contained in the file "filename".  Any output will be displayed on the console.

For full usage details, enter:

    python3 CESIL.py --help

That will display the complete built-in help, along with options:


    Usage: CESIL.py [OPTIONS] SOURCE_FILE
      
      CESILPlus - CESIL Interpreter (w/ optional language extentions).
    
        CESIL: Computer Eduction in Schools Instruction Language
    
        "Plus" language extensions add a STACK, SUBROUTINE support and MODULO
        division to the language, enabled with the -p | --plus options. Extensions
        are DISABLED by default.
    
        "Plus" Mode - Extension instructions:
    
	      MODULO  operand - MODULO division of ACCUMULATOR by operand    
	                       (sets ACCUMULATOR to REMAINDER)
    
	      PUSH            - PUSHes the ACCUMULATOR value on to STACK    
	      POP             - POPs top value from STACK into the ACCUMULATOR
    
	      JUMPSR  label   - Jumps to SUBROUTINE @ label    
	      JSIZERO label   - Jumps to SUBROUTINE @ label if ACCUMULATOR = 0    
	      JSINEG  label   - Jumps to SUBROUTINE @ label if ACCUMULATOR < 0    
	      RETURN          - Returns from SUBROUTINE and continues execution
    
    Options:    
      -s, --source [t|text|c|card] Text or Card input. [default: text]    
      -d, --debug [0|1|2|3|4] Debug mode/verbosity level. [default: 0]    
      -p, --plus Enables "plus" mode language extensions.    
      --version Show the version and exit.    
      --help Show this message and exit.
      
### Text vs. Card Mode
Text and Card modes (set via the `-s`, `--source` option) determine whether strict adherence to character/column positions from coding sheets or "Cards" are observed, or if simple Text files are expected.  The default is Text mode.

Text mode only assumes valid whitespace (spaces or tabs) separation between `labels`, `instructions` and `operands`.  The number of spaces/tabs doesn't matter.  

In Card mode, there are fixed-width columns for `labels` and `instructions` (8 characters each), and then `operands` can be as wide as the remainder of the line.  See [card_test.ces](https://github.com/idunmore/CESIL/blob/master/examples/card_test.ces) for an example.

This means it is possible to have code that works in one mode but not the other.  For example:

    1234567890123456789012345678901234567890
    -------|-------|------------------------
    LABEL  |INSTRUC|OPERAND
    -------|-------|------------------------
            SUBTRACT 10
            SUBTRACT10       
    
The first line is only valid in Text mode, as the `operand` will not be read correctly in Card mode.  The second line is only valid in Card mode, as there is no whitespace separating the `instruction` from the `operand`.

### Debug Mode
The debug option (`-d, --debug`) enables a debug view, which shows the current state of the CESIL execution environment.  There are five options for the debug mode, specified as `0` to `4`, which break down as follows:

    0 = No Debugging (default if no -d | --debug option specified)
    1 = Summary output
    2 = Summary output w/ step
    3 = Verbose output
    4 = Verbose output w/ step

Options `1` and `2` show either summary or verbose output, respectively, without pausing execution of the program.  Options `3` and `4` show either summary or verbose output, respectively, but pause execution (`stops`) after every line of the CESIL program until the user hits `[Enter]`, allowing stepping-through the code.

The `verbose` output, in "stop" mode, looks like this:

    DEBUG:	[Accumlator:          7] [Flags: None] [Stack Top:          7] ->         LINE
    
            [Stack:                ] [Variable :    Value]
                      7 -> (Top)         COUNT :        7
                      6
                      5
                      4
                      3
                      2
                      1 -> (Bottom)

The top line displays the current value of the ACCUMULATOR, which flags are set (`None`, `Zero`, `Neg`) , the top value on the `stack` and the current line of `code`.  Below this, the entire contents of the `stack` are shown, from the top down, along with all current `variables` and their `values`.

In `summary` mode, only the **top** line of the above display would be shown, but consecutive lines of code display one after the other as they execute:

    DEBUG:	[Accumlator:          0] [Flags: Zero] [Stack Top:      Empty] ->         LOAD     0
    DEBUG:	[Accumlator:          0] [Flags: Zero] [Stack Top:      Empty] ->         STORE    COUNT
    DEBUG:	[Accumlator:          0] [Flags: Zero] [Stack Top:      Empty] -> STACK   LOAD     COUNT
    DEBUG:	[Accumlator:          0] [Flags: Zero] [Stack Top:      Empty] ->         ADD      1
    DEBUG:	[Accumlator:          1] [Flags: None] [Stack Top:      Empty] ->         STORE    COUNT
    DEBUG:	[Accumlator:          1] [Flags: None] [Stack Top:      Empty] ->         PUSH
    DEBUG:	[Accumlator:          1] [Flags: None] [Stack Top:          1] ->         OUT


## Why CESIL?

A couple of reasons ...

* The **first** is more along the lines of "[a lonely impulse of delight](https://www.poetryfoundation.org/poems/57311/an-irish-airman-foresees-his-death)".

  CESIL was a language I learned in school, in keeping with its CES origins, for my Computer Studies "[O-Level](https://en.wikipedia.org/wiki/GCE_Ordinary_Level)".  As I was already coding in 6502 and Z80A assembly languages, as well as a BASIC and Logo, it was a bit of a curiosity - but also a necessity for the classwork.  The very limited nature of the language made me think about problems in a different way, which was academically interesting as well as oddly enjoyable.

  I suppose nostalgia, with its propensity to make things seem much more fun/interesting than the reality of the time, is also partly at work here.  There are days I miss the bare-metal programming I did back in the days of the [Altair 8800](https://en.wikipedia.org/wiki/Altair_8800), [NasCom 1](https://en.wikipedia.org/wiki/Nascom), [Atari 400/800](https://en.wikipedia.org/wiki/Atari_8-bit_family) and Sinclair Research [ZX81](https://en.wikipedia.org/wiki/ZX81) and [ZX Spectrum](https://en.wikipedia.org/wiki/ZX_Spectrum).

  I looked at some of the other open-source CESIL implementations, and they were fun to play with for a little bit.  But it was really creating a CESIL interpreter (originally it was "compiled") that was fueling my interest.

* The **second** is a bit more "practical" ... or as practical as things are likely to get when it comes to "dead" languages.

  As part of my on-going computer science/engineering/programming mentoring efforts, I wanted to introduce my mentees to a very simple, limited, programming model and get away from massively powerful functions riding on top of multiple levels of abstraction.  Have them write some code that way, compare and contrast it with modern, higher-level, approaches.

  And then, just as importantly, have *them* implement a similar language themselves.

  From there, I wanted something to use in additional mentoring to look at ways of making code maintainable and both easily and cleanly extensible - which is what drove this "final" version (vs. earlier prototypes).  

* And **third**,  to use the extension mechanisms from point two, add additional features/instructions/capabilities (e.g., a stack, modulo division and subroutines) and see what affect those would have on the way code is written to solve different problems.

# Implementation Approach & Theory of Operation

The real/primary implementation here is [src/CESIL.py](https://github.com/idunmore/CESIL/blob/master/src/CESIL.py).  This is an evolution of earlier, experimental, "[prototype](https://github.com/idunmore/CESIL/blob/master/README.md#prototypes)" versions that makes major changes to the internal implementation of CESIL instructions, how they are enumerated and, most importantly, how they are executed.

In *common* with the prototypes, particularly [prototypes/CESILPy.py](https://github.com/idunmore/CESIL/blob/master/prototypes/CESILPy.py), is the parsing logic, command line interface, general structure and some of the "extension" instructions.  However, here the extensibility of the supported instruction set is made extremely easy, and the execution process is more generalized to allow simply, and flexible, composition, of new instructions and/or the addition of new language features:

## Defining CESIL Instructions
To implement an instruction for our CESIL interpreter, we provide a simple Python method, as a "protected" member of the `CESIL` class, which can then manipulate the state of that class to provide its behavior.  The example below implements the "HALT" instruction:  
     
    def _halt(self):    
        '''Halts program execution'''    
        self._halt_execution = True

In this case, it sets the program execution flag _`halt_exection`, which causes the `run()` loop to terminate the program.

To identify a method as a CESIL instruction, rather than some other method in the class, we apply a custom decorator to the method's definition:

    @instruction("HALT", OpType.NONE, False)    
    def _halt(self):    
        '''Halts program execution'''    
        self._halt_execution = True

The `@instruction` decorator provides the CESIL instruction "mnemonic" that will be mapped to the Python function name (to prevent collisions between Python and CESIL keywords/instruction names), indicates the type of operand the instruction uses, and whether the instruction is considered part of *my* "Plus", or extended, version the language.

At runtime, all of the CESIL instructions are "registered" - i.e., evaluated and added to an instructions dictionary, indexed by CESIL instruction "mnemonic", and containing a *function pointer* to the implementing Python function, as well as the operand type the function uses.

### Adding a new "Extension" Instruction

This is as simple as writing a simple Python function, within the `CESIL` class, and then applying the `@instruction` decorator.  As an example, the following code adds the `MODULO` instruction, which performs modulo-division on the CESIL accumulator:

    @instruction("MODULO", OpType.LITERAL_VAR, True)
    def _modulo(self):
        '''Modulo division of ACCUMULATOR by OPERAND; ACCUMULATOR = REMAINDER'''
        self._accumulator %= self._get_real_value(self._current_line.operand)

The _modulo() function simply assigns the modulo-divided value of the accumulator back to the accumulator (i.e., puts the remainder on the accumulator).  Note that the `@instruction` decorator indicates this function can operate on LITERAL or VARIABLE operands, and that it is an "extension" or "plus" instruction.

No other code needs to be touched to make this work.

*ALL of the supported CESIL instructions here are implemented in this fashion.*

### Instructions that change State and/or Program Flow

Most instructions change the internal state of the CESIL execution environment, the entirety of which is accessible to any CESIL instruction.  However, most commonly mutated states are:

* **_accumulator** - The current `accumulator` value.

  Typically arithmetic operations, as well as a the `LOAD` function, alter the `accumulator`.
  
* **_instruction_ptr** - Index of the next instruction to be executed.

  Branching instructions, such as `JUMP`, `JIZERO`, `JSINEG` or `RETURN` change `_instruction_ptr`, to transfer control/execution to a different part of the CESIL program.

  **Note:** When altering `_instruction_ptr` within a CESIL instruction, the `_branch` flag should be set to `True`; this prevents the `run()` loop from simply executing the next instruction it was going to and causes it to transfer execution to the now-current value of `_instruction_ptr`.

* **_data_ptr** - Index of the current data value.
* **_stack** - The internal stack (as a Python list); available in "Plus" mode.

Additionally there are two flags that control the flow of program execution, and these should be set/unset within the Python implementation of a CESIL instruction according to what that instruction is intended to do:

* **_halt** - If set (`True`), the CESIL program will terminate upon completion of the current instruction.

* **_branch** - if set (`True`), then `_instruction_ptr` will NOT be incremented, and control will transfer to the  current line of code indicated by `_instruction_ptr` when the current CESIL instruction completes.

## Running the CESIL Program (Executing Instructions)
The `run()` loop is relatively simple.  It steps through the items in the CESIL program, one `CodeLine` at a time, and invokes the function provided by the function pointer in the `_instructions` dictionary, using `CodeLine.instruction` as the lookup key:

* The invoked function performs its operations on the state of the CESIL environment, then control returns to the `run()` loop.

* The value of the `accumulator` is checked for overflow; and an exception raised if necessary.

* The `_halt` flag is checked, and if set the program is terminated (exits the `run()` loop).

* The `_branch flag` is checked; if unset (`False`) then `_instruction_ptr` is incremented - and if set (`True`) it is NOT incremented (to observe the behavior of a branching instruction and what it has done to the `_instruction_ptr`).

* The `run()` loop continues with whatever line of code is now indicated by the `_instruction_ptr`.

## Prototypes

The prototypes/ folder contains the source code for my **earlier**, experimental, implementations of CESIL in Python:

* [prototypes/CESIL.py](https://github.com/idunmore/CESIL/blob/master/prototypes/CESIL.py)

  More of an exploratory implementation, which doesn't follow any particular Python coding convention or standard - so, for example, long lines are common (and artificially shorten the apparent [SLOC](https://en.wikipedia.org/wiki/Source_lines_of_code) for the implementation).  There's no command-line; so running code requires changing the source to point to the file to be executed.  It is largely monolithic, with just one class for the CESIL interpreter and another to represent a line of code.   It's not particularly "Pythonic" (doesn't necessarily do things in a way that it is idiomatic to general Python code).  Really just a quick-and-dirty test-bed for the approach and some logic.

* [prototypes/CESILPlus.py](https://github.com/idunmore/CESIL/blob/master/prototypes/CESILPlus.py)

    This adds a proper command line, allowing CESIL code to be run from the console, [optional "extension" instructions](https://github.com/idunmore/CESIL#cesil--cesil-plus), and a simple "debugger" - which lets yo see the overall state of the CESIL execution environment, including variable values and STACK contents, as code runs.
  
  Multiple classes are now used to represent lines of code (`CodeLine`), the overall CESIL Program (`Program`) - including code, variables, labels and data, as well as the execution state of the CESIL environment (`State`).

  Line lengths are now limited, and an overall more "Pythonic" approach is taken to the implementation.

* [prototypes/CESILPy.py](https://github.com/idunmore/CESIL/blob/master/prototypes/CESILPy.py)

  This is largely a restructuring of the above [CESILPlus.py](https://github.com/idunmore/CESIL/blob/master/prototypes/CESILPlus.py) implementation.  It moves the `Program` and `State` data back into the main CESIL class, since they were just groups of variables anyway.  Other features and functions remain the same.

  Some adjustments to properly observe the PEP8 conventions were made, some functions/methods were simplified (or made "less clever") or, again, my more "Pythonic".

### Prototype Operation
While the features, and details, of these three versions vary, as do the coding standards/style they observe, they all use a similar approach to **executing** CESIL code.  All of them read the code from a file, then validate and parse it into an ordered list of `CodeLine` instances.  Each `CodeLine` represents one line of CESIL Code, which can include a label and instruction and an operand (not all are present for all lines of code).

#### Executing CESIL Code
Executing the code, in the prototypes, involves moving an "instruction pointer" through the `CodeLine` list, one line at a time, and uses a large `if/elif/else` block to identify each CESIL instruction and executes the necessary Python code to implement that instruction's behavior (e.g., arithmetic, looping, conditional branching etc.)

This is a "simple" or, at least, *easily readable,* way to implement the execution process (the `run()` method).  For the 14 instructions that comprise the CESIL language, it's reasonably manageable - taking a total of 45 lines.  However, the overall structure isn't very extensible; the `run()` method would rapidly become unwieldy if you added additional "extension" instructions.

## Notice to Copyright Holders
Attempts to identify and/or contact current copyright holders for assets such as the "[CESIL Reference Card](https://github.com/idunmore/CESIL/blob/master/doc/CESIL%20Reference%20Card.pdf)" and the [CESIL "Coding Sheet"](https://github.com/idunmore/CESIL/blob/master/doc/CESIL%20Coding%20Sheet%20%28Facsimilie%29.pdf) (reproduced from scratch as a visual/content facsimilie of the original - including original copyright notice) were unsuccessful.

I believe my usage/recreation of these assets falls under fair-use, for non-profit educational and/or documentary/editorial purposes.

However, if said copyright holders have *any* issue with their reproduction here, I will be happy to remove these assets, modify their presentation, and/or transfer ownership (including the CESIL.org domain), at their behest.

*No legal/formal request/demand needed, just let me know.*  
