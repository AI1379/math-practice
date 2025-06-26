import subprocess
import json
import os
import sys
import re


def convert_ipynb_to_rmd(ipynb_path, rmd_path=None):
    """
    将Jupyter Notebook转换为R Markdown格式
    """
    if not os.path.exists(ipynb_path):
        raise FileNotFoundError(f"文件未找到: {ipynb_path}")

    # 设置默认输出路径
    if rmd_path is None:
        rmd_path = f"{os.path.splitext(ipynb_path)[0]}-temp.Rmd"

    # 读取ipynb文件内容
    with open(ipynb_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # 构建Rmd内容
    rmd_content = "---\noutput: pdf_document\n---\n\n"

    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            # 处理Markdown单元格
            rmd_content += "\n".join(cell["source"]) + "\n\n"
        elif cell["cell_type"] == "code":
            # 处理代码单元格
            code = "".join(cell["source"])
            # 转换Python魔法命令为R等效命令
            code = re.sub(r"^%matplotlib inline\s*", "", code, flags=re.MULTILINE)
            code = (
                re.sub(r"^!", 'system("', code) + '")' if code.startswith("!") else code
            )

            rmd_content += f"```{{r}}\n{code}\n```\n\n"

    # 写入Rmd文件
    with open(rmd_path, "w", encoding="utf-8") as f:
        f.write(rmd_content)

    return rmd_path


def render_rmd_to_pdf(rmd_path, pdf_path=None):
    """
    将R Markdown文件渲染为PDF
    """
    if not os.path.exists(rmd_path):
        raise FileNotFoundError(f"文件未找到: {rmd_path}")

    # 设置默认输出路径
    if pdf_path is None:
        pdf_path = os.path.splitext(rmd_path)[0] + ".pdf"

    # 调用Rscript渲染PDF
    r_script = f"""
    rmarkdown::render(
        input = "{rmd_path}",
        output_file = "{pdf_path}",
        output_format = "pdf_document"
    )
    """

    # 创建临时R脚本
    temp_r_script = "render_script.R"
    with open(temp_r_script, "w") as f:
        f.write(r_script)

    # 执行渲染
    try:
        subprocess.run(["Rscript", temp_r_script], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"PDF渲染失败: {e.stderr}") from e
    finally:
        if os.path.exists(temp_r_script):
            os.remove(temp_r_script)

    return pdf_path


def ipynb_to_pdf(ipynb_path, keep_rmd=False):
    """
    主函数：转换ipynb到PDF
    """
    # 步骤1: 转换为Rmd
    rmd_path = convert_ipynb_to_rmd(ipynb_path)
    print(f"✅ 已生成R Markdown文件: {rmd_path}")

    # 步骤2: 渲染为PDF
    pdf_path = render_rmd_to_pdf(rmd_path)
    print(f"✅ 已生成PDF文件: {pdf_path}")

    # 清理中间文件
    if not keep_rmd:
        os.remove(rmd_path)
        print(f"🗑️ 已清理临时文件: {rmd_path}")

    return pdf_path


# 使用示例
if __name__ == "__main__":
    input_notebook = sys.argv[1] if len(sys.argv) > 1 else "input.ipynb"
    output_pdf = ipynb_to_pdf(input_notebook, keep_rmd=True)
    print(f"🎉 转换完成! PDF保存于: {output_pdf}")
