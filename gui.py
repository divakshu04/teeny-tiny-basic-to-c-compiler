import sys
import os
import tempfile
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton,
    QLabel, QHBoxLayout, QMessageBox, QSplitter, QSizePolicy
)
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, QProcess, QTimer

# Assuming main.py is in the same directory and contains compile_basic_to_c
try:
    from main import compile_basic_to_c
except ImportError:
    QMessageBox.critical(None, "Import Error", "Could not import 'compile_basic_to_c' from main.py. "
                                                 "Please ensure main.py is in the same directory.")
    sys.exit(1)


class CompilerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.has_gcc = self.check_gcc_installed()  # Check for GCC installation
        self.init_ui()
        
        self.last_c_code = ""  # Stores the last successfully converted C code

        # Separate QProcess objects for compilation and execution
        self.gcc_process = None
        self.exec_process = None 

        # Store paths for cleanup. These will be in the script's directory.
        self.current_c_file_path = None
        self.current_exe_path = None

    def init_ui(self):
        """Initializes the graphical user interface elements and their layout."""
        self.setWindowTitle("Teeny Tiny BASIC to C Compiler")
        self.setGeometry(200, 100, 1200, 800)  # Set initial window size

        # Enhanced modern styling using CSS-like syntax
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f9fc; /* Light gray-blue background */
                font-family: 'Arial', 'Segoe UI', sans-serif; /* Modern font stack */
                color: #333; /* Dark gray text color */
            }
            QLabel#heading { /* Specific styling for the heading label */
                background-color: #4a90e2; /* Bright blue for the header */
                color: white;
                padding: 15px;
                border-bottom-left-radius: 10px; /* Rounded bottom corners for header */
                border-bottom-right-radius: 10px;
                margin-bottom: 10px;
                font-weight: bold;
                letter-spacing: 0.5px; /* Slightly spaced letters for heading */
                text-transform: uppercase; /* Uppercase for a modern feel */
                font-size: 24px; /* Larger font size for the heading */
            }
            QTextEdit {
                border: 1px solid #ccc; /* Lighter gray border */
                border-radius: 10px; /* More rounded corners for text editors */
                padding: 10px; /* Increased padding inside text editors */
                background-color: #ffffff; /* White background for editors */
            }
            QTextEdit:focus { /* Style when a text editor is focused */
                border: 1px solid #4a90e2; /* Blue border on focus */
            }
            QPushButton {
                padding: 12px 20px; /* More padding for buttons */
                border: none;
                border-radius: 10px; /* More rounded corners for buttons */
                font-weight: bold;
                letter-spacing: 0.5px;
                font-size: 14px; /* Slightly larger font for buttons */
            }
            QPushButton#convertButton { /* Styling for the Convert button */
                background-color: #5cb85c; /* Green */
                color: white;
            }
            QPushButton#convertButton:hover { /* Hover effect for Convert button */
                background-color: #4cae4c; /* Darker green on hover */
            }
            QPushButton#runButton { /* Styling for the Run button */
                background-color: #d9534f; /* Red */
                color: white;
            }
            QPushButton#runButton:hover { /* Hover effect for Run button */
                background-color: #c9302c; /* Darker red on hover */
            }
            QPushButton:disabled { /* Style for disabled buttons */
                background-color: #cccccc;
                color: #666666;
            }
            QSplitter::handle { /* Styling for the splitter handles */
                background-color: #e0e0e0; /* Light gray handle */
                width: 8px;
                border-radius: 4px;
            }
            QSplitter::handle:hover { /* Hover effect for splitter handles */
                background-color: #b0b0b0; /* Darker gray on hover */
            }
        """)

        title_font = QFont("Arial", 16, QFont.Bold)  # Font for the main heading
        editor_font = QFont("Consolas", 12)  # Monospaced font for code editors

        self.heading = QLabel("Teeny Tiny BASIC to C Compiler")
        self.heading.setObjectName("heading")  # Assign object name for specific CSS targeting
        self.heading.setAlignment(Qt.AlignCenter)
        self.heading.setFont(title_font)
        self.heading.setFixedHeight(60)  # Set fixed height for the heading

        # BASIC Input Editor
        self.basic_input = QTextEdit()
        self.basic_input.setFont(editor_font)
        self.basic_input.setPlaceholderText("Enter your BASIC code here...")
        self.basic_input.setLineWrapMode(QTextEdit.NoWrap)  # Disable word wrap for code readability

        # C Output Editor (Read-only)
        self.c_output = QTextEdit()
        self.c_output.setFont(editor_font)
        self.c_output.setReadOnly(True)  # C output is not editable by the user
        self.c_output.setPlaceholderText("C code output will appear here...")
        self.c_output.setLineWrapMode(QTextEdit.NoWrap)  # Disable word wrap for code readability

        # Terminal Output (for Compilation messages only in this version)
        self.terminal_output = QTextEdit()
        self.terminal_output.setFont(editor_font)
        self.terminal_output.setPlaceholderText("Compilation messages (GCC output) will appear here. Program I/O will open in a separate window.")
        self.terminal_output.setReadOnly(True)  # Make this read-only as user input goes to external terminal now
        self.terminal_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Convert Button
        self.convert_btn = QPushButton("Convert to C")
        self.convert_btn.setObjectName("convertButton")  # Assign object name for specific CSS targeting
        self.convert_btn.setFont(QFont("Arial", 13))
        self.convert_btn.clicked.connect(self.convert_code)

        # Run Button
        self.run_btn = QPushButton("Run Code")
        self.run_btn.setObjectName("runButton")  # Assign object name for specific CSS targeting
        self.run_btn.setFont(QFont("Arial", 13))
        self.run_btn.clicked.connect(self.run_code)
        self.run_btn.setEnabled(False)  # Disable run button initially if GCC not found or no code converted

        # Main Vertical Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)  # Outer margins
        main_layout.setSpacing(15)  # Spacing between widgets
        main_layout.addWidget(self.heading)

        # Horizontal splitter for BASIC input and the right panel (C output + Terminal)
        code_splitter = QSplitter(Qt.Horizontal)
        code_splitter.addWidget(self.basic_input)  # Left side: BASIC input

        # Vertical splitter for C output and Terminal output on the right side
        right_panel_splitter = QSplitter(Qt.Vertical)
        right_panel_splitter.addWidget(self.c_output)
        right_panel_splitter.addWidget(self.terminal_output)
        # Set initial sizes for the C output and terminal (e.g., C output 60%, terminal 40%)
        right_panel_splitter.setSizes([int(self.height() * 0.6), int(self.height() * 0.4)])
        
        code_splitter.addWidget(right_panel_splitter)  # Right side: C output and Terminal
        # Set initial sizes for the BASIC input and the right panel (e.g., BASIC 40%, right panel 60%)
        code_splitter.setSizes([int(self.width() * 0.4), int(self.width() * 0.6)])
        
        main_layout.addWidget(code_splitter, 1)  # Make splitter expand with window resize

        # Horizontal layout for buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)  # Pushes buttons to the center-right
        btn_layout.addWidget(self.convert_btn)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        if not self.has_gcc:
            QMessageBox.warning(self, "Compiler Missing", 
                                 "GCC compiler not found. You won't be able to run C code.\n"
                                 "Please install GCC and ensure it's in your system's PATH to enable code execution.")

    def check_gcc_installed(self):
        """Check if GCC is available in the system PATH"""
        process = QProcess()
        process.start("gcc", ["--version"])
        is_finished = process.waitForFinished(2000)
        exit_code = process.exitCode()
        
        if is_finished and exit_code == 0:
            return True
        else:
            return False

    def append_to_terminal(self, text):
        """Appends text to the terminal output area and ensures the cursor is at the end."""
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.terminal_output.setTextCursor(cursor)
        self.terminal_output.ensureCursorVisible()

    def convert_code(self):
        """Converts BASIC code to C code and displays it."""
        basic_code = self.basic_input.toPlainText().strip()
        if not basic_code:
            QMessageBox.warning(self, "Input Error", "Please enter BASIC code to convert.")
            return

        self.c_output.clear()  # Clear previous C output
        self.terminal_output.clear()  # Clear terminal
        self.append_to_terminal("Attempting to convert BASIC to C...\n")

        try:
            from main import compile_basic_to_c
            c_code = compile_basic_to_c(basic_code)
            self.c_output.setPlainText(c_code)
            self.last_c_code = c_code  # Store for potential execution
            self.run_btn.setEnabled(self.has_gcc and bool(self.last_c_code))  # Enable run button only if GCC is available and code exists
            self.append_to_terminal("BASIC to C conversion successful.\n")
        except Exception as e:
            self.c_output.clear()  # Clear C output on error
            error_message = f"Conversion failed during BASIC to C: {e}\n"
            self.append_to_terminal(error_message)
            QMessageBox.critical(self, "Conversion Error", error_message)
            self.run_btn.setEnabled(False)  # Disable run button on conversion failure

    def run_code(self):
        """Initiates the compilation of the C code and then, if successful, executes the compiled program in a separate console window."""
        if not self.last_c_code:
            QMessageBox.warning(self, "Run Error", "Please convert BASIC code to C first.")
            return
        if not self.has_gcc:
            QMessageBox.critical(self, "Run Error", "GCC compiler not found. Cannot run C code.")
            return

        self.terminal_output.clear()  # Clear previous terminal output
        self.append_to_terminal("Starting C compilation and execution...\n")

        # Define paths in the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.current_c_file_path = os.path.join(script_dir, "output.c")
        self.current_exe_path = os.path.join(script_dir, "output.exe" if os.name == 'nt' else "output.out")

        # Write the C code to the designated file
        try:
            with open(self.current_c_file_path, 'w') as f:
                f.write(self.last_c_code)
            self.append_to_terminal(f"C source saved to: {self.current_c_file_path}\n")
        except IOError as e:
            self.append_to_terminal(f"Error writing C source file: {e}\n")
            QMessageBox.critical(self, "File Write Error", f"Could not write C source file: {e}")
            return

        # --- Set up QProcess for GCC Compilation ---
        self.gcc_process = QProcess(self)
        self.gcc_process.setProgram("gcc")
        self.gcc_process.setArguments([self.current_c_file_path, "-o", self.current_exe_path])
        
        # Connect signals for compilation output (stdout and stderr)
        self.gcc_process.readyReadStandardOutput.connect(self.read_compile_stdout)
        self.gcc_process.readyReadStandardError.connect(self.read_compile_stderr)
        self.gcc_process.finished.connect(self.handle_compile_finished)

        # Start the compilation process
        self.append_to_terminal(f"Compiling C code with GCC...\n")
        self.gcc_process.start()
        
    def read_compile_stdout(self):
        """Reads and appends stdout from the GCC compilation process to the terminal."""
        output = self.gcc_process.readAllStandardOutput().data().decode(errors='ignore')
        self.append_to_terminal(output)

    def read_compile_stderr(self):
        """Reads and appends stderr from the GCC compilation process to the terminal."""
        error = self.gcc_process.readAllStandardError().data().decode(errors='ignore')
        self.append_to_terminal(error)

    def handle_compile_finished(self, exit_code, exit_status):
        """Callback when GCC compilation process finishes."""
        if exit_code != 0:  
            self.append_to_terminal(f"C Compilation Failed (Exit Code: {exit_code}). See above for errors.\n")
            QMessageBox.critical(self, "Compilation Error", f"C Code compilation failed with exit code {exit_code}. Check terminal output for details.")
            return
        
        # Check if the executable file actually exists after compilation
        if not os.path.exists(self.current_exe_path):
            self.append_to_terminal(f"Error: Compiled executable not found at {self.current_exe_path}.\n")
            QMessageBox.critical(self, "Execution Error", "Compiled executable not found. This might indicate a linker error or an issue with GCC installation.")
            return

        self.append_to_terminal(f"C Compilation successful. Executable at: {self.current_exe_path}\n")
        self.append_to_terminal("Launching program in separate console...\n")
        
        # --- Launch Compiled C Code in a separate console ---
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['start', 'cmd', '/k', self.current_exe_path], shell=True)
            else:  # Linux / macOS
                subprocess.Popen([self.current_exe_path])
            
        except Exception as e:
            self.append_to_terminal(f"Error launching executable: {e}\n")
            QMessageBox.critical(self, "Execution Error", f"Could not launch executable: {e}")
            
    def cleanup_temp_files(self):
        """Removes the temporary C source and executable files."""
        files_to_remove = []
        if self.current_c_file_path and os.path.exists(self.current_c_file_path):
            files_to_remove.append(self.current_c_file_path)
        if self.current_exe_path and os.path.exists(self.current_exe_path):
            files_to_remove.append(self.current_exe_path)

        for f_path in files_to_remove:
            try:
                os.unlink(f_path)
            except OSError as e:
                print(f"Warning: Could not remove file {f_path}: {e}")

        # Reset paths after cleanup attempt
        self.current_c_file_path = None
        self.current_exe_path = None

    def set_buttons_enabled(self, enabled):
        """Enables or disables the Convert and Run buttons."""
        self.convert_btn.setEnabled(enabled)
        self.run_btn.setEnabled(enabled and self.has_gcc and bool(self.last_c_code))

# Main application entry point
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = CompilerGUI()
    gui.show()
    sys.exit(app.exec_())
