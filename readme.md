# A Python parser for TunerStudio INI files
 Example:

    import sys
    from ts_ini_parser import TsIniParser, DataClassTransformer
    
    parser = TsIniParser()
    parser.define('LAMBDA', True)
    parser.define('ALPHA_N', True)
    with open(sys.argv[1], 'r') as  file:
      tree = parser.parse(file)
      # tree will contain the parsed INI file as a Lark Tree
      # object with any #if preprocessing directives applied
      #
      # The Lark tree conatins a lot of detail that most consumers
      # won't need. It's main appeal is that the tree elements can
      # be tied back to the file lines & columns
      #
      # Apply a predefined transform to convert the tree into
      # an idiomatic Python object tree
      dataclass = DataClassTransformer().transform(tree)

      injBatRates = dataclass['Constants'][6]['injBatRates']
      print(injBatRates.dim1d)

Note that this parser is less tolerant of format issues than TunerStudio:

 - Key-value pairs: the value must be comma delimited (TunerStudio
   tolerates spaces)
  - There must be a blank line at the end
   - Expression markers ("{", "}") and parentheses ("(", ")") must be balanced
   - All identifiers must be Java/C/C++ [identifers](https://docs.microsoft.com/en-us/cpp/c-language/c-identifiers?view=msvc-160) (no spaces, quotes etc.)

