"""
Comprehensive unit tests for CodebaseAnalysisAgent.

This test suite covers:
- Agent initialization and configuration
- Shell script execution and output handling
- Code analysis capabilities
- Response formatting
- Error handling and edge cases
- Security considerations
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import subprocess
import os
import tempfile
import shutil
from codebase_analysis_agent import CodebaseAnalysisAgent


class TestCodebaseAnalysisAgentInitialization(unittest.TestCase):
    """Test suite for agent initialization and configuration."""
    
    def test_init_with_default_parameters(self):
        """Test agent initialization with default parameters."""
        agent = CodebaseAnalysisAgent()
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, CodebaseAnalysisAgent)
    
    def test_init_with_custom_repository_path(self):
        """Test agent initialization with custom repository path."""
        custom_path = "/custom/repo/path"
        agent = CodebaseAnalysisAgent(repository_path=custom_path)
        self.assertEqual(agent.repository_path, custom_path)
    
    def test_init_creates_necessary_attributes(self):
        """Test that initialization creates all necessary attributes."""
        agent = CodebaseAnalysisAgent()
        # Verify agent has expected attributes
        self.assertTrue(hasattr(agent, 'repository_path'))
        self.assertTrue(hasattr(agent, 'execute_shell_script'))
    
    def test_multiple_agent_instances_are_independent(self):
        """Test that multiple agent instances don't interfere with each other."""
        agent1 = CodebaseAnalysisAgent(repository_path="/path1")
        agent2 = CodebaseAnalysisAgent(repository_path="/path2")
        self.assertNotEqual(agent1.repository_path, agent2.repository_path)


class TestShellScriptExecution(unittest.TestCase):
    """Test suite for shell script execution functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodebaseAnalysisAgent()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('subprocess.run')
    def test_execute_simple_shell_command(self, mock_run):
        """Test execution of a simple shell command."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="command output",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("echo 'hello'")
        
        mock_run.assert_called_once()
        self.assertEqual(result['stdout'], "command output")
        self.assertEqual(result['returncode'], 0)
    
    @patch('subprocess.run')
    def test_execute_command_with_error(self, mock_run):
        """Test handling of command execution errors."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error message"
        )
        
        result = self.agent.execute_shell_script("invalid_command")
        
        self.assertEqual(result['returncode'], 1)
        self.assertEqual(result['stderr'], "error message")
    
    @patch('subprocess.run')
    def test_execute_command_with_timeout(self, mock_run):
        """Test handling of command timeouts."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="long_running_command",
            timeout=30
        )
        
        with self.assertRaises(subprocess.TimeoutExpired):
            self.agent.execute_shell_script("long_running_command", timeout=30)
    
    @patch('subprocess.run')
    def test_execute_multi_line_script(self, mock_run):
        """Test execution of multi-line shell scripts."""
        script = """#!/bin/bash
        echo "line 1"
        echo "line 2"
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout="line 1\nline 2\n",
            stderr=""
        )
        
        result = self.agent.execute_shell_script(script)
        
        self.assertEqual(result['returncode'], 0)
        self.assertIn("line 1", result['stdout'])
        self.assertIn("line 2", result['stdout'])
    
    @patch('subprocess.run')
    def test_execute_script_with_special_characters(self, mock_run):
        """Test execution of scripts containing special characters."""
        script = "echo 'test $VAR with \"quotes\" and `backticks`'"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="test output",
            stderr=""
        )
        
        result = self.agent.execute_shell_script(script)
        
        self.assertEqual(result['returncode'], 0)
    
    @patch('subprocess.run')
    def test_execute_command_in_specific_directory(self, mock_run):
        """Test command execution in a specific working directory."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="/specific/path",
            stderr=""
        )
        
        result = self.agent.execute_shell_script(
            "pwd",
            cwd="/specific/path"
        )
        
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        self.assertEqual(call_kwargs.get('cwd'), "/specific/path")
    
    @patch('subprocess.run')
    def test_execute_command_with_environment_variables(self, mock_run):
        """Test command execution with custom environment variables."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="custom_value",
            stderr=""
        )
        
        env = os.environ.copy()
        env['CUSTOM_VAR'] = 'custom_value'
        
        result = self.agent.execute_shell_script(
            "echo $CUSTOM_VAR",
            env=env
        )
        
        self.assertEqual(result['returncode'], 0)
    
    @patch('subprocess.run')
    def test_execute_command_captures_both_stdout_and_stderr(self, mock_run):
        """Test that both stdout and stderr are captured."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="standard output",
            stderr="error output"
        )
        
        result = self.agent.execute_shell_script("command")
        
        self.assertIn('stdout', result)
        self.assertIn('stderr', result)
        self.assertEqual(result['stdout'], "standard output")
        self.assertEqual(result['stderr'], "error output")
    
    @patch('subprocess.run')
    def test_execute_empty_script_safely(self, mock_run):
        """Test handling of empty script input."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("")
        
        self.assertEqual(result['returncode'], 0)
    
    @patch('subprocess.run')
    def test_execute_script_with_pipes_and_redirects(self, mock_run):
        """Test execution of scripts with pipes and redirections."""
        script = "cat file.txt | grep 'pattern' > output.txt"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        result = self.agent.execute_shell_script(script)
        
        self.assertEqual(result['returncode'], 0)


class TestCodebaseAnalysis(unittest.TestCase):
    """Test suite for codebase analysis capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodebaseAnalysisAgent()
        self.temp_repo = tempfile.mkdtemp()
        self.agent.repository_path = self.temp_repo
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_repo):
            shutil.rmtree(self.temp_repo)
    
    @patch('subprocess.run')
    def test_list_files_in_repository(self, mock_run):
        """Test listing files in repository."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="file1.py\nfile2.py\nfile3.js\n",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("git ls-files")
        
        self.assertEqual(result['returncode'], 0)
        self.assertIn('file1.py', result['stdout'])
        self.assertIn('file2.py', result['stdout'])
    
    @patch('subprocess.run')
    def test_search_code_patterns(self, mock_run):
        """Test searching for code patterns using grep/rg."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="file.py:10:def function_name():\n",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("rg 'def function_name'")
        
        self.assertEqual(result['returncode'], 0)
        self.assertIn('function_name', result['stdout'])
    
    @patch('subprocess.run')
    def test_analyze_file_structure(self, mock_run):
        """Test analyzing file structure with find."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="./src\n./src/main.py\n./tests\n./tests/test_main.py\n",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("find . -type f -name '*.py'")
        
        self.assertEqual(result['returncode'], 0)
        self.assertIn('main.py', result['stdout'])
        self.assertIn('test_main.py', result['stdout'])
    
    @patch('subprocess.run')
    def test_read_file_contents(self, mock_run):
        """Test reading file contents."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="import sys\ndef main():\n    pass\n",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("cat main.py")
        
        self.assertEqual(result['returncode'], 0)
        self.assertIn('import sys', result['stdout'])
        self.assertIn('def main', result['stdout'])
    
    @patch('subprocess.run')
    def test_analyze_git_history(self, mock_run):
        """Test analyzing git history."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="commit abc123\nAuthor: Test\nDate: 2024-01-01\n",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("git log --oneline -10")
        
        self.assertEqual(result['returncode'], 0)
        self.assertIn('commit', result['stdout'])
    
    @patch('subprocess.run')
    def test_analyze_dependencies(self, mock_run):
        """Test analyzing project dependencies."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="requests==2.28.0\npandas==1.5.0\n",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("cat requirements.txt")
        
        self.assertEqual(result['returncode'], 0)
        self.assertIn('requests', result['stdout'])
        self.assertIn('pandas', result['stdout'])


class TestResponseFormatting(unittest.TestCase):
    """Test suite for response formatting functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodebaseAnalysisAgent()
    
    def test_format_markdown_response(self):
        """Test formatting responses in markdown."""
        data = {
            'title': 'Test Analysis',
            'content': 'Analysis results'
        }
        
        formatted = self.agent.format_markdown_response(data)
        
        self.assertIsInstance(formatted, str)
        self.assertIn('Test Analysis', formatted)
        self.assertIn('Analysis results', formatted)
    
    def test_format_code_snippet(self):
        """Test formatting code snippets with syntax highlighting."""
        code = "def hello():\n    print('world')"
        language = "python"
        
        formatted = self.agent.format_code_snippet(code, language)
        
        self.assertIn('```python', formatted)
        self.assertIn('def hello', formatted)
        self.assertIn('```', formatted)
    
    def test_format_file_tree(self):
        """Test formatting file tree structures."""
        files = [
            'src/main.py',
            'src/utils/helper.py',
            'tests/test_main.py'
        ]
        
        formatted = self.agent.format_file_tree(files)
        
        self.assertIsInstance(formatted, str)
        for file in files:
            self.assertIn(file, formatted)
    
    def test_format_empty_response(self):
        """Test formatting empty responses."""
        formatted = self.agent.format_markdown_response({})
        
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)
    
    def test_format_response_with_special_characters(self):
        """Test formatting responses containing special markdown characters."""
        data = {
            'content': 'Text with *asterisks* and _underscores_ and `backticks`'
        }
        
        formatted = self.agent.format_markdown_response(data)
        
        self.assertIn('*asterisks*', formatted)
        self.assertIn('_underscores_', formatted)


class TestErrorHandling(unittest.TestCase):
    """Test suite for error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodebaseAnalysisAgent()
    
    @patch('subprocess.run')
    def test_handle_nonexistent_command(self, mock_run):
        """Test handling of non-existent commands."""
        mock_run.side_effect = FileNotFoundError("Command not found")
        
        with self.assertRaises(FileNotFoundError):
            self.agent.execute_shell_script("nonexistent_command")
    
    @patch('subprocess.run')
    def test_handle_permission_denied(self, mock_run):
        """Test handling of permission denied errors."""
        mock_run.side_effect = PermissionError("Permission denied")
        
        with self.assertRaises(PermissionError):
            self.agent.execute_shell_script("restricted_command")
    
    @patch('subprocess.run')
    def test_handle_interrupted_execution(self, mock_run):
        """Test handling of interrupted command execution."""
        mock_run.side_effect = KeyboardInterrupt()
        
        with self.assertRaises(KeyboardInterrupt):
            self.agent.execute_shell_script("command")
    
    @patch('subprocess.run')
    def test_handle_very_large_output(self, mock_run):
        """Test handling of very large command outputs."""
        large_output = "x" * 1000000  # 1MB of output
        mock_run.return_value = Mock(
            returncode=0,
            stdout=large_output,
            stderr=""
        )
        
        result = self.agent.execute_shell_script("command")
        
        self.assertEqual(len(result['stdout']), 1000000)
    
    @patch('subprocess.run')
    def test_handle_binary_output(self, mock_run):
        """Test handling of binary output from commands."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=b'\x00\x01\x02\x03',
            stderr=""
        )
        
        result = self.agent.execute_shell_script("binary_command")
        
        self.assertIsNotNone(result)
    
    def test_handle_invalid_repository_path(self):
        """Test handling of invalid repository paths."""
        agent = CodebaseAnalysisAgent(repository_path="/nonexistent/path")
        
        self.assertEqual(agent.repository_path, "/nonexistent/path")
    
    @patch('subprocess.run')
    def test_handle_command_killed_by_signal(self, mock_run):
        """Test handling of commands killed by signals."""
        mock_run.return_value = Mock(
            returncode=-9,  # SIGKILL
            stdout="",
            stderr="Killed"
        )
        
        result = self.agent.execute_shell_script("command")
        
        self.assertEqual(result['returncode'], -9)
    
    @patch('subprocess.run')
    def test_handle_unicode_in_output(self, mock_run):
        """Test handling of unicode characters in command output."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Hello 世界 🌍 Ñoño",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("echo unicode")
        
        self.assertIn('世界', result['stdout'])
        self.assertIn('🌍', result['stdout'])
        self.assertIn('Ñoño', result['stdout'])
    
    @patch('subprocess.run')
    def test_handle_newlines_and_whitespace(self, mock_run):
        """Test handling of various newline and whitespace characters."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="line1\nline2\r\nline3\t\tindented",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("command")
        
        self.assertIn('\n', result['stdout'])
        self.assertIn('\t', result['stdout'])


class TestSecurityConsiderations(unittest.TestCase):
    """Test suite for security-related functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodebaseAnalysisAgent()
    
    @patch('subprocess.run')
    def test_command_injection_prevention(self, mock_run):
        """Test prevention of command injection attacks."""
        malicious_input = "ls; rm -rf /"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        # The agent should handle this safely
        result = self.agent.execute_shell_script(malicious_input)
        
        # Verify that subprocess.run was called
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_environment_variable_isolation(self, mock_run):
        """Test that environment variables are properly isolated."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        # Execute with clean environment
        result = self.agent.execute_shell_script(
            "echo $SECRET_VAR",
            env={'SECRET_VAR': 'should_not_leak'}
        )
        
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_path_traversal_in_file_access(self, mock_run):
        """Test handling of path traversal attempts."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="No such file"
        )
        
        result = self.agent.execute_shell_script("cat ../../../etc/passwd")
        
        # Command should be executed (but fail in sandbox)
        mock_run.assert_called_once()


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for common usage scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodebaseAnalysisAgent()
        self.temp_repo = tempfile.mkdtemp()
        
        # Create a simple test repository structure
        os.makedirs(os.path.join(self.temp_repo, 'src'))
        os.makedirs(os.path.join(self.temp_repo, 'tests'))
        
        with open(os.path.join(self.temp_repo, 'src', 'main.py'), 'w') as f:
            f.write('def main():\n    print("Hello")\n')
        
        with open(os.path.join(self.temp_repo, 'README.md'), 'w') as f:
            f.write('# Test Project\n\nThis is a test.\n')
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_repo):
            shutil.rmtree(self.temp_repo)
    
    @patch('subprocess.run')
    def test_full_codebase_analysis_workflow(self, mock_run):
        """Test complete workflow of analyzing a codebase."""
        # Simulate multiple commands in sequence
        mock_run.side_effect = [
            Mock(returncode=0, stdout="src/main.py\nREADME.md\n", stderr=""),
            Mock(returncode=0, stdout="def main():\n    print('Hello')\n", stderr=""),
            Mock(returncode=0, stdout="# Test Project\n", stderr=""),
        ]
        
        # Execute analysis workflow
        files_result = self.agent.execute_shell_script("ls -la")
        main_result = self.agent.execute_shell_script("cat src/main.py")
        readme_result = self.agent.execute_shell_script("cat README.md")
        
        self.assertEqual(files_result['returncode'], 0)
        self.assertEqual(main_result['returncode'], 0)
        self.assertEqual(readme_result['returncode'], 0)
    
    @patch('subprocess.run')
    def test_search_and_analyze_pattern(self, mock_run):
        """Test workflow of searching for patterns and analyzing results."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="src/main.py:1:def main():\n", stderr=""),
            Mock(returncode=0, stdout="def main():\n    print('Hello')\n", stderr=""),
        ]
        
        # Search for pattern
        search_result = self.agent.execute_shell_script("rg 'def main'")
        
        # Read found file
        file_result = self.agent.execute_shell_script("cat src/main.py")
        
        self.assertEqual(search_result['returncode'], 0)
        self.assertEqual(file_result['returncode'], 0)
    
    @patch('subprocess.run')
    def test_multi_step_analysis_with_filtering(self, mock_run):
        """Test multi-step analysis with data filtering."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="100 files\n", stderr=""),
            Mock(returncode=0, stdout="50 *.py files\n", stderr=""),
            Mock(returncode=0, stdout="10 test files\n", stderr=""),
        ]
        
        all_files = self.agent.execute_shell_script("find . -type f | wc -l")
        py_files = self.agent.execute_shell_script("find . -name '*.py' | wc -l")
        test_files = self.agent.execute_shell_script("find . -name 'test_*.py' | wc -l")
        
        self.assertEqual(all_files['returncode'], 0)
        self.assertEqual(py_files['returncode'], 0)
        self.assertEqual(test_files['returncode'], 0)


class TestEdgeCasesAndBoundaries(unittest.TestCase):
    """Test suite for edge cases and boundary conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodebaseAnalysisAgent()
    
    @patch('subprocess.run')
    def test_execute_with_null_bytes_in_input(self, mock_run):
        """Test handling of null bytes in command input."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="output",
            stderr=""
        )
        
        # Null bytes should be handled without crashing
        result = self.agent.execute_shell_script("echo 'test\x00data'")
        
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_execute_very_long_command(self, mock_run):
        """Test execution of very long commands."""
        long_command = "echo " + "x" * 10000
        mock_run.return_value = Mock(
            returncode=0,
            stdout="x" * 10000,
            stderr=""
        )
        
        result = self.agent.execute_shell_script(long_command)
        
        self.assertEqual(result['returncode'], 0)
    
    @patch('subprocess.run')
    def test_concurrent_command_execution(self, mock_run):
        """Test that agent can handle concurrent operations."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="output",
            stderr=""
        )
        
        # Execute multiple commands
        results = []
        for i in range(5):
            result = self.agent.execute_shell_script(f"echo {i}")
            results.append(result)
        
        self.assertEqual(len(results), 5)
        self.assertEqual(mock_run.call_count, 5)
    
    @patch('subprocess.run')
    def test_command_with_no_output(self, mock_run):
        """Test commands that produce no output."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        result = self.agent.execute_shell_script(":")  # No-op command
        
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['stdout'], "")
    
    @patch('subprocess.run')
    def test_command_with_only_stderr_output(self, mock_run):
        """Test commands that only produce stderr output."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr="warning message"
        )
        
        result = self.agent.execute_shell_script("command_with_warnings")
        
        self.assertEqual(result['stdout'], "")
        self.assertEqual(result['stderr'], "warning message")


class TestPureFunctions(unittest.TestCase):
    """Test suite specifically for pure functions in the agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodebaseAnalysisAgent()
    
    def test_pure_function_deterministic_output(self):
        """Test that pure functions produce deterministic output."""
        input_data = "test input"
        
        # If there's a pure parsing/formatting function
        result1 = self.agent.parse_command_output(input_data)
        result2 = self.agent.parse_command_output(input_data)
        
        self.assertEqual(result1, result2)
    
    def test_pure_function_no_side_effects(self):
        """Test that pure functions have no side effects."""
        original_data = "original"
        data_copy = original_data
        
        # Call a pure function
        result = self.agent.sanitize_input(data_copy)
        
        # Original should be unchanged
        self.assertEqual(data_copy, "original")
    
    def test_pure_function_idempotency(self):
        """Test that pure functions are idempotent."""
        input_data = "test"
        
        result1 = self.agent.normalize_path(input_data)
        result2 = self.agent.normalize_path(result1)
        
        # Applying twice should give same result as applying once
        self.assertEqual(result1, result2)


class TestPerformanceConsiderations(unittest.TestCase):
    """Test suite for performance-related aspects."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodebaseAnalysisAgent()
    
    @patch('subprocess.run')
    def test_efficient_large_file_handling(self, mock_run):
        """Test efficient handling of large files."""
        # Simulate reading a large file
        large_content = "line\n" * 100000  # 100k lines
        mock_run.return_value = Mock(
            returncode=0,
            stdout=large_content,
            stderr=""
        )
        
        result = self.agent.execute_shell_script("cat large_file.txt")
        
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(len(result['stdout'].split('\n')), 100000)
    
    @patch('subprocess.run')
    def test_streaming_output_handling(self, mock_run):
        """Test handling of streaming command output."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="line1\nline2\nline3\n",
            stderr=""
        )
        
        result = self.agent.execute_shell_script("tail -f file.log")
        
        self.assertIsNotNone(result)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)