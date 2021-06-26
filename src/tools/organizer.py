import re
import os
import sys
import shutil


def slugify(base: str) -> str:
    return re.sub(r"[^a-zA-Z0-9-]+", "", base.replace(" ", "-"))


def main() -> None:
    print("Flesh-Network Blog Post Organization Tool (2021)")
    print("-> Sort markdown files into their directories!\n")
    if len(sys.argv) != 2:
        print("Please supply a directory name!")
        sys.exit(-1)

    input_name = sys.argv[1]
    entries = os.listdir(input_name)
    files = filter(lambda e: e.endswith(".md"), entries)

    for file in files:
        print(f"Packaging \"{file}\"...")

        base_path = slugify(file.rsplit(".", 1)[0])
        res_path = os.path.join(base_path, "res")
        destination = os.path.join(base_path, "post.md")

        os.mkdir(base_path)
        os.mkdir(res_path)

        shutil.move(file, destination)


if __name__ == "__main__":
    main()
