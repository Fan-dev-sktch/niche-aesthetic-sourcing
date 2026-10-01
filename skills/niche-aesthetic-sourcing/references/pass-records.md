# 通过记录的字段

门槛通常保持 `unknown`；只有实际证据充分时填写 `pass`。每门的 `details` 保存判断所需字段，数字来自原始记录，不从模板默认生成。检查器负责发现字段和口径矛盾，人工仍须验证内容、代表性与可比性。

## demand

- `target_country` 与批次市场一致。
- `measurement_scope` 为 `sku`、`defined_niche` 或 `purchase_experiment`；填写 `sample_size`、ISO格式 `period_start / period_end`、事先记录的 `decision_threshold` 和 `threshold_met: true`。
- 引用的销售/交易/购买试验来源，`data_scope` 使用以上范围之一，`market` 与目标市场一致。至少有支付指标：`metrics.name` 为 `units_sold / paid_orders / purchases`，`basis` 为 `transaction / platform_sales_data / purchase_experiment`，`scope` 为对应范围。
- `defined_niche` 需在来源观察中说明包括与排除哪些产品，防止把全店交易换名。两条评论没有资格被填成交易样本。

## aesthetic_premium

- `price_basis: transaction`；同一明确 `currency`；正值 `design_price / baseline_price`、`sample_size`。
- `matched_controls` 明确列出 `material, size, function, brand, market, delivery`；记录如何匹配和未消除因素，不能仅写字段名就视作证实。
- `confound_reviewed: true`，明确 `decision_threshold`、`threshold_met: true`。
- 对照/购买试验来源至少有 `median_sold_price` 或 `experiment_paid_price` 指标，`basis: transaction`。只有挂牌价格保持未知。

## competition_gap

记录与批次一致的 `target_country / target_channel`、检查过的 `direct_substitutes_examined`、`new_entrant_evidence_reviewed: true`、具体 `gap_statement`、`coverage_limitations`，以及 `unmet_need_source_ids / comparator_source_ids`。来源需支撑客群缺口与替代比较，不能把关键词搜索页数量改名为有效竞品数。

## unit_economics

记录明确 `currency`、`working_capital_checked: true`、非负 `contribution_margin_floor`。引用真实 `supplier_quote` 和 `cost_model`。schema 1.1/1.2另要求 `fulfillment_labor / design_allocated`，与其他费用不重算。

`components` 中有 `revenue, purchase, packaging, international_shipping, platform_payment, taxes, cac, returns, other_variable`。每项包含 `low / high / source_ids / basis`。零成本也需说明适用原因和来源；不能用 0 隐藏未取报价、未知税费或未来获客成本。

检查器计算 `revenue.low − 所有成本.high`，低于记录的贡献门槛时拒绝通过。模型需说明收入及税费责任边界、折扣、货币转换和国内物流等归属，避免漏计或重复计算。

## rights_and_channel

引用产品专属 `rights_document` 与 `channel_policy`。市场与渠道一致；`rights_basis` 是实际核查的 `original_design_reviewed / licensed_verified / legal_review_recorded` 之一。`final_design_assets_reviewed / marketing_assets_reviewed / channel_eligibility_reviewed` 均完成。平台规则文档不能替代角色授权或商品原创材料。

## fulfillment_fit

引用实际 `fulfillment_test`；`sample_checked / fit_quality_checked / delivery_plan_checked` 均完成，记录 `test_date / test_result`。报价、卖家宣传与规格表不足以证明试样和履约通过。

## pilot_ready

国家与渠道明确、六门通过后记录 `pilot`：`audience / duration / variables / success_criteria / stop_criteria / authorization_required / budget_cap / currency`。通过检查只表明声明材料满足结构条件，不授权自动执行，不确认盈利，也不能抵消已发现的事实矛盾。

schema 1.1还要求下列渠道资格和获客字段。旧schema 1.0的结构检查仍兼容，但不能据此补出旧记录缺失的真实资格与获客结果。

## schema 1.1：channel_access

`test_ready / pilot_ready` 的 scope明确 `seller_country / seller_entity / target_country / target_channel / ship_from`。

候选的 `channel_access` 有 `status: pass`，与scope一致的卖家国家、主体和渠道，`seller_verification_reviewed / payout_reviewed: true`，以及具体 `rationale`。`source_ids` 引用 `channel_policy`；`seller_evidence_source_ids` 引用实际核查的 `seller_account_record`。只读了支持国家名单不能代替用户真实资格。

资格记录只存状态、适用条件和本地引用，不在公开报告保存证件号码、银行号码等敏感信息。用户未提供记录就保持未知；不为通过检查擅自开户。

## schema 1.1：test_ready

`rights_and_channel / fulfillment_fit` 通过；其余门可以未知，但已失败的方案需先调整。试验准备不要求预先证明需求、溢价或低竞争。

`test_costs` 保存 `currency / boundary / quote_source_ids / model_source_ids / acquisition_cap_per_order / max_affordable_loss / working_capital_checked`。报价引用真实 `supplier_quote`，公开最低价应另用 `supplier_price_listing`，不能冒充实际报价。

`components` 保存 `revenue / purchase / packaging / international_shipping / platform_payment / taxes / returns / other_variable / fulfillment_labor / design_allocated` 各项 `low / high / basis / source_ids`。完整区间可以是研究情景，不据此认定实际盈利。

保守一单亏损加该单获客费用上限不得超过整个可承受损失；批量库存、固定承诺和多订单累计损失仍需在计划中核查，结构检查的单订单保护不能替代总体资金审查。

`pilot` 除普通计划字段，还记录 `qualified_visit_target / acquisition_channel`；预算不超过声明可承受损失，与成本币种一致。`authorization_required` 写实际会话授权状态及待授权动作，不自动覆盖会话决定。

## schema 1.1：pilot_ready acquisition

`acquisition` 保存 `status: pass / channel / measurement_basis / qualified_unique_visitors / paid_buyers / paid_orders / investment_total / investment_basis / period_start / period_end / decision_threshold / threshold_met / source_ids`。

目标访问者、付费买家与订单口径一致、均为正值，买家不多于访问，订单不少于买家。引用目标市场、具体SKU/定义品类/试验的实际交易或购买结果。现金和劳动投入说明边界；零投入仍有理由。记录事先标准和实际是否满足，不能以点赞或泛店铺销量替代。

获客源有对应且一致的 `paid_orders` 指标，不能只写来源类型。若多个来源，先生成可追踪、去重后的队列汇总记录；不要直接加总订单。显式渠道不得与目标销售渠道矛盾。`investment_total`按整单成本币种记录；若另有`currency`字段须一致，pilot预算也与成本币种一致。

已完成需求/获客的期间和样品检查日不得晚于账本`as_of`。正审美溢价需设计成交价高于匹配基础款；单有价差方向仍不能代替可比性和因果检验。

## schema 1.2：当前预算与整体资金

新批次的`test_ready / pilot_ready`要求`scope.budget / currency`是最新明确的用户现金上限。`pilot.budget_cap / currency`不得超出或矛盾；旧schema显式写了预算/币种时也检查冲突。未知预算不阻止发现或验证阶段。

`funding_plan`字段见 [资金模板](../assets/funding-plan-template.json)：同币种、`max_orders`正整数、`max_affordable_loss`、`boundary`、`zero_revenue_zero_recovery: true`及`no_double_counting_reviewed: true`。`cash_components`六组恰为`inventory / samples_setup / acquisition / fulfillment_reserve / fees_taxes_returns_reserve / other_commitments`；每组`high / basis / source_ids`，零值也有适用理由。

库存另填非负整数`quantity / quote_minimum_quantity`和`unit_cash_high / inbound_cash_high`；数量不得小于报价MOQ，库存high覆盖其乘积加入库费用，引用实际`supplier_quote`。`pilot.acquisition_budget_cap`是整轮现金获客上限，资金获客组不得少于它。所有引用需可用。逐单成本和总资金分别核，不重复扣设计固定成本。

脚本求六组high之和，拒绝超用户预算、试卖预算或可承受亏损。逐单记录的亏损上限也须覆盖整轮承诺。`max_orders`用于设履约停止上限，各储备的数量、期间、费率和结算依据由原始记录逐项核查，不能仅勾选完成。数值填得不真实或遗漏项，结构通过仍无效。

实际成交来源的market、币种和统计范围不得与判断明确冲突。1.2审美溢价记录必须有目标市场和同币种的正成交价格指标；外币/原始订单先保存，再建立说明汇率、去重及归属的派生对照记录。门槛引用派生记录，不能默默混算。
