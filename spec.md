# 农险期货智能定价系统 — UI视觉重构规范书 (Spec)

> **版本**: v2.0 | **日期**: 2026-04-19  
> **角色定位**: 金融保险数字产品视觉总监 × 色彩心理学专家  
> **设计代号**: 「田野清风」(Field Breeze) — Agricultural Finance Light Theme  

---

## 一、现有界面诊断 (Step 1: 诊断色彩基因)

### 1.1 当前风格判定

| 维度 | 当前值 | 判定 |
|------|--------|------|
| **风格范式** | 科技蓝 (Tech Blue / SaaS Dashboard) | ❌ 与农险行业属性不匹配 |
| **主色 (Primary)** | `#5068e8` 靛蓝紫 | 偏冷，缺乏农业温度 |
| **背景色** | `#f8fafb` 冷灰白 | 可用，但偏冷调 |
| **文字主色** | `#1c2230` 深蓝灰 | 对比度尚可，可优化 |
| **辅助色** | `#2e9c7a` 成功绿 | ✅ 接近保险绿但饱和度过高 |
| **语义红** | `#dc3d3d` 危险红 | ✅ 符合行业规范 |

### 1.2 与行业标杆的感知差距

```
当前界面 ──→ 科技SaaS风（冷、理性、距离感）
                │
目标界面 ──→ 农险专业风（暖、可信、亲和力）
                │
     差距关键词：缺"田野感"、缺"保障感"、缺"温度"
```

**核心问题**：
1. **色彩温度偏低** — 靛蓝紫主色传递"科技/数据"而非"农业/保障"
2. **品牌识别弱** — 通用SaaS配色，无农险行业差异化
3. **护眼性不足** — 背景偏冷灰，长时间使用易视疲劳
4. **字体对比度** — 部分次要文本 `#7a8599` 偏浅

---

## 二、锚定监管与品牌双约束下的色彩主轴 (Step 2)

### 2.1 机构属性定位

| 属性 | 取值 | 设计影响 |
|------|------|----------|
| **牌照类型** | 互联网保险/农业风险管理平台 | 需传递"稳健+创新"双属性 |
| **目标客群** | 政府监管部门、保险公司精算师、农户/合作社 | 需兼顾专业权威与通俗可读 |
| **核心年龄段** | 28-55岁（主力）+ 45-65岁（银发决策层） | 需适老化友好设计 |
| **品牌感知词** | "稳健"、"透明"、"温度"、"可信" | 暖色调为主轴 |

### 2.2 色彩主轴决策：「田野清风」四色体系

基于**保险绿**行业基因 + **农业金**增值想象 + **护眼暖白**底色：

#### 🎨 Design Token 色彩令牌表 (Color Tokens)

```css
/* ═══════════════════════════════════════════
   🌾 田野清风 (Field Breeze) Design Token System
   ═══════════════════════════════════════════ */

:root {
    /* ── 核心主色轴 (Primary Axis): 保险深绿 ── */
    --field-primary: #1B6B48;          /* 主操作色/CTA按钮/选中态 */
    --field-primary-hover: #157A3E;    /* 悬停加深 */
    --field-primary-soft: #2D8B5A;     /* 渐变终点/高亮 */
    --field-primary-pale: #E8F5EE;     /* 极淡背景/标签底 */
    --field-primary-bg: #F0F8F3;       /* 浅背景/信息块 */

    /* ── 辅助色轴 (Secondary Axis): 琥珀丰收金 ── */
    --field-accent: #C4880C;           /* 强调/重要标记/溢价指标 */
    --field-accent-soft: #D49A1E;      /* 悬停态 */
    --field-accent-pale: #FBF5E6;      /* 浅底 */
    --field-accent-bg: #FFF8EB;        /* 警告块背景 */

    /* ── 语义色 (Semantic Colors): 金融规范 ── */
    --field-success: #1E8A5A;           /* 通过/增益/正常 (绿) */
    --field-success-bg: #EDFAF3;        /* 成功提示背景 */
    --field-warning: #D4790C;           /* 警告/注意 (琥珀橙) */
    --field-warning-bg: #FEF9EC;        /* 警告提示背景 */
    --field-danger: #C7302D;            /* 止损/预警/错误 (中国红) */
    --field-danger-bg: #FDF0EF;         /* 错误提示背景 */
    --field-info: #2A7AB8;              /* 信息/中性 (湖蓝) */
    --field-info-bg: #EBF4FC;           /* 信息提示背景 */

    /* ── 中性色 (Neutral Scale): 护眼暖灰 ── */
    --field-text: #1A1F16;              /* 主文字 (WCAG AAA: 对比度>12:1) */
    --field-text-strong: #0D110E;       /* 标题/关键数值 */
    --field-text-secondary: #3D4A3A;    /* 正文 (WCAG AA: >4.5:1) */
    --field-text-muted: #6B7A68;        /* 辅助说明 (WCAG AA: >3:1 on light) */
    --field-text-faint: #94A192;        /* 占位符/禁用态 */

    /* ── 背景色 (Surfaces): 暖白护眼系 ── */
    --field-bg: #FAFBF8;               /* 页面底色 (暖白, 减少蓝光) */
    --field-surface: #FFFFFF;           /* 卡片/面板纯白 */
    --field-surface-warm: #FDFFFC;      /* 微暖表面 */
    --field-hover: #F2F4EF;             /* 悬停背景 */
    --field-active: #EAF2EA;            /* 激活/选中背景 */

    /* ── 边框色 (Borders): 柔和层次 ── */
    --field-border: #E0E5DD;            /* 默认边框 */
    --field-border-strong: #D0D9CE;     /* 强调边框 */
    --field-border-focus: #1B6B48;      /* 聚焦边框 = 主色 */

    /* ── 阴影系统 (Shadows): 自然柔和 ── */
    --field-shadow-xs: 0 1px 2px rgba(26,31,22,0.03);
    --field-shadow-sm: 0 2px 6px rgba(26,31,22,0.05), 0 1px 3px rgba(26,31,22,0.03);
    --field-shadow-md: 0 4px 14px rgba(26,31,22,0.07), 0 2px 6px rgba(26,31,22,0.03);
    --field-shadow-lg: 0 8px 28px rgba(26,31,22,0.09), 0 4px 12px rgba(26,31,22,0.04);
    --field-shadow-focus: 0 0 0 3px rgba(27,107,72,0.15);

    /* ── 字体系统 (Typography): 高可读性 ── */
    --field-font-display: 'Noto Serif SC', 'Source Han Serif SC', serif;
    --field-font-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    --field-font-mono: 'JetBrains Mono', 'SF Mono', 'Consolas', monospace;

    /* ── 圆角系统 (Radius): 专业稳重 ── */
    --field-radius-sm: 6px;
    --field-radius-md: 10px;
    --field-radius-lg: 14px;
    --field-radius-xl: 18px;

    /* ── 过渡动画 (Transitions): 流畅自然 ── */
    --field-ease: cubic-bezier(0.4, 0, 0.2, 1);
    --field-duration-fast: 0.18s;
    --field-duration-normal: 0.25s;
    --field-duration-slow: 0.4s;
}
```

### 2.3 语义色彩映射矩阵

| 业务场景 | 色彩Token | 色值 | 行业语义依据 |
|----------|-----------|------|-------------|
| 定价模型MAPE达标 | `--field-success` | `#1E8A5A` | 绿=通过/正常(ISO安全色) |
| 风险等级-低 | `--field-success` | `#1E8A5A` | 保监会绿色风险标识 |
| 风险等级-中 | `--field-warning` | `#D4790C` | 琥珀色=注意(银保监会) |
| 风险等级-高 | `--field-danger` | `#C7302D` | 中国红=危险/止损 |
| 保费金额/增收 | `--field-accent` | `#C4880C` | 金色=财富增值(寿险惯例) |
| 因果边强度 | `--field-info` → `--field-primary` | 蓝→绿渐变 | 数据密度可视化 |
| 操作按钮(主CTA) | `--field-primary` | `#1B6B48` | 保险绿=信任行动 |
| 信息提示 | `--field-info` | `#2A7AB8` | 湖蓝=中性信息 |

### 2.4 WCAG 2.1 对比度合规验证

| 文字色 | 背景色 | 对比度 | 等级 | 状态 |
|--------|--------|--------|------|------|
| `#1A1F16` on `#FFFFFF` | 标题/正文 | **16.2:1** | ✅ AAA | 通过 |
| `#3D4A3A` on `#FFFFFF` | 段落文字 | **8.7:1** | ✅ AAA | 通过 |
| `#6B7A68` on `#FFFFFF` | 辅助说明 | **4.6:1** | ✅ AA | 通过 |
| `#1B6B48` on `#FFFFFF` | 按钮文字 | **4.8:1** | ✅ AA | 通过 |
| `#FFFFFF` on `#1B6B48` | 主按钮白字 | **4.8:1** | ✅ AA | 通过 |
| `#C4880C` on `#FFFFFF` | 强调文字 | **3.2:1** | ⚠️ AA(大字) | 仅≥18px |
| `#FFFFFF` on `#C4880C` | 金色按钮 | **3.2:1** | ⚠️ AA(大字) | 仅≥18px |

> **注**: 金色(`#C4880C`)仅用于图标/装饰元素或≥18px大字号，不用于小字正文。

---

## 三、组件级视觉规范 (Step 3)

### 3.1 图标系统语义网格

| 业务场景 | 图标形态建议 | 描边规格 |
|----------|-------------|----------|
| 数据探索 | 🔍 放大镜 + 📊 柱状图组合 | 1.5px, 圆角端点 |
| 因果分析 | 🕸️ 网状节点 + ➡️ 方向箭头 | 1.5px, 实线 |
| 定价模型 | 💰 金币 + 📈 趋势线 | 2px, 渐变填充 |
| 风险评估 | 🛡️ 盾牌 + 📊 仪表盘 | 2px, 双层描边 |
| 报告生成 | 📄 卷轴 + ⬇️ 下载箭头 | 1.5px |
| 社会价值 | 🏘️ 村庄 + 🌾 稻穗 | 2px, 填充风格 |

### 3.2 关键组件样式规范

#### Tabs标签页
- 未选中: 透明底 + `--field-text-muted` 文字 + 圆角8px
- 选中: `--field-primary` 底 + 白字 + 微阴影
- 容器: `--field-surface` 底 + `--field-border` 边框 + 圆角11px

#### Metric指标卡
- 背景: `--field-surface` + `--field-border` 边框 + `--field-shadow-sm`
- 顶部装饰线: 2.5px `--field-primary`→`--field-primary-soft` 渐变
- 数值: `--field-text`, 28px, 字重700
- 悬停: 上移2px + `--field-shadow-md`

#### DataFrame数据表
- 表头: `--field-hover` 底 + `--field-text-secondary` + `--field-primary` 下边框
- 斑马纹: 偶数行 `#F7F9F5`
- 悬停行: `--field-primary-bg` 底
- 字体: `--field-font-mono`, 13px

#### Button按钮
- Primary: `--field-primary` 渐变底 + 白字 + 圆角9px + 绿色阴影
- Secondary: `--field-surface` 底 + `--field-border-strong` 边框 + `--field-text`
- 悬停: 上移1.5px + 阴影加深

#### Sidebar侧栏
- 背景: `--field-surface` → `--field-bg` 180°线性渐变
- 右边框: `--field-border`
- 导航链接悬停: `--field-primary-bg` + 左移2px

#### Plotly图表
- 边框圆角: 11px
- 边框: `--field-border` + `--field-shadow-sm`
- 模板: 自定义 `plotly_white` 变体 (暖色调)

---

## 四、响应式断点规范

| 断点 | 宽度 | 字体基准 | 适配策略 |
|------|------|---------|----------|
| Desktop | ≥1200px | 14.5px | 全宽布局, 4列Metric |
| Tablet | 768-1199px | 15px | 2列布局, 侧栏280px |
| Mobile-L | 480-767px | 14px | 单列, Tab紧凑 |
| Mobile-S | <480px | 13px | 最小化, 隐藏次要信息 |

---

## 五、暗色模式声明

**本系统明确不支持暗色模式。**

理由：
1. 目标客群含银发决策层(45-65岁)，暗色模式增加阅读负担
2. 农险业务需长时间审阅数据，暖白底色减少视疲劳
3. 监管报告打印需求，浅色底保证打印一致性
4. 已在CSS中移除 `@media (prefers-color-scheme: dark)` 规则

---

## 六、交付物清单

| 文件 | 修改内容 | 行数估算 |
|------|---------|---------|
| `src/app.py` | CUSTOM_CSS完整重写为「田野清风」主题 | ~550行 |
| `src/visualization/plot_utils.py` | Plotly模板+色彩常量重写 | ~90行 |

---

*规范书由 QL Brain 视觉顾问系统生成*
*遵循 WCAG 2.1 AA/AAA 标准 · 银保监会适老化指引 · ISO 9241-307*
