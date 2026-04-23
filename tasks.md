# 农险期货智能定价系统 — UI重构任务分解 (Tasks)

> **基于**: spec.md v2.0 「田野清风」视觉规范  
> **总预估**: 2个文件, ~640行代码修改  

---

## Phase 1: CSS核心变量层 (Foundation)

### Task 1.1: 重写 `:root` Design Token变量集
**文件**: `src/app.py` → CUSTOM_CSS (行72-100区域)  
**操作**: 替换全部 `--fin-*` 变量为 `--field-*` 变量  
**验收**: 
- [ ] 主色从 `#5068e8`(靛蓝) 变为 `#1B6B48`(保险深绿)
- [ ] 背景从 `#f8fafb`(冷灰) 变为 `#FAFBF8`(暖白)
- [ ] 文字色从 `#1c2230`(蓝灰) 变为 `#1A1F16`(深墨绿)
- [ ] 共计35+个变量全部替换

### Task 1.2: 重写动画关键帧
**文件**: `src/app.py` → CUSTOM_CSS (行102-113区域)  
**操作**: 
- `finSlideUp` 保持(通用)
- `finGentle` 颜色从 `rgba(80,104,232,...)` 改为 `rgba(27,107,72,...)`
- `finShimmer` 保持
**验收**: 动画颜色与主色轴一致

---

## Phase 2: 全局样式层 (Global Styles)

### Task 2.1: .stApp 根容器
**文件**: `src/app.py` → 行115-123
**变更**:
```css
/* 旧 */
background: var(--fin-bg);    /* #f8fafb */
color: var(--fin-text);       /* #1c2230 */
/* 新 */
background: var(--field-bg);   /* #FAFBF8 暖白 */
color: var(--field-text);      /* #1A1F16 墨绿黑 */
```
**验收**: 页面底色呈现温暖米白色调

### Task 2.2: 标题系统 (h1/h2/h3)
**文件**: `src/app.py` → 行125-169
**变更**:
- h1下划线渐变: `--field-primary` → `--field-primary-soft`
- h2左边框 + 背景: `--field-primary` + `--field-primary-bg`
- 字体可考虑标题用 `--field-font-display`(衬线)增加权威感
**验收**: 标题有绿色装饰线，层次分明

### Task 2.3: 正文段落 (p/li/span/div/label)
**文件**: `src/app.py` → 行171-174
**变更**: 文字色改为 `--field-text-secondary` (#3D4A3A)
**验收**: 正文呈深绿色调而非蓝灰色

---

## Phase 3: 组件样式层 (Components)

### Task 3.1: Tabs标签页
**文件**: `src/app.py` → 行176-211
**变更**:
- 容器背景/边框: `--field-surface` / `--field-border`
- 未选中文字: `--field-text-muted`
- 选中态: `--field-primary` 底 + 白字
- 悬停: `--field-hover` 底
**验收**: 标签页选中后呈深绿色

### Task 3.2: Metric指标卡
**文件**: `src/app.py` → 行213-250
**变更**:
- 装饰线渐变: 绿色系
- 数值颜色: `--field-text`
- 悬停阴影: 绿色调
**验收**: 指标卡顶部有绿色装饰条

### Task 3.3: DataFrame数据表
**文件**: `src/app.py` → 行252-287
**变更**:
- 表头背景: `--field-hover`
- 表头文字: `--field-text`
- 下边框: `--field-primary`
- 斑马纹偶数行: `#F7F9F5` (极淡绿)
- 数据字体: 保持 monospace
**验收**: 表头底部有绿色分隔线

### Task 3.4: Button按钮系统
**文件**: `src/app.py` → 行308-351
**变更**:
- Primary按钮: `--field-primary` 渐变底 (非纯色) + 白字
- Secondary按钮: `--field-surface` + `--field-border-strong`
- Primary悬停: `--field-primary-soft` + 上浮动画
- 阴影颜色: 绿色系 rgba(27,107,72,...)
**验收**: 主操作按钮呈深绿色

### Task 3.5: 输入框/选择器
**文件**: `src/app.py` → 行353-373
**变更**:
- 边框: `--field-border-strong`
- 聚焦边框: `--field-primary`
- 聚焦阴影: `rgba(27,107,72,0.10)` 绿色光晕
**验收**: 聚焦时出现绿色边框

### Task 3.6: Alert提示框
**文件**: `src/app.py` → 行375-384
**变更**:
- Info提示: `--field-info-bg` + `--field-info` 色调
**验收**: 提示框呈淡蓝色调(信息)

### Task 3.7: Sidebar侧栏
**文件**: `src/app.py` → 行411-434
**变更**:
- 渐变背景: `--field-surface` → `--field-bg`
- 导航链接悬停: `--field-primary-bg`
**验收**: 侧栏背景呈暖白渐变

### Task 3.8: 其他组件
**文件**: `src/app.py` → 行298-307(blockquote), 436-445(selectbox), 447-449(slider), 451-464(radio), 466-468(animation), 470-480(image), 482-491(plotly), 493-495(markdown), 497-501(caption), 503-509(toolbar)
**变更**: 全部 `--fin-*` → `--field-*` 映射替换
**验收**: 无残留旧色值

---

## Phase 4: Plotly图表主题 (Visualization)

### Task 4.1: plot_utils.py 色彩常量重写
**文件**: `src/visualization/plot_utils.py` → COLOR_SCHEMES字典
**变更**:
```python
'financial': {
    'primary': '#1B6B48',        # 旧: #2563eb
    'accent': '#C4880C',         # 旧: #d97706
    'success': '#1E8A5A',        # 旧: #059669
    'warning': '#D4790C',        # 旧: #d97706
    'danger': '#C7302D',         # 旧: #dc2626
    'bg_card': '#FFFFFF',
    'text_primary': '#1A1F16',   # 旧: #0f172a
    'text_secondary': '#3D4A3A', # 旧: #475569
}
```
**验收**: 图表主色与UI一致

### Task 4.2: FINANCIAL_CSS 微调
**文件**: `src/visualization/plot_utils.py` → 行9-16
**变更**: 背景色改为 `#FAFBF8`
**验收**: 图表容器背景一致

---

## Phase 5: 响应式适配 (Responsive)

### Task 5.1: 移动端断点
**文件**: `src/app.py` → 行510-538
**变更**:
- 保留现有断点逻辑
- 更新引用的变量名
- **删除** `@media (prefers-color-scheme: dark)` 规则块(行531-538)
**验收**: 暗色模式规则已移除

---

## Phase 6: 最终清理 (Cleanup)

### Task 6.1: 残留旧变量扫描
**操作**: 全文搜索 `--fin-` 确保零残留
**验收**: grep返回0结果

### Task 6.2: table th 覆盖样式修复
**文件**: `src/app.py` → 行552-558
**变更**: `var(--fin-primary)` → `var(--field-primary, #1B6B48)`
**验收**: 表头使用正确的fallback色值

---

## 执行顺序依赖图

```
Phase 1 (变量) ──→ Phase 2 (全局) ──→ Phase 3 (组件) ──→ Phase 5 (响应式)
     │                                          │
     └──────────────────→ Phase 4 (Plotly) ←────┘
                              │
                         Phase 6 (清理)
```

**预计总耗时**: ~15分钟 (含验证)
