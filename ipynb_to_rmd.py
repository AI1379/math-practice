import subprocess
import json
import os
import sys
import re
import argparse


def convert_ipynb_to_rmd(ipynb_path, rmd_path=None):
    """
    Convert Jupyter Notebook to R Markdown format
    """
    if not os.path.exists(ipynb_path):
        raise FileNotFoundError(f"File not found: {ipynb_path}")

    # Set default output path for Rmd
    if rmd_path is None:
        rmd_path = f"{os.path.splitext(ipynb_path)[0]}-result.Rmd"

    # Read the ipynb file content
    with open(ipynb_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # Build Rmd content
    rmd_content = "---\noutput: pdf_document\n---\n\n"
    if notebook["cells"][0]["cell_type"] == "raw":
        # It is the YAML header
        rmd_content = "".join(notebook["cells"][0]["source"]) + "\n\n"

    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            # Process Markdown cells
            rmd_content += "\n".join(cell["source"]) + "\n\n"
        elif cell["cell_type"] == "code":
            # Process code cells
            code = "".join(cell["source"])
            # Convert Python magic commands to R equivalents
            code = re.sub(r"^%matplotlib inline\s*", "", code, flags=re.MULTILINE)
            code = (
                re.sub(r"^!", 'system("', code) + '")' if code.startswith("!") else code
            )

            rmd_content += f"```{{r}}\n{code}\n```\n\n"

    # Write Rmd file
    with open(rmd_path, "w", encoding="utf-8") as f:
        f.write(rmd_content)

    return rmd_path


def render_rmd_to_pdf(rmd_path, pdf_path=None):
    """
    Render R Markdown file to PDF
    """
    RSCRIPT_EXECUTABLE = "Rscript.exe" if sys.platform == "win32" else "Rscript"

    if not os.path.exists(rmd_path):
        raise FileNotFoundError(f"File not found: {rmd_path}")

    # Set default output path for PDF
    if pdf_path is None:
        pdf_path = os.path.splitext(rmd_path)[0] + ".pdf"

    rmd_path = rmd_path.replace("\\", "\\\\")  # Ensure correct path format
    pdf_path = pdf_path.replace("\\", "\\\\")  # Ensure correct path format

    # Call Rscript to render PDF
    r_script = f"""
    rmarkdown::render(
        input = "{rmd_path}",
        output_file = "{pdf_path}",
        output_format = "pdf_document"
    )
    """

    # Create temporary R script
    temp_r_script = "render_script.R"
    with open(temp_r_script, "w") as f:
        f.write(r_script)

    # Execute rendering
    try:
        subprocess.run(
            [RSCRIPT_EXECUTABLE, temp_r_script],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"PDF rendering failed: {e.stderr}") from e
    finally:
        if os.path.exists(temp_r_script):
            os.remove(temp_r_script)

    return pdf_path


def ipynb_to_pdf(ipynb_path, keep_rmd=False):
    """
    Main function: Convert ipynb to PDF
    """
    # Step 1: Convert to Rmd
    rmd_path = convert_ipynb_to_rmd(ipynb_path)
    print(f"✅ Generated R Markdown file: {rmd_path}")

    # Step 2: Render to PDF
    pdf_path = render_rmd_to_pdf(rmd_path)
    print(f"✅ Generated PDF file: {pdf_path}")

    # Clean up intermediate files
    if not keep_rmd:
        os.remove(rmd_path)
        print(f"🗑️ Cleaned up temporary file: {rmd_path}")

    return pdf_path


# Main entry point for the script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Jupyter Notebook to PDF via R Markdown."
    )
    parser.add_argument(
        "input_notebook", help="Path to the input Jupyter Notebook file."
    )
    parser.add_argument(
        "--keep-rmd", action="store_true", help="Keep the intermediate Rmd file."
    )
    args = parser.parse_args()

    input_notebook = os.path.abspath(args.input_notebook)
    input_notebook = os.path.abspath(input_notebook)
    output_pdf = ipynb_to_pdf(input_notebook, keep_rmd=args.keep_rmd)
    print(f"🎉 Conversion completed! PDF saved at: {output_pdf}")
