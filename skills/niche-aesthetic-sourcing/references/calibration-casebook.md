# 真实案例与反例：2026-10-02校准

公开页面观察用于校准取证和推理，不是成交数据库、用户审美画像或成功率训练集。8个主商品来自4家卖家，另有1个零评论控制样本。五个案例用于形成规则，另外三个供独立应用检查。原轮图片未逐一评审；后续另记录实际看图的范围。未取得用户偏好评价，不声称已校准用户审美。

## 建规则的五个案例

| 来源 | 当时观察 | 合理用途 | 不当用途 |
|---|---|---|---|
| [Slow Living Stamps](https://www.stickiiclub.com/collections/all/products/slow-living-stamps) | 一张9×17cm，US$3.95，金箔/PVC/PET；2条商品页评论赞作者世界与质量 | 原创系列、收藏假设；注意工艺 | 标价当成交，品牌影响当纯审美溢价 |
| [Moon and Star Tabs](https://www.stickiiclub.com/collections/stationery/products/moon-and-star-tabs) | US$3.95降至2.60；评论提章节标记、打折购入 | 功能与外观共同价值、价格试验 | 原价证明接受高价，折扣购买当全价验证 |
| [The Guardians](https://www.stickiiclub.com/products/the-guardians) | US$3.95；2评论均署名Ira，一条报告第二次购买 | 复购线索、主题搭配用途 | 两评论当两个独立买家，文字推销量 |
| [Through the Trees 1](https://www.stickiiclub.com/products/through-the-trees-1) | US$3.95；评论称原本喜欢合作作者parakid | 区分作者、品牌、工艺、题材与设计 | 用户喜欢等于支付溢价 |
| [Etsy姓名贴](https://www.etsy.com/listing/1160827295/holographic-graffiti-vinyl-name-sticker) | $2.99起、多个长度字体；90条本listing评论、复购与电脑用途线索 | 个性化+视觉假设，先固定变体币种交付 | 全店56.2k当该品销量，起价当任意变体价 |

访问日不保证价格和评论实时。STICKII的USD由公开HTML默认币种确认；Etsy只有$符号，ISO币种未知。正文未显示购买/激励标签时保持未知。独立评估另使用功能标签、视觉预期及评论归属案例，本仓库提供案例摘要与第一方链接，未随附完整原始采集记录；重查时保存原文观察，不先提供预期答案。非随机小样本不能概括整个市场。

## 平台与成本快照

以下为当日官方页面记录，实际决策前重查：

- [Etsy国家](https://help.etsy.com/hc/en-us/articles/115015710408-Countries-Eligible-for-Etsy-Payments)：大陆不能开新店，France支持；店铺银行国家与账户匹配。用户实际资格未知。
- [创意标准](https://www.etsy.com/legal/creativity/)、[生产伙伴](https://help.etsy.com/hc/en-us/articles/360000336547-Working-with-Production-Partners-on-Etsy)、[手作用材](https://help.etsy.com/hc/en-us/articles/32404729668887-What-Craft-and-Party-Supplies-am-I-Allowed-to-Sell)：原创外包与普通批发分开；贴纸是纸艺手作用材例子，不能一概禁止拿货贴纸。
- [基础费用](https://www.etsy.com/legal/fees/)、[支付处理](https://help.etsy.com/hc/en-gb/articles/115015628847-What-are-Payment-Processing-Fees-for-Selling-on-Etsy)、[监管运营](https://help.etsy.com/hc/fr/articles/1500011073202-Que-sont-les-frais-d-exploitation-r%C3%A9glementaires)：France快照US$0.20上架/逐件续刊、6.5%交易、4%+€0.30支付、1.14%监管运营；适用开店费、税、广告和汇兑另计，各用自己的基数，不能套其他国家。
- [Shopify Payments](https://help.shopify.com/en/manual/payments/shopify-payments/supported-countries)：France支持，大陆不在名单；不等于大陆不能建站，第三方收款单核。[营销](https://help.shopify.com/en/manual/promoting-marketing/developing-a-marketing-plan)需要具体获客办法。
- [eBay中国](https://www.ebay.cn/newcms/Home/topic/515)：个人可入驻，企业招商另有条件；注册、收款、额度和跨境权限分开。
- [Amazon中国](https://sell.amazon.com/zh/global-selling/china)：公司营业执照要求，不接受个体工商户营业执照；美国个人卖家通用说明不可套用。
- [Sticker Mule样品](https://www.stickermule.com/faqs/stickermule/can-i-see-samples-before-i-buy)：公开自有设计样品10枚US$9并称免费运输；未绑定我们的尺寸、材质、目的地及税，只作打样预算线索。
- [StickerApp最低订单](https://stickerapp.com/support/placing-orders/what-is-the-minimum-order-for-custom-stickers)：亮面白vinyl异形公开最低US$26、整张US$28，数量随尺寸；不是固定每枚制造成本。未保存选中规格的配置页价格不用于盈利计算。

两个供应商均没有给我们方案的完整落地报价，也未下单或验样。这些页面足够制定询价字段，不足以通过整单利润门槛。

## 现成技能审查

5个真实外部SKILL.md、4个本地技能；仅借鉴数据/判断分离、ID去重、日期缓存与阶段交接，没有复制外部代码或安装原方案。

- [Nexscope市场空缺](https://github.com/nexscope-ai/eCommerce-Skills/blob/ee0fb29433d02ccc22e3e6cea9ab4586d49fd42e/market-gap-analysis/SKILL.md)及其Etsy技能是通用清单，缺数据/晋级规则。
- [AronLEEdev管线](https://github.com/AronLEEdev/product-opportunity-finder-skill/blob/535c15bf9d768d46b01bb711f2e7145a88a89f1f/SKILL.md)有去重缓存，但以价格重量代理利润、缺值给默认分；依赖登录浏览器、Helium10和远端代码，不采用原方案。
- OmniMCP、astDeniss审查版本无明确许可证，不导入资源。本地ab-testing的p值解释有误，本技能单独写统计边界，不照搬。

上方外部链接固定到审查时的提交；本仓库仅含方法摘要，没有导入外部代码或完整审查日志。方法参考不等于执行了原方案或取得其服务数据。

## 扩展与实际视觉评审

同日新增[三路径六商品](crosscategory-cases.md)：通用收藏展示、通用娃衣、微缩场景。使用机制可以迁移，权属、功能适配和履约仍需逐款核查；它们不构成蓝海或盈利验证。

2026-10-02的浏览器评审实际查看了Slow Living Stamps、Moon and Star Tabs及anniyell小卡扣件的主图像素。前者的邮票边缘、乡居叙事与色彩系列可提出收藏假设；后者有对称页签结构及黑底金色月星，用途不同，两者不能直接当审美溢价对照。金箔/材质来自商品描述，图片不验证耐久和做工。

[anniyell扣件](https://anniyell.com/products/b-grade-have-you-seen-them-acrylic-photocard-holder)实际主图有暖桃色边框、醒目文字、猫/花图案和橙色珠链，背景使用草地、格纹布及星形道具。区分产品造型和拍摄氛围；不凭图判断卡套适配或权属。浏览器France/EUR页面所选A-GRADE显示€13.95及Add to cart；研究快照此前USD15与Sold out。保留地区/变体/读取差异，不把二者当价格上涨或需求变化。

其余五件跨品类商品仍未实际看图。商品审美与用户偏好没有因此全部验收。本仓库保留观察摘要及来源链接，未随附完整采集日志；实际决策前须重查。官方工具入口和指定规格公开价见[渠道与试卖](channels-and-trials.md)。

## 增长与套装成本复核：2026-10-02

以下是公开来源观察，用于检验推理；未取得我方订单、样品或完整利润。

- [Etsy春夏2026报告](https://www.etsy.com/seller-handbook/article/1473931456647)的journal charm搜索+395%，数据截至2026-02-10，近三个月对上一年同期，美国登录用户的标准化搜索。不能据此认定十月仍快增长，也不能归给某个单品的销量。
- [Pinterest爱好报告](https://newsroom.pinterest.com/en-ca/news/2026-pinterest-hobbies-trend-report/)于2026-08-25发布，clay bag charms +1499%、sashiko ideas +1509%的口径是全球文本搜索、2026年5月对2025年5月。绝对基数未披露；不是八月实时增长，也不是成品付款。
- [Google Trends方法](https://support.google.com/trends/answer/4365533?hl=en)说明相对指数、采样和低量限制。核验时保留实际查询、地区与完整期间；能导出时保存原始导出，否则保留截图或原值及读取限制。历史报告、不同关键词和不同平台不可拼成一个增长率。
- [Wren图案包](https://wrenbirdarts.com/products/visible-mending-transfers-value-pack)挂牌USD36对应16片、约4×5英寸，工具不含。拟做同尺寸8片时，应先按数量核对；不能沿用16片价格来暗示我方高利润。
- [Sulky水溶纸](https://sulky.com/sulky-sticky-fabrisolvy-stabilizer-white-85-x-11-pkg-12-sheets)USD15.99对应12张8.5×11英寸。保守每张出2片时，8片的纸材消耗约USD5.33；裁切、打印、设计、劳动、失败损耗、包装、配送、税费、获客与退赔仍未知。纸材消耗不是成品成本；整包采购及开发测试另算现金。

这些观察支持检查观察期、对齐规格与保留未知费用，不构成某品类永久排除规则或盈利承诺。公开链接和观察摘要供重查，不包含私人账号资料；价格和政策在实际决策前重核。
