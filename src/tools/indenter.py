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
                # Docx extraction artifact
                if line.strip() == "*-":
                    line = "---"

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


def process_md_file(input_name: str, out_file_name: str) -> None:
    print(f"Reading .md file: \"{input_name}\"... ", end="")
    with open(input_name, "r", encoding="utf-8", errors="replace") as f:
        lines = [e.strip() for e in f.readlines()]

    text = str()
    new_line = True
    for line in lines:
        if not line or any([line.startswith(c) for c in "*#"]):
            new_line = True
            text += "\n\n"

        if line:
            if new_line:
                new_line = False
            else:
                text += " "
            text += line

    print("OK")
    with open(out_file_name, "w", encoding="utf-8", errors="replace") as f:
        f.write(text)


def verify_file_does_not_exist_and_get_output_name(input_file_name: str, extension: str) -> str:
    output_name = input_file_name.rsplit(".", 1)[0] + extension
    if os.path.exists(output_name):
        print("Output file already exists!")
        sys.exit(-1)

    return output_name


def process_file(input_name: str) -> None:
    lower_file_name = input_name.lower().strip().rsplit(os.path.sep, 1)[-1]

    if lower_file_name.endswith(".txt"):
        output_name = verify_file_does_not_exist_and_get_output_name(input_name, ".md")
        print(f"Reading .txt file: \"{input_name}\"... ", end="")
        with open(input_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
            write_output(lines, output_name)

    # docx files need some more handling
    elif lower_file_name.endswith(".docx") and not lower_file_name.startswith("~$"):
        output_name = verify_file_does_not_exist_and_get_output_name(input_name, ".md")
        print(f"Reading .docx file: \"{input_name}\"... ", end="")
        text = docx2python.docx2python(input_name).text.replace("--", "*")
        lines = [e + "\n" for e in text.splitlines() if e]
        write_output(lines, output_name)

    # convert .md files back to a format paste-able into Word
    elif lower_file_name.endswith(".md"):
        output_name = verify_file_does_not_exist_and_get_output_name(input_name, ".txt")
        process_md_file(input_name, output_name)


def process(input_name: str) -> None:
    if not os.path.exists(input_name):
        print(f"No file with name \"{input_name}\"!")
        return

    if os.path.isdir(input_name):
        print(f"Converting directory \"{input_name}\"...")
        entries = os.listdir(input_name)
        files = filter(lambda e: e.endswith(".docx") or e.endswith(".txt"), entries)

        for file in files:
            path = os.path.join(input_name, file)
            process_file(path)

    else:
        process_file(input_name)


def main() -> None:
    print("Flesh-Network Blog Post Indenting Tool (2021)")
    print("-> Convert .txt and .docx files into properly formatted blog posts!\n")
    if len(sys.argv) != 2:
        print("Please supply a file name!")
        sys.exit(-1)

    input_name = sys.argv[1]
    process(input_name)


if __name__ == "__main__":
    main()
