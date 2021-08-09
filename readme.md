# A Python parser for TunerStudio INI files
 Example:

    from TsIniParser import TsIniParser
    
    parser = TsIniParser()
    parser.define('LAMBDA', True)
    parser.define('ALPHA_N', True)
    with  open(sys.argv[1], 'r') as  file:
    	tree = parser.parse(file)
    	# tree will contain the parsed INI file
    	# with any #if preprocessing directives applied

Note that this parser is less tolerant of format issues than TunerStudio:

 - Key-value pairs: the value must be comma delimited (TunerStudio
   tolerates spaces)
  - There must be a blank line at the end
   - Expression markers ("{", "}") and parentheses ("(", ")") must be balanced
   - All identifiers must be Java/C/C++ [identifers](https://docs.microsoft.com/en-us/cpp/c-language/c-identifiers?view=msvc-160) (no spaces, quotes etc.)

