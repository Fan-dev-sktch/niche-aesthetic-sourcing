![Niche Aesthetic Sourcing](assets/banner.svg)

[![Local tests](https://img.shields.io/badge/local_tests-12_passing-2e6d51)](tests/test_workflow.py)
![Version](https://img.shields.io/badge/skill-v1.0.1-111827)
![Runtime](https://img.shields.io/badge/tools-Python_stdlib-3776AB)

中文 · [English](README.en.md) · [下载](https://github.com/Fan-dev-sktch/niche-aesthetic-sourcing/releases/latest) · [技能原文](skills/niche-aesthetic-sourcing/SKILL.md)

# Niche Aesthetic Sourcing · 小众审美选品

**把审美直觉，变成可检验的生意。**

一张贴纸很好看，标价也不低。轮到你卖，谁会付款？算上运费、平台费、获客和售后，一单还能留下多少？

`niche-aesthetic-sourcing` 是面向海外消费者零售的 AI skill，把小众审美和兴趣产品的想法，变成有来源、有反证、有成本边界的选品判断。适合原创设计者、小型卖家，以及正在评估贴纸、收藏配件、娃衣或微缩小物的人。

你带来审美、设计或供货能力。它帮助你找出最值得继续的 1–3 个候选，说明买家为什么买、现有替代品有什么、关键证据还缺什么，以及下一笔时间和钱该用来验证哪件事。审美负责提出想法，证据决定是否继续。

## 六项证据，逐项判断

| 项目 | 要回答的问题 |
|---|---|
| 需求 | 目标人群是否有实际购买证据？ |
| 审美溢价 | 控制材质、功能、品牌和交付后，设计是否获得额外付款？ |
| 竞争缺口 | 买家哪里不满意，现有替代品为何没有满足？ |
| 整单利润 | 扣除配送、平台、获客、劳动和售后，一单能留下多少？ |
| 权利与渠道 | 产品和宣传素材能否使用，真实卖家是否具备准入资格？ |
| 履约 | 实物质量、适配、发货和退换能否兑现？ |

要求快增长时，另外核对数据观察期和当前可比趋势；个人收藏用于找风格，完整成本用于判断利润。

每项记录“通过 / 未知 / 不通过”。价格高、评论多、搜索结果少，都不能单独证明生意成立。未知费用保留未知；全店销量不归给单品；供应网页不冒充正式报价。

## 从想法到有限试卖

1. 定人群、国家、预算和能力，找不同购买理由的候选。
2. 看商品图、原页、使用反馈和差评，核对替代品与反证。
3. 找出最影响决定的缺口，补报价、样品、权利、渠道或成本。
4. 条件齐备后，设计一个成交渠道、一条获客路径的有限试卖；提前写预算、付款指标和停止条件，用实际结果更新判断。

既算一单能留的钱，也算整轮最高现金承诺：库存、打样、投放、履约及退赔。零收入、未售库存零回收时，也要守住可承受亏损。上架时间、首单和回本日期不作保证。


## 安装与开始

**在 Codex 对话中说：**

> 请用 skill-installer，从 https://github.com/Fan-dev-sktch/niche-aesthetic-sourcing/tree/main/skills/niche-aesthetic-sourcing 安装这个技能。

也可下载 [Release 技能包](https://github.com/Fan-dev-sktch/niche-aesthetic-sourcing/releases/latest)，把其中 `niche-aesthetic-sourcing` 文件夹放入 `~/.codex/skills/`（Windows：`%USERPROFILE%\.codex\skills\`）。已存在同名技能时先保留旧版，再决定如何更新。安装后从下一轮对话调用。

技能本身是 Markdown 与模板。可选计算工具使用 Python 标准库，无第三方 Python 依赖；运行环境需提供搜索与原页读取能力。没有账号数据时可以继续公开研究，不会自动接通 Etsy、eBay 或付费服务。

在仓库根目录运行格式示例与合成订单示例：

```bash
python skills/niche-aesthetic-sourcing/scripts/check_batch.py skills/niche-aesthetic-sourcing/assets/discovery-example.json
python skills/niche-aesthetic-sourcing/scripts/analyze_trial.py examples/zero-orders.json
python -m unittest discover -s tests -v
```

`examples/` 与 `tests/fixtures/` 为明确标记的合成数据，用于展示行为，不是市场数据。


## 三个可直接复制的提示词

> 使用 $niche-aesthetic-sourcing，面向法国消费者，研究原创文具小物。我的优势是插画设计，预算 €300，不做角色授权产品。给最多 3 个候选，指出各自的购买理由、反证和最先要补的证据。

> 使用 $niche-aesthetic-sourcing，评估这款产品：[商品链接]。先看图片、规格、到手价和买家反馈，再按六项证据判断。未核实的信息保留未知，告诉我下一步最值得查什么。

> 使用 $niche-aesthetic-sourcing，我已有报价、样品记录和费用表：[提供资料]。检查整单成本与本轮资金上限，提出有限试卖的付款指标和停止条件。条件不足就列出缺口。

## 输出长什么样

以下完全是格式示意，**不是选品推荐，也不是真实研究结论**。

| 品类 | 值得查的理由 | 关键风险 | 当前状态 |
|---|---|---|---|
| 原创夜读页签套装 | 可围绕阅读用途检验设计价值 | 支付、正式报价和耐用性待核 | 继续查 |

下一步示意：核同规格替代品和实际购买反馈；在联系供应商的授权范围内，取得含目的地运费的报价。缺资料时，不提前算出“高利润”。

## 验证边界与可选工具

本地 CLI、预算约束与案例应用已检验；尚未用本项目自身的真实订单、正式报价、实物样品或已实现利润验证商业效果。公开案例用于检查取证和推理，不代表市场已验证或能盈利。账号工具也未自动接通。

本地工具可选：`check_batch.py` 检查记录、引用、矛盾和准备条件；`analyze_trial.py` 计算已提供的订单数据。它们不验证网页真伪、授权、审美因果或未来盈利。研究记录不自动授权采购、开户、发布或投放。

## 反馈与贡献

欢迎提交带来源、日期、口径和复现条件的 [Issue](https://github.com/Fan-dev-sktch/niche-aesthetic-sourcing/issues)。产品使用反例、预算漏项和真实试卖复盘，最能帮助改进这套判断。

[中文宣传文案](docs/promotion.md)可作为分享草稿；宣传措辞与技能的当前验证范围一致。
