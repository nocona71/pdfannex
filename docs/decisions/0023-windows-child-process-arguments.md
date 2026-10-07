# 0023 Quote Windows child-process arguments

- Context: the PowerShell bootstrap used by the CLI decodes a structured request, then starts a child process through `System.Diagnostics.ProcessStartInfo`. Its `Arguments` property accepts one command-line string, so individually wrapping arguments in quotes does not preserve all valid Windows arguments.
- Decision: quote each child argument according to Windows command-line parsing rules before joining them into `ProcessStartInfo.Arguments`. Keep the outer PowerShell bootstrap encoded with `-EncodedCommand`; do not pass either command layer through shell-interpreted interpolated text.
- Consequences: paths containing spaces and literal shell metacharacters remain single arguments. Windows CI tests exercise lock replacement and resolver invocation; test failures include captured stdout and stderr to make future process errors diagnosable.
