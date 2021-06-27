import os
import sys
import docx2python


# Program to convert MS-Word pastes into a less
# annoying text file layout.

# Certain unicode symbols can be annoying to work with.
TRANSLATION_TABLE = [
    ("“", "\""), ("”", "\""), ("„", "\""),
    ("’", "'"), ("–", "-"), ("…", "..."),
    ("•", "*"),
]


def write_output(lines: list, out_file_name: str) -> None:
    if os.path.exists(out_file_name):
        print("Already exists!")
        return

    with open(out_file_name, "w") as f:
        was_whitespace = False
        in_preformatted_block = False

        for line in lines:
            # Handle HTML <pre> blocks
            if "<pre>" in line or in_preformatted_block:
                in_preformatted_block = True

            if in_preformatted_block:
                f.write(line)
                if "</pre>" in line:
                    in_preformatted_block = False
                    was_whitespace = False

                continue

            # Convert unicode symbols
            for sym, rep in TRANSLATION_TABLE:
                line = line.replace(sym, rep)

            # Header
            if line.startswith("#"):
                was_whitespace = False
                f.write(line + "\n")

            # Whitespace
            elif not line.strip():
                if not was_whitespace:
                    was_whitespace = True
                    f.write("\n")

            # Normal text
            else:
                was_whitespace = False
                buffer = str()
                for word in line.split():
                    if len(buffer) + len(word) + 1 < 80:
                        buffer += (" " + word if buffer else word)

                    else:
                        f.write(buffer + "\n")
                        buffer = word

                f.write(buffer + "\n\n")

        print("OK")


def process_file(input_name: str) -> None:
    output_name = input_name.rsplit(".", 1)[0] + ".md"
    lower_file_name = input_name.lower().strip()

    if lower_file_name.endswith(".txt"):
        print(f"Reading .txt file: \"{input_name}\"... ", end="")
        with open(input_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
            write_output(lines, output_name)

    # docx files need some more handling
    elif lower_file_name.endswith(".docx"):
        print(f"Reading .docx file: \"{input_name}\"... ", end="")
        text = docx2python.docx2python(input_name).text.replace("--", "*")
        lines = [e + "\n" for e in text.splitlines() if e]
        write_output(lines, output_name)


def main() -> None:
    print("Flesh-Network Blog Post Indenting Tool (2021)")
    print("-> Convert .txt and .docx files into properly formatted blog posts!\n")
    if len(sys.argv) != 2:
        print("Please supply a file name!")
        sys.exit(-1)

    input_name = sys.argv[1]
    if os.path.isdir(input_name):
        print(f"Converting directory \"{input_name}\"...")
        entries = os.listdir(input_name)
        files = filter(lambda e: e.endswith(".docx") or e.endswith(".txt"), entries)

        for file in files:
            path = os.path.join(input_name, file)
            process_file(path)

    else:
        process_file(input_name)


if __name__ == "__main__":
    main()
