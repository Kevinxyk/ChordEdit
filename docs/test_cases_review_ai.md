# Testcase design review（AI review）

> 本文件是 AI 对 `docs/test_cases_design_kevin.md` 的 review，不修改原始 design 文档。
> 原始 case 的作者仍记为 Kevin；新增 case 和本文建议均明确标注为 AI。

## 总体判断

现有设计方向是合理的：用普通 case 检查局部编辑，用极端 case 检查语义和结构压力，用边界 case 检查超出 ChordEdit 适用范围时的行为。这个分层比只看最终图片好，因为 ChordEdit 的目标更接近“保持大部分内容，只改变指定语义”。

当前设计共有 15 个 Kevin case，另有 15 个 AI-designed case。它们覆盖了颜色、附件、物体替换、状态变化、空间关系、数量变化、人物属性、全局光照、风格、文字和反射一致性。

## 需要修正或单独标注的地方

1. `case_1_2` 的 `stripe car` 虽然不够自然，但它来自网页官方示例，因此 metadata 保留网页原始 prompt。同时增加语义解释，说明我们把它理解为“车身条纹变化”，这样既能复现官方 case，也能进行可解释的评价。

2. `case_1_3` 的英文语法确实有问题，但它来自网页示例；网页实际意图是 coffee 表面的拉花图案变化。因此 metadata 保留原始句子，并额外记录“改变杯面拉花形状”的 semantic intent。

3. `case_1_5` 的开合状态变化不一定是普通 case。它会改变笔记本的可见表面和几何结构，建议作为普通 case 的上界，单独记录结构变化伪影。

4. `case_2_1` 的 “green cat” 很不自然。metadata 保留了原意，但改写为 “a cat with green fur”，并标记为高风险颜色/语义编辑。

5. `case_2_5` 原本的 `whiping girl` 是拼写错误；根据 Kevin 的确认，目标应为 “a crying girl”。metadata 已改为从 smiling 到 crying 的表情变化。

6. `case_2_6` 是文字生成压力测试。它不属于 boundary：编辑区域仍然局部，只是文字渲染本身困难，因此保留在 extreme 下并标记为 `special_challenge`，单独报告书名可读性、拼写和字体布局。

7. `case_3_1`、`case_3_3`、`case_3_4` 是 Kevin 有意设计的超大语义差距 boundary case。它们可以保留，并标记 `stress_only`；不能用来否定 ChordEdit 在局部编辑上的效果。

8. `AI-case E2` 与 Kevin 的 `case_2_3` 使用相同的编辑意图，但可以理解为对原 prompt 的续写和规范化，而不是完全无意义的重复。metadata 将其标记为 `derived_from: case_2_3`；汇总统计时建议把它作为 prompt variant 单独列出，不与原 case 简单平均。

## 推荐的统一评价维度

每个 case 不要只记录“改成功没有”，建议分别记录：

- `edit_fidelity`：目标属性是否真的改变；
- `background_preservation`：未指定区域是否保持；
- `identity_consistency`：主体身份、姿态、构图是否保持；
- `structure_consistency`：手、遮挡、接触关系、反射等是否自然；
- `prompt_following`：生成结果是否遵循 target prompt；
- `failure_mode`：颜色泄漏、背景重绘、结构畸变、文本错误或目标未改变。

其中局部编辑和全局编辑不应共用一个总分。全局光照、季节和风格变化天然会降低像素级背景相似度，这不等同于编辑失败。

## 主观评分的保存方式（AI suggestion）

建议把“评分标准”放进 `test_metadata.json`，但不要把每次实验的具体分数直接写回设计 metadata。设计 metadata 应保持稳定，具体结果另存为 `evaluation.jsonl` 或 `evaluation.json`，这样同一个 case 可以记录多个 seed、多个模型或多名评价者。

建议使用 0～5 分：

- `edit_fidelity`：目标编辑是否发生，0 为完全失败，5 为准确完成；
- `background_preservation`：未指定区域保持程度；
- `identity_consistency`：主体身份、姿态和构图保持程度；
- `structure_consistency`：手指、遮挡、接触、反射等结构自然程度；
- `prompt_following`：输出是否符合 target prompt。

前期建议人工填写 evaluation 文件，成本低且便于保留解释性备注。等 case 数量和重复 seed 增加后，再在前端增加一个独立的 annotation 面板，保存到 evaluation 文件；不要让前端直接改写 testcase 设计 metadata。

## 推荐实验流程（AI suggestion）

1. 先为每个 case 准备一张严格符合 `source_prompt` 的 source image。
2. 使用固定 canonical seed `42`，再用 `43`、`44` 做重复实验。
3. 普通和极端 case 优先使用 512×512；边界 case 单独标注，不与普通 case 求平均。
4. 每个 case 生成后保存 source image、target prompt、输出图、seed 和人工观察结果。
5. 最终报告至少给出逐 case 结果，不只给一个平均分。

## metadata 与代码的关系

设计文档指定的总索引位于 `test/img_edit_exp/test_metadata.json`，本次已按此要求生成。当前 `app.py` 和 `utils.py` 加载示例时读取的是 `images/<case>/meta.jsonl`，字段为 `original_prompt`、`edited_prompt`、`edit_prompt`。因此总 metadata 中同时保留了可读的设计字段和运行所需的 edit 字段，后续生成图片时可以直接转换为前端目录格式。
