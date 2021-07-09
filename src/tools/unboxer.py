import indenter
import shutil
import os


def main() -> None:
    print("Flesh-Network Blog Post Unboxing Tool (2021)")
    print("-> Turn blogpost folders into text files!\n")

    copy_paths = list()
    for root, dirs, files in os.walk("."):
        for _dir in dirs:
            base_path = os.path.join(root, _dir)
            txt_path = os.path.join(base_path, "post.txt")
            md_path = os.path.join(base_path, "post.md")
            copy_paths.append((_dir, txt_path))
            indenter.process(md_path)

    print("Finishing up... ", end="")
    for name, path in copy_paths:
        shutil.move(path, name + ".txt")
        shutil.rmtree(name)

    print("Done!")


if __name__ == "__main__":
    main()
