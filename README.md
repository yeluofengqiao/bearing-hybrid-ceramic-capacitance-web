# Hybrid Ceramic Bearing Capacitance Web

这是一个面向工程判断的混合陶瓷球轴承电容分析工具，包含 Flask 版本和 GitHub Pages 版本，两端共享同一套 Python 核心模型、同一套前端配置和同一套结果渲染逻辑。

默认参数按 `6208` 深沟球轴承预填：

- `PCD = 60 mm`
- `Dw = 11.906 mm`
- `Z = 9`

## 当前功能

网页默认走轻量分析路径，优先保证打开和计算响应速度；核心 Python 模型仍然保留扩展分析能力。

- 单工况计算：
  - 轴承本体电容
  - 显式寄生并联网络
  - 测量等效总电容
  - 三段分压与等效场强
  - 单球路径明细
- 阻抗输出：
  - 单点频率下的 `Ceq`、`Xc`、`|Z|`
- 风险判断：
  - 基于最大油膜场强和最小 `lambda`
  - 输出风险等级、主风险段和触发原因
- Compare Mode：
  - `Case A / Case B` 双工况比较
  - 输出关键指标差值
- 交互与导出：
  - 中英文切换
  - 单位切换
  - 分享链接
  - 单球结果 CSV 导出
  - PDF 报告导出

如果直接调用 Python 核心模型，仍可启用扩展分析输出：

- 扫频
- 转速/温度/载荷扫参
- 敏感性分析

## 模型结构

每条主路径采用串联电容网络：

```text
内圈油膜 + 陶瓷球本体 + 外圈油膜
```

整套轴承的测量总电容采用：

```text
C_total = C_intrinsic + C_cage + C_seal + C_mounting + C_background
```

其中：

- `C_intrinsic` 是加载滚动体路径的并联和
- `C_cage`、`C_seal`、`C_mounting`、`C_background` 是显式寄生并联支路

## 已考虑的因素

- 转速
- 径向载荷
- 轴向载荷
- 轴向预紧
- 内圈温度
- 外圈温度
- 初始游隙、配合损失、热损失
- 钢圈 / 陶瓷球弹性参数
- 油品粘温关系
- 温度和压力下的介电修正
- 润滑状态倍率修正
- 粗糙峰接触修正

## 本轮明确未做

- 背景电容自动标定
- 油膜导电 / 泄漏电阻支路
- 批量 CSV 工况导入

当前阻抗仍是纯电容等效阻抗模型：

```text
phase = -90°
```

## 使用的近似

- Hertz 点接触椭圆接触
- Hamrock-Dowson 点接触中央膜厚与最小膜厚（中央膜厚用于集总电容近似，最小膜厚用于 `lambda` 和峰值场强）
- 深沟球轴承准静态载荷分配
- 陶瓷球本体 spreading capacitance 近似
- 纯电容阻抗等效，不含泄漏电阻

因此它更适合作为工程估算和参数比较工具，而不是高频测试台反演模型。

当 `lambda < 3` 时，结果会明确标记为混合/边界润滑筛查；尤其 `lambda < 1` 时，纯电容网络不再是可闭合的物理模型，风险等级只能作为触发复测的信号，不能当成绝对击穿概率。

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

## 部署

### Flask / Render

仓库包含：

- `app.py`
- `render.yaml`
- `gunicorn.conf.py`

Render 连接 GitHub 后会自动创建服务。

### GitHub Pages

仓库中的 `docs/` 目录提供静态公开页面。

- 页面通过 `Pyodide` 在浏览器里直接运行同一套 Python 模型
- 使用与 Flask 相同的共享前端资源和配置
- 不依赖独立后端服务
