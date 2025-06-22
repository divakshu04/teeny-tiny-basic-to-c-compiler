from lexer import Lexer
from parser import Parser
from code_generator import CodeGenerator


def compile_basic_to_c(basic_code):
    # Step 1: Lexical Analysis
    lexer = Lexer(basic_code)
    tokens = lexer.tokenize()

    # Step 2: Parsing to AST
    parser = Parser(tokens)
    ast = parser.parse()

    # Step 3: Code Generation
    generator = CodeGenerator()
    c_code = generator.visit(ast)

    return c_code


def main():
    print("--- BASIC to C Compiler ---")
    input_file = input("Enter the BASIC file path: ").strip()

    try:
        with open(input_file, 'r') as f:
            basic_code = f.read()

        c_code = compile_basic_to_c(basic_code)

        output_file = input_file.rsplit('.', 1)[0] + ".c"
        with open(output_file, 'w') as f:
            f.write(c_code)

        print(f"\nC code generated and saved to: {output_file}")

    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"Compilation failed: {e}")


if __name__ == "__main__":
    main()
