import json
import glob
import sys
import os

new_kernel_spec = {
    "name": "ir",
    "display_name": "R",
    "language": "R",
}

new_language_info = {
    "name": "R",
}

base = []

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if os.path.exists(arg):
            base.append(arg)
        else:
            print(f"Warning: {arg} does not exist. Skipping.")

if len(base) == 0:
    print("No valid paths provided. Searching in the current directory.")
    base = ["./"]

for path in base:
    for ipynb_file in glob.glob(f"{path}/*.ipynb"):
        print(f"Updating kernel spec in {ipynb_file}...")
        with open(ipynb_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["metadata"]["kernelspec"] = new_kernel_spec
        data["metadata"]["language_info"] = new_language_info

        with open(ipynb_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
