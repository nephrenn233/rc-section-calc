import json
import math

with open('materials.json', 'r') as f:
    materials = json.load(f)

concrete = input('请输入混凝土型号（如 C30）：')
rebar = input('请输入钢筋型号（如 HRB400）：')
# 输入材料型号
b = input('请输入截面宽度 b（mm）：')
# 截面宽度
h = input('请输入截面高度 h（mm）：')
# 截面高度
a_s = input('请输入受拉钢筋保护层厚度 a_s（mm）：')
# 受拉钢筋合力点至截面受拉边缘的距离
M = input('请输入弯矩设计值 M（kN·m）：')
# 弯矩设计值
f_cuk = materials['concrete'][concrete]['f_cuk']
# 混凝土立方体抗压强度标准值
fc = materials['concrete'][concrete]['fc']
# 混凝土轴心抗压强度设计值
ft = materials['concrete'][concrete]['ft']
# 混凝土轴心抗拉强度设计值
Es = materials['rebar'][rebar]['Es']
# 钢筋弹性模量
fy = materials['rebar'][rebar]['fy']
# 钢筋抗拉强度设计值
alpha_1 = materials['concrete'][concrete]['alpha_1']
beta_1 = materials['concrete'][concrete]['beta_1']
# 混凝土受压区等效矩形应力图形系数
epsilon_cu = 0.0033 - (f_cuk - 50) * (1e-5)
# 混凝土极限压应变
xi_b = beta_1 / (1 + fy / (epsilon_cu * Es))
# 相对界限受压区高度
rho_min = max(0.002, 0.45 * ft / fy)
# 最小配筋率
A_smin = rho_min * b * h
# 最小受拉钢筋面积
h0 = h - a_s
# 截面有效高度

def get_As():
# 计算 所需受拉钢筋面积
    alpha_s = M / (alpha_1 * fc * b * h0 * h0)
    xi = 1 - math.sqrt(1 - 2 * alpha_s)

    if xi > xi_b:
        return -1
    else:
        A_s = alpha_1 * fc * b * xi * h0 / fy
        if A_s < A_smin:
            A_s = A_smin
        return A_s

A_s = get_As()
if A_s == -1:
    print('截面受压区高度过大，需增加截面尺寸或提高混凝土强度等级')
else:
# 选配钢筋
    valid_rebars = []
    for diameter in [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 36, 40, 50]:
        area = math.pi * (diameter / 2) ** 2
        n_bars = math.ceil(A_s / area)
        s = max(25, diameter)
        A_s_provided = n_bars * area
        b_min = 2 * a_s + (n_bars - 1) * (diameter + s)

        if A_s_provided >= A_s and b_min <= b:
            valid_rebars.append((diameter, n_bars, A_s_provided))

    if not valid_rebars:
        print('无法满足受拉钢筋面积要求，需增加截面宽度或调整钢筋型号')
    else:
        print('所需受拉钢筋面积 A_s = {:.2f} mm²'.format(A_s))
        print('可选配筋方案（钢筋直径 mm，根数，提供面积 mm²）：')
        for diameter, n_bars, A_s_provided in valid_rebars:
            print('直径：{} mm，根数：{}，提供面积：{:.2f} mm²'.format(diameter, n_bars, A_s_provided))