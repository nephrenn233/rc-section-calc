# gui.py
import tkinter as tk
from tkinter import messagebox, Listbox, END
import json
import design
import math

with open('materials.json', 'r') as f:
    materials = json.load(f)


def run_calc():
    try:
        concrete = listbox_concrete.get(listbox_concrete.curselection())
        rebar = listbox_rebar.get(listbox_rebar.curselection())
        b = float(entry_b.get())
        h = float(entry_h.get())
        a_s = float(entry_as.get())
        M = float(entry_M.get())

        result = design.calc_rebar(concrete, rebar, b, h, a_s, M)
        text_result.delete(1.0, END)
        canvas.delete("all")

        if not isinstance(result, dict):
            messagebox.showerror("结果", "design.calc_rebar 未返回预期结构（应为 dict）。")
            text_result.insert(END, f"错误：design 返回非 dict：{result}\n")
            return

        if "error" in result:
            messagebox.showerror("结果", result["error"])
            text_result.insert(END, f"错误：{result['error']}\n")
            return

        econ = result.get("economic")
        if isinstance(econ, (list, tuple)) and len(econ) == 5:
            d, n, A_p, rows, per = econ
        else:
            opts = result.get("options", [])
            target_As = result.get("A_s", None)
            if opts and target_As is not None:
                econ = min(opts, key=lambda x: abs(x[2] - target_As))
                d, n, A_p, rows, per = econ
            else:
                messagebox.showerror("结果", "无法解析配筋方案。")
                return

        A_s = result.get("A_s", None)
        msg_main = (
            f"所需 Aₛ = {A_s:.2f} mm²\n"
            f"推荐方案：直径 {d} mm × {n} 根\n"
            f"排数：{rows}，每排：{per} 根\n"
        )
        messagebox.showinfo("计算结果", msg_main)

        text_result.insert(END, "=== 计算结果 ===\n")
        text_result.insert(END, msg_main + "\n")
        text_result.insert(END, "其他可行方案：\n")
        for d2, n2, A_p2, rows2, per2 in result.get("options", []):
            rowinfo = f"{per2}" if rows2 == 1 else f"{per2}/{n2 - per2}"
            text_result.insert(
                END,
                f"直径 {d2} mm，{n2} 根，提供面积 {A_p2:.1f} mm²，排数 {rows2}，每排 {rowinfo}\n"
            )

        draw_section(concrete, rebar, b, h, a_s, d, n, rows, per)

    except Exception as e:
        messagebox.showerror("错误", str(e))


def draw_section(concrete, rebar, b, h, a_s, d, n, rows, per):
    """绘制优化版钢筋混凝土截面"""
    canvas.delete("all")
    W, H = int(canvas["width"]), int(canvas["height"])
    margin = 60  # 边距更大，防止标注重叠

    # 动态缩放比例（保持截面最大尺寸适中）
    scale = min((W - 2 * margin) / b, (H - 2 * margin) / h)
    if scale <= 0:
        scale = 1.0

    bw = b * scale
    bh = h * scale
    cx, cy = W / 2, H / 2 + 10  # 稍微下移避免顶端文字重叠

    # 绘制混凝土矩形
    x0, y0 = cx - bw / 2, cy - bh / 2
    x1, y1 = cx + bw / 2, cy + bh / 2
    canvas.create_rectangle(x0, y0, x1, y1, fill="#D9D9D9", outline="black", width=2)

    # 钢筋参数转换
    a_px = a_s * scale
    dia = d * scale
    spacing = (b - 2 * a_s - d) / max(1, per - 1) if per > 1 else 0

    # 绘制钢筋
    def draw_row(offset_mm, count):
        for i in range(count):
            x_mm = -b / 2 + a_s + d / 2 + i * spacing
            x_px = cx + x_mm * scale
            y_mm = h / 2 - offset_mm
            y_px = cy + y_mm * scale
            canvas.create_oval(
                x_px - dia / 2, y_px - dia / 2,
                x_px + dia / 2, y_px + dia / 2,
                fill="#CC3333", outline="black"
            )

    if rows == 1:
        draw_row(a_s, n)
    else:
        draw_row(a_s, per)
        draw_row(a_s + d + 10, n - per)

    # 尺寸标注线
    arrow_opt = dict(arrow=tk.LAST, width=1)
    # b 尺寸（底部）
    canvas.create_line(x0, y1 + 20, x1, y1 + 20, **arrow_opt)
    canvas.create_line(x1, y1 + 20, x0, y1 + 20, arrow=tk.LAST, width=1)
    canvas.create_text(cx, y1 + 35, text=f"b = {b:.0f} mm", font=("Arial", 10))

    # h 尺寸（右侧）
    canvas.create_line(x1 + 15, y0, x1 + 15, y1, **arrow_opt)
    canvas.create_line(x1 + 15, y1, x1 + 15, y0, arrow=tk.LAST, width=1)
    canvas.create_text(x1 + 40, cy, text=f"h = {h:.0f} mm", font=("Arial", 10))

    # 标题和材料信息
    canvas.create_text(cx, y0 - 35, text="截面示意图", font=("Arial", 11, "bold"))
    canvas.create_text(cx, y0 - 20, text=f"混凝土：{concrete}", font=("Arial", 10))
    canvas.create_text(cx, y0 - 5, text=f"钢筋：{rebar}", font=("Arial", 10))

    # # 底部说明（分两行）
    # canvas.create_text(cx, H - 30,
    #                    text=f"φ{d} mm × {n} 根，保护层 aₛ = {a_s:.0f} mm",
    #                    font=("Arial", 9))
    # canvas.create_text(cx, H - 15,
    #                    text=f"截面尺寸：{b:.0f} × {h:.0f} mm",
    #                    font=("Arial", 9, "italic"))

# === GUI 布局 ===
root = tk.Tk()
root.title("钢筋混凝土正截面设计")

frame_left = tk.Frame(root)
frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="n")

tk.Label(frame_left, text="混凝土型号").grid(row=0, column=0)
listbox_concrete = Listbox(frame_left, height=6, exportselection=False)
for c in materials["concrete"].keys():
    listbox_concrete.insert(END, c)
listbox_concrete.grid(row=0, column=1)

tk.Label(frame_left, text="钢筋型号").grid(row=1, column=0)
listbox_rebar = Listbox(frame_left, height=6, exportselection=False)
for r in materials["rebar"].keys():
    listbox_rebar.insert(END, r)
listbox_rebar.grid(row=1, column=1)

tk.Label(frame_left, text="b (mm)").grid(row=2, column=0)
entry_b = tk.Entry(frame_left)
entry_b.grid(row=2, column=1)
tk.Label(frame_left, text="h (mm)").grid(row=3, column=0)
entry_h = tk.Entry(frame_left)
entry_h.grid(row=3, column=1)
tk.Label(frame_left, text="a_s (mm)").grid(row=4, column=0)
entry_as = tk.Entry(frame_left)
entry_as.grid(row=4, column=1)
tk.Label(frame_left, text="M (kN·m)").grid(row=5, column=0)
entry_M = tk.Entry(frame_left)
entry_M.grid(row=5, column=1)

tk.Button(frame_left, text="计算", command=run_calc).grid(row=6, column=0, columnspan=2, pady=10)

# 中间结果显示
frame_middle = tk.Frame(root)
frame_middle.grid(row=0, column=1, padx=10, pady=10, sticky="n")
tk.Label(frame_middle, text="计算结果").pack()
text_result = tk.Text(frame_middle, width=45, height=20)
text_result.pack()

# 右侧截面图
frame_right = tk.Frame(root)
frame_right.grid(row=0, column=2, padx=10, pady=10, sticky="n")
tk.Label(frame_right, text="截面图").pack()
canvas = tk.Canvas(frame_right, width=400, height=400, bg="white")
canvas.pack()

root.mainloop()
