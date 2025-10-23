import json
import math
2
with open('materials.json', 'r') as f:
    materials = json.load(f)

def calc_rebar(concrete, rebar, b, h, a_s, M):
    f_cuk = materials['concrete'][concrete]['fcuk']           # 混凝土立方体抗压强度标准值
    fc = materials['concrete'][concrete]['fc']                # 混凝土轴心抗压强度标准值
    ft = materials['concrete'][concrete]['ft']                # 混凝土轴心抗拉强度标准值
    Es = materials['rebar'][rebar]['Es']                      # 钢筋弹性模量
    fy = materials['rebar'][rebar]['fy']                      # 钢筋抗拉强度设计值
    alpha_1 = materials['concrete'][concrete]['alpha1']       # 混凝土受压区等效矩形系数
    beta_1 = materials['concrete'][concrete]['beta1']         # 同上
    epsilon_cu = 0.0033 - (f_cuk - 50) * (1e-5)               # 混凝土极限压应变
    xi_b = beta_1 / (1 + fy / (epsilon_cu * Es))              # 相对界限受压区高度
    rho_min = max(0.002, 0.45 * ft / fy)                      # 最小配筋率
    A_smin = rho_min * b * h                                  # 最小受拉钢筋面积
    h0 = h - a_s                                              # 截面有效高度

    alpha_s = M * 1e6 / (alpha_1 * fc * b * h0 * h0)
    xi = 1 - math.sqrt(1 - 2 * alpha_s)
    if xi > xi_b:
        return {"error": "截面受压区高度过大，应增大截面尺寸或提高混凝土强度等级"}

    A_s = alpha_1 * fc * b * xi * h0 / fy
    if A_s < A_smin:
        A_s = A_smin

    valid = []
    for d in [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 36, 40, 50]:
        area = math.pi * (d / 2) ** 2
        n = math.ceil(A_s / area)
        s = max(25, d)
        A_p = n * area
        b_req = 2 * a_s + (n - 1) * (d + s)
        if A_p >= A_s and b_req <= b:
            valid.append((d, n, A_p, 1, n))
        else:
            if (h - a_s) >= (2 * d + 10):
                per = math.ceil(n / 2)
                b_req2 = 2 * a_s + (per - 1) * (d + s)
                if A_p >= A_s and b_req2 <= b:
                    valid.append((d, n, A_p, 2, per))

    if not valid:
        return {"error": "无法满足受拉钢筋面积要求，需增加截面宽度或调整钢筋型号"}

    econ = min(valid, key=lambda x: x[2] - A_s)
    return {
        "A_s": A_s,
        "options": valid,
        "economic": econ,
    }
