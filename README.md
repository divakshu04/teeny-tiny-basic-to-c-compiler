# 🧠 Teeny Tiny BASIC to C Compiler

This project implements a simple compiler that translates a subset of BASIC language code into equivalent C code. It features a graphical user interface (GUI) built with **PyQt5**, allowing users to input BASIC code, view the generated C output, and execute the compiled C program in a separate console window.

---

## 🚀 Features

- **BASIC to C Conversion**: Translates common BASIC statements and expressions into C.
- **GUI Interface**: PyQt5-based application for interactive usage.
- **Lexical Analysis**: Converts BASIC code into tokens.
- **Parsing**: Builds an Abstract Syntax Tree (AST) from tokens.
- **Code Generation**: Walks the AST to generate C code.
- **External Execution**: Compiles the C code using GCC and runs it in a terminal for I/O.
- **Automatic Cleanup**: Deletes temporary files after execution.

---

## 🛠️ Installation

### Prerequisites

Ensure the following are installed on your system:

- **Python 3.x**

```bash
python --version
```

If not, download from [python.org](https://www.python.org/).

- **PyQt5**

```bash
pip install PyQt5
```

- **GCC (GNU Compiler Collection)**

**Windows**:  
Install [MinGW-w64](https://www.mingw-w64.org/) and add the `mingw64/bin` directory to your PATH.

**macOS**:  
Install Xcode command line tools:

```bash
xcode-select --install
```

**Linux (Ubuntu/Debian)**:

```bash
sudo apt update
sudo apt install build-essential
```

---

## 📁 Project Setup

1. Clone this repository or download the files manually.
2. Ensure all required `.py` files are in the same directory:
   - `tokens.py`
   - `lexer.py`
   - `astt.py`
   - `parser.py`
   - `code_generator.py`
   - `main.py`
   - `gui.py`

3. Verify GCC is in your PATH:

```bash
gcc --version
```

If not found, check your compiler installation.

---

## 🚦 Usage

### Launching the GUI

Navigate to your project folder:

```bash
cd path/to/teeny-tiny-compiler
```

Run the GUI:

```bash
python gui.py
```

### How to Use

1. **Enter BASIC Code**: Type in the left-side editor.
2. **Convert to C**: Click the "Convert to C" button.
3. **Run Code**: Click the "Run Code" button to compile and execute.

> 🔔 If GCC compiles successfully, a new terminal window (on Windows) or the same terminal (on macOS/Linux) will handle the input/output of the program.

---

## 📂 Project Structure

| File               | Purpose                                                              |
|--------------------|----------------------------------------------------------------------|
| `tokens.py`        | Defines token types for lexical analysis                             |
| `lexer.py`         | Scans BASIC source and produces tokens                               |
| `astt.py`          | Defines AST nodes used for syntax parsing                            |
| `parser.py`        | Converts tokens to an AST structure                                  |
| `code_generator.py`| Traverses AST and generates equivalent C code                        |
| `main.py`          | Core compiler pipeline (lexer → parser → generator)                  |
| `gui.py`           | PyQt5 GUI for code input, conversion, and execution                  |

---

## 🧠 Compiler Workflow

1. **Lexical Analysis**: BASIC source is tokenized.
2. **Parsing**: Tokens are parsed into an AST.
3. **Code Generation**: AST is converted into C code.
4. **Compilation**: C code is compiled via GCC.
5. **Execution**: Executable runs in terminal for input/output.

---

## ⚠️ Limitations & Future Enhancements

- Currently supports only a **subset of BASIC**.
- Error messages are **minimal and could be improved**.
- Generated C code is basic and **not optimized**.
- External terminal launching is **more robust on Windows** than Linux/macOS.
- Future work could include:
  - Float and array support
  - Function and procedure support
  - Improved cross-platform compatibility
  - Enhanced error diagnostics

---
