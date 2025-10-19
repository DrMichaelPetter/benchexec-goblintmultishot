"""
BenchExec tool-info module for MuVal.

MuVal is a verification tool based on modal μ-calculus for C programs.
"""

import benchexec.result as result
import benchexec.tools.template


class Tool(benchexec.tools.template.BaseTool2):
    """Tool-info for MuVal"""

    REQUIRED_PATHS = ["solver", "coar", "llvm2kittel", "Ptr2Arr"]

    def executable(self, tool_locator):
        return tool_locator.find_executable("solver", subdir="bin")

    def name(self):
        return "MuVal"

    def version(self, executable):
        return self._version_from_tool(executable, arg="--version")

    def cmdline(self, executable, options, task, rlimits):
        """
        Compose command line for MuVal.
        
        Args:
            executable: Path to solver script
            options: Tool options from benchmark definition
            task: Task to verify (includes property file and input file)
            rlimits: Resource limits
        """
        cmd = [executable]
        
        # Add property file
        if task.property_file:
            cmd.append(f"--property={task.property_file}")
        
        # Add timeout if specified
        if rlimits.cputime:
            cmd.append(f"--timeout={int(rlimits.cputime)}")
        
        # Add additional options from benchmark definition
        cmd.extend(options)
        
        # Add input file
        cmd.append(task.single_input_file)
        
        return cmd

    def determine_result(self, run):
        """
        Parse tool output to determine verification result.
        
        Returns:
            BenchExec result status
        """
        if run.exit_code.value != 0:
            return result.RESULT_ERROR
        
        output = "\n".join(run.output)
        
        # Parse output for verdicts
        for line in run.output:
            line = line.strip()
            
            # Termination verdicts
            if line == "YES":
                return result.RESULT_TRUE_PROP
            elif line == "NO":
                return result.RESULT_FALSE_TERMINATION
            
            # Reachability verdicts
            elif line == "TRUE":
                return result.RESULT_TRUE_PROP
            elif line == "FALSE":
                return result.RESULT_FALSE_REACH
            
            # Unknown/Timeout
            elif line == "UNKNOWN":
                return result.RESULT_UNKNOWN
            elif line == "TIMEOUT":
                return result.RESULT_TIMEOUT
        
        # No clear verdict found
        return result.RESULT_UNKNOWN

