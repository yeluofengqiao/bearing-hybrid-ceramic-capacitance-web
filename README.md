# Hybrid Ceramic Bearing Capacitance Web

这是一个独立的 Flask 网页工具，用来估算混合陶瓷球轴承在不同转速、温度和载荷下的等效电容。

默认参数按 `6208` 深沟球轴承近似预填：

- 节圆直径 `PCD = 60 mm`
- 球径 `Dw = 11.906 mm`
- 滚动体数量 `Z = 9`

网页会同时给出：

- 轴承本体电容 `C_bearing`
- 含背景电容的测量等效总电容 `C_total = C_bearing + C_background`
- 单球载荷、膜厚和串联等效电容明细

## 模型结构

每颗滚动体通路采用串联电容近似：

```text
内圈油膜电容 + 陶瓷球本体电容 + 外圈油膜电容
```

整套轴承的本体电容采用并联叠加：

```text
C_bearing = Σ C_ball_path
```

## 考虑的因素

- `载荷`：通过准静态载荷分配求每颗球的接触载荷
- `转速`：通过卷吸速度影响 EHL 膜厚
- `温度`：通过 ASTM D341 粘温关系影响运行粘度，再影响膜厚
- `材料`：钢圈 / 陶瓷球的等效弹性模量和介电常数都参与计算
- `润滑剂介电常数`：用 Clausius-Mossotti 关系按温度和压力修正

## 使用的近似

- Hertz 点接触椭圆接触面积
- Hamrock-Dowson 点接触中心膜厚
- 深沟球轴承准静态位移平衡载荷分配
- 陶瓷球本体采用 spreading capacitance 近似

这意味着它更适合作为工程估算工具，而不是高频阻抗测试台的严格反演模型。

## 本地运行

```bash
pip install -r requirements.txt
python3 app.py
```

浏览器打开：

```text
http://127.0.0.1:5001
```

## 测试

```bash
python3 -m unittest discover -s tests
```

## Render 部署

仓库包含：

- `app.py`
- `requirements.txt`
- `gunicorn.conf.py`
- `render.yaml`

Render 连接到 GitHub 后会自动读取 `render.yaml` 创建服务。

## GitHub Pages 公开网页

仓库中的 `docs/` 目录提供了一个静态公开页面。

- 页面通过 `Pyodide` 在浏览器里直接运行同一套 Python 模型
- 不依赖单独的 Flask 服务
- 启用 GitHub Pages 后可直接公开访问

如果 Pages 已启用，公开链接通常为：

```text
https://yeluofengqiao.github.io/bearing-hybrid-ceramic-capacitance-web/
```

## 说明

混合陶瓷球轴承里，陶瓷球本体常常会成为串联链路中的主要限流元件，因此：

- `载荷` 对总电容的影响通常最明显
- `转速` 和 `温度` 对油膜电容的影响仍然存在，但对总电容的敏感度会比全钢轴承更温和
