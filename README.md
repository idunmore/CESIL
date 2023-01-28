# CESIL

A [CESIL](https://en.wikipedia.org/wiki/CESIL) interpreter written in Python, intended as a "Language Preservation" project.

CESIL is the Computer Education in Schools Instruction Language.  It was developed as an introductory instructional language, targeted at British secondary school students (ages 11 to 16).  It was developed by [International Computers Limited](https://en.wikipedia.org/wiki/International_Computers_Limited) ([ICL](https://en.wikipedia.org/wiki/International_Computers_Limited)), a sort of "British version of IBM", as part of the "Computer Education in Schools" (CES) project, and was introduced in 1974.

## CESIL "Plus"
In addition to the original, standard, CESIL instruction set, this version adds some simple language extensions.  

There are two modes of operation:

* **Standard** - Default mode; matches the original implementation of the CESIL language.
* **Plus** - Optional; adds instructions for a stack, subroutines and modulo division.

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
    
        "Plus" language extensions add a STACK and SUBROUTINE support to the    
        language, enabled with the -p | --plus options. Extensions are DISABLED    
        by default.
    
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
      -s, --source [t|text|c|card] Text or punched Card input. [default: text]    
      -d, --debug [0|1|2|3|4] Debug mode/verbosity level. [default: 0]    
      -p, --plus Enables "plus" mode language extensions.    
      --version Show the version and exit.    
      --help Show this message and exit.

### Notice to Copyright Holders:
Attempts to identify and/or contact current copyright holders for assets such as the "[CESIL Reference Card](https://github.com/idunmore/CESIL/blob/master/doc/CESIL%20Reference%20Card.pdf)" and the [CESIL "Coding Sheet"](https://github.com/idunmore/CESIL/blob/master/doc/CESIL%20Coding%20Sheet%20%28Facsimilie%29.pdf) (reproduced from scratch as a visual/content facsimilie of the original - including original copyright notice) were unsuccessful.

I believe my usage/recreation of these assets falls under fair-use, for non-profit educational and/or documentary/editorial purposes.

However, if said copyright holders have *any* issue with their reproduction here, I will be happy to remove these assets, modify their presentation, and/or transfer ownership (including the CESIL.org domain), at their behest.

*No legal/formal request/demand needed, just let me know.*  
