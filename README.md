# CESIL

A [CESIL](https://en.wikipedia.org/wiki/CESIL) interpreter written in Python, intended as a "Language Preservation" project.

CESIL is the Computer Education in Schools Instruction Language.  It was developed as an introductory instructional language, targeted at British secondary school students (ages 11 to 16).  It was developed by [International Computers Limited](https://en.wikipedia.org/wiki/International_Computers_Limited) ([ICL](https://en.wikipedia.org/wiki/International_Computers_Limited)), a sort of "British version of IBM", as part of the "Computer Education in Schools" (CES) project, and was introduced in 1974.

## CESIL & CESIL "Plus"

In addition to the original, standard, CESIL instruction set, this version implements what I call CESIL "Plus".  This is an extension of the original CESIL language.  It is not in "official" nor "standard" in anyway.  It consists of seven new instructions (50% of the original total), which incorporate new features, that my CESIL implementation (optionally) adds to the official language.

There are two modes of operation:

-   **Standard**  - Default mode; matches the original implementation of the CESIL language.
-   **Plus**  - Optional; adds instructions for a stack, subroutines and modulo division.

"Plus" mode is enabled by use of the `-p` or `--plus` options; the default behavior only observes the original CESIL instructions.  In "Plus" mode, the following additional features/instructions are available:

- A **stack** capability, and the instructions to support its use: `PUSH` and `POP` (see "[Stack_test.ces](https://github.com/idunmore/CESIL/blob/master/examples/Stack_test.ces)").

 - **Subroutine** support; expands the simple branch/jump capabilities of CESIL with the ability to jump to, or "call" a new point of execution, and then *return* to the original point of execution (see "[Sub_test.ces](https://github.com/idunmore/CESIL/blob/master/examples/Sub_test.ces)").

  Adds the instructions: `JUMPSR`, `JSIZERO`, `JSINEG` and `RETURN`.

 - **Modulo division**; a new `MODULO` instruction that leaves the remainder of a division in the ACCUMULATOR.
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


## Notice to Copyright Holders
Attempts to identify and/or contact current copyright holders for assets such as the "[CESIL Reference Card](https://github.com/idunmore/CESIL/blob/master/doc/CESIL%20Reference%20Card.pdf)" and the [CESIL "Coding Sheet"](https://github.com/idunmore/CESIL/blob/master/doc/CESIL%20Coding%20Sheet%20%28Facsimilie%29.pdf) (reproduced from scratch as a visual/content facsimilie of the original - including original copyright notice) were unsuccessful.

I believe my usage/recreation of these assets falls under fair-use, for non-profit educational and/or documentary/editorial purposes.

However, if said copyright holders have *any* issue with their reproduction here, I will be happy to remove these assets, modify their presentation, and/or transfer ownership (including the CESIL.org domain), at their behest.

*No legal/formal request/demand needed, just let me know.*  
