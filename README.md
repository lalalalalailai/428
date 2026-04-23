# 农险期货智能定价模型 - Streamlit Cloud 部署指南

## 在线访问地址
**部署后自动生成**: `https://<your-app-name>.streamlit.app`

## 一键部署步骤（3分钟）

### Step 1: 登录 Streamlit Cloud
1. 打开 https://share.streamlit.io
2. 使用 GitHub 账号登录
3. 点击 **"Deploy an app"**

### Step 2: 连接 GitHub 仓库
- Repository: 选择 `lalalalalailai/ifap`
- Branch: `master`
- Main file path: `src/app.py`
- Python version: `3.11` (或3.10)

### Step 3: 高级设置 (Advanced settings)
```
Requirements file: requirements.txt
Working directory: /workspace (默认)
Monitor: Enable (免费版)
```

### Step 4: 部署
点击 **"Deploy!"** 按钮，等待约2-3分钟构建完成

---

## 系统架构说明

```
Streamlit Cloud (Ubuntu Linux)
├── src/app.py              ← 主入口 (12个Tab模块)
├── src/models/             ← 三大原创算法
│   ├── agri_pc.py         ← Agri-PC 因果发现
│   ├── acml.py            ← ACML 因果元学习
│   ├── ccp.py             ← CCP 保形预测
│   ├── pricing_model.py   ← 定价核心引擎
│   ├── theorem_proofs.py  ← 6定理证明链
│   └── ablation_study.py  ← 9点消融实验
├── src/data/              ← 数据处理层
├── src/utils/             ← 工具与配置
└── enhanced_data/         ← 36品种期货数据(内置)
```

## 功能模块一览

| Tab | 功能 | 数据需求 |
|-----|------|---------|
| Tab1 | 因果DAG可视化 | 自动加载 |
| Tab2 | 数据探索 | futures csv |
| Tab3 | 定价模型 | 全量数据 |
| Tab4 | 保费计算 | 定价结果 |
| Tab5 | 风险评估 | SHAP分析 |
| Tab6 | 原创算法对比 | AgriPC/ACML/CCP |
| Tab7 | 政策评估 | 社会价值量化 |
| Tab8 | 社会价值 | 宏观影响 |
| Tab9 | 可复现性验证 | 5重交叉验证 |
| Tab10| CSSCI对标 | 学术基准 |
| Tab11| 极端风险预警 | 尾部风险管理 |
| Tab12| 决策支持系统 | 综合推荐 |

## 技术规格

- **语言**: Python 3.11
- **框架**: Streamlit 1.37+
- **算法**: XGBoost + LightGBM + NetworkX
- **AI工具**: 100%国产 (Qwen/GLM/MiniMax)
- **数据**: 36品种 × 2020-2025 × 90+维特征
- **测试**: 46项一致性测试 100%通过

## 常见问题

**Q: 首次加载慢?**
A: 正常, Streamlit Cold Start需要1-2分钟初始化数据和模型

**Q: 某些品种无数据?**
A: 系统使用内置演示数据(A0豆一), 可在设置中切换其他品种

**Q: 内存不足?**
A: 免费版限制1GB RAM, 如遇OOM请减少同时加载的品种数
