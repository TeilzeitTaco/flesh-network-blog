import sys


# Program to convert MS-Word pastes into a less
# annoying text file layout.

translation_table = [
    ("“", "\""), ("”", "\""), ("„", "\""),
    ("’", "'"), ("–", "-"), ("…", "..."),
    ("•", "*"),
]


def main(file_name: str, out_file_name: str) -> None:
    with open(file_name, "r", encoding="utf-8") as f:
        lines = f.readlines()

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
            for sym, rep in translation_table:
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please supply a file name!")
        sys.exit(-1)

    output_name = "processed-" + sys.argv[1]
    main(sys.argv[1], output_name)
    print(f"Output file written to \"{output_name}\"!")
