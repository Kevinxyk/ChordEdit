# Testcase evaluation protocol

> Kevin  
> 26/11/13  

## 1. 文档说明

本文档规定 ChordEdit testcase 的实验记录、人工评价和时间统计方式。

当前这批 30 个 testcase 被定义为第一批实验：

```text
batch_id: exp_001
batch_name: initial-chordedit-case-batch
created_at: 2026-11-13T18:57:26+08:00
timezone: Asia/Shanghai
status: designed
```

case 设计和评价结果分开保存：

- 设计 metadata：`test/img_edit_exp/test_metadata.json`
- 评价结果：`test/img_edit_exp/evaluation.jsonl`
- 评价填写模板：`test/img_edit_exp/evaluation_template.jsonl`
- runner 自动写入的运行记录：`run_records.jsonl`（也可以通过命令行改到指定路径）
- 本实验批次：`exp_001`

`test_metadata.json` 描述 case 是什么；`evaluation.jsonl` 描述某一次运行得到什么结果。相同 case 可以因为不同 seed、模型版本或评价者而出现多条 evaluation 记录。

批次编号按 `exp_001`、`exp_002`、`exp_003` 顺序递增；不同实验者不要复用已有 `batch_id`。同一批次内，每次模型运行只递增 `run_id`，这样可以区分模型版本、seed、GPU 和评价者，而不必复制一份 case 设计。

## 2. 图片资产与目录

图片采用“固定原图、运行隔离、seed 分文件”的规则：

```text
test/img_edit_exp/
├── assets/source/{case_id}/source.png
├── assets/source/{case_id}/meta.jsonl
├── assets/source/{case_id}/source_metadata.json
└── runs/{run_id}/
    ├── outputs/{case_id}/seed_{seed}.png
    └── run_records.jsonl
```

- `assets/source/{case_id}/source.png` 或 `source_gemini.jpg`：该 case 的唯一 canonical source image，后续不同 run 和 seed 都复用它；
- `assets/source/{case_id}/meta.jsonl`：每个 case 的独立 metadata，字段兼容项目现有 `images/<case>/meta.jsonl`，可直接被本地前端数据加载器识别；
- `source_metadata.json`：记录原图来源、source prompt、原图生成模型、source seed、分辨率和创建时间；
- `runs/{run_id}/outputs/{case_id}/seed_{seed}.png`：某次运行的编辑结果，不能写回 source 目录；
- `run_records.jsonl`：该次运行的自动时间与状态记录；
- `evaluation.jsonl`：人工评分和观察结果，可引用对应的 `run_id`、`case_id` 和 seed。

`prompt_source=official_web_example` 只表示 prompt 或案例语义来自官网，不表示官网截图就是实验原图。当前 `ai_A1`～`ai_E3` 是按时间顺序导入的 Gemini `1024×1024` 图片，其余 case 由服务器 SD-Turbo 生成；实际尺寸、来源和文件名必须记录在 metadata 中。不要把 source image 每次复制到 run 目录，否则后续很难判断不同运行是否使用了完全相同的输入。

当前已准备第一批 `exp_001` 的 source 目录和 `exp_001_run_001` 的 output 目录；另有 `source_generation_manifest.jsonl` 供服务器批量生成 source image，具体路径模板以 `test_metadata.json` 中的 `image_storage` 为准。

### 2.1 source quality gate

生成图片后，必须先人工检查它是否基本符合 `source_prompt`，再开始 ChordEdit 编辑实验。检查结果写入每个 case 的 `source_metadata.json` 和 `meta.jsonl`：

```json
{
  "source_validated": true,
  "source_quality_note": "主体、构图和主要属性符合 source prompt。",
  "source_validated_by": "Kevin",
  "source_validated_at": "2026-11-13T20:00:00+08:00"
}
```

`source_validated=true` 才能进入正式评价；`null` 表示尚未检查，`false` 表示 source 不合格，应重新生成或剔除。source 不合格时，不应把后续编辑失败归因于 ChordEdit。

## 3. 评价标准

### 3.1 基础检查

以下两项是二值记录，不参与 0～5 分平均：

1. `output_exists`：是否成功得到输出图片。
2. `edit_direction_correct`：输出是否朝 target prompt 的方向改变。

### 3.2 五维主观评分

每项使用 0～5 分：

| 维度 | 含义 |
|---|---|
| `edit_fidelity` | 指定属性或对象是否准确完成编辑 |
| `background_preservation` | 未要求修改的背景是否保持 |
| `identity_consistency` | 主体身份、姿态、构图是否保持 |
| `structure_consistency` | 手指、遮挡、接触、反射等结构是否自然 |
| `prompt_following` | 输出是否完整遵循 target prompt |

分数含义：

- `0`：编辑失败或图片不可用；
- `1`：几乎没有完成目标，或出现严重结构错误；
- `2`：部分完成，但语义漂移或伪影明显；
- `3`：基本完成，有可见瑕疵；
- `4`：编辑准确，只有轻微瑕疵；
- `5`：编辑准确，未指定内容和结构也保持良好。

### 3.3 备注和失败模式

`failure_modes` 使用可重复的短标签，建议从以下集合选择：

```text
no_output
target_not_applied
wrong_region
background_leakage
identity_drift
pose_drift
geometry_artifact
hand_artifact
occlusion_error
reflection_error
text_error
style_overwrite
over_editing
under_editing
```

`notes` 用于记录主观评分无法表达的现象，例如“颜色改对了，但杯面拉花完全消失”。

## 4. 时间与运行信息

所有时间使用带时区的 ISO 8601 格式，例如：

```text
2026-11-13T14:30:00+08:00
```

### 4.1 批次级字段

批次级字段只写一次，保存在 `test_metadata.json` 的 `experiment_batch` 中：

```json
{
  "batch_id": "exp_001",
  "batch_name": "initial-chordedit-case-batch",
  "created_at": "2026-11-13T18:57:26+08:00",
  "timezone": "Asia/Shanghai",
  "status": "designed"
}
```

### 4.2 每次运行字段

每一次运行或每一个 case 的结果都应记录：

| 字段 | 说明 |
|---|---|
| `batch_id` | 所属实验批次，例如 `exp_001` |
| `run_id` | 一次连续运行的编号，例如 `exp_001_run_001` |
| `record_type` | case 记录为 `case`；整次运行汇总为 `run_summary` |
| `case_id` | 对应 testcase |
| `evaluator` | 人工评价者 |
| `started_at` | 本次运行开始时间 |
| `finished_at` | 本次运行结束时间 |
| `elapsed_seconds` | `finished_at - started_at` |
| `model_load_started_at` | 模型加载开始时间，可选 |
| `model_load_finished_at` | 模型加载结束时间，可选 |
| `model_load_seconds` | 模型加载耗时，可选 |
| `inference_started_at` | 推理开始时间 |
| `inference_finished_at` | 推理结束时间 |
| `inference_seconds` | 单个 case 推理耗时 |
| `seed` | 随机种子 |
| `device` | 例如 `cuda:0` |
| `gpu_name` | 实际 GPU 型号 |
| `software_versions` | torch、diffusers、ChordEdit commit 等 |
| `output_path` | 输出图片路径 |
| `status` | `saved`、`skipped_existing`、`input_error`、`inference_error` 或 `no_output` |
| `error` | 运行异常的简短文本；正常完成时为 `null` |

`model_load_seconds` 和 `inference_seconds` 必须分开。模型第一次加载的时间不能当作每张图片的推理速度；批量实验中可以让同一个 `run_id` 共享一次模型加载记录。

### 4.3 runner 自动记录

当前 `run_pie_bench.py` 已支持自动写入上述时间字段。默认情况下，每次运行在 `--export-root` 下追加 `run_records.jsonl`；也可以显式指定输出位置：

```bash
python run_pie_bench.py \
  --model-root /path/to/sd-turbo \
  --pie-root /path/to/pie_bench \
  --experiment-batch-id exp_001 \
  --timing-output /path/to/test/img_edit_exp/run_records.jsonl
```

每个 case 写一行 JSON，运行结束时再追加一行 `record_type=run_summary` 的整批汇总，不覆盖历史记录。`run_id` 默认带有本地时区时间戳，也可以手动传入固定编号。runner 会自动记录模型加载、单 case 推理、GPU 同步后的耗时、整批耗时、设备、GPU 型号、软件版本和 Git commit；人工评价字段保留为 `null`，之后再补填到评价文件。

时间含义需要区分：

- `model_load_seconds`：从加载本地模型组件开始，到 pipeline 可用为止；
- `inference_seconds`：单个 case 的 pipeline 调用耗时，CUDA 设备会在前后同步；
- `elapsed_seconds`：该 case 从读入、推理到输出保存的总耗时，因此通常略大于 `inference_seconds`。

## 5. 评价流程

1. 固定 `case_id`、source image、source prompt、target prompt 和 seed。
2. 启动一次实验；runner 自动记录 `run_id`、设备、软件版本和时间。
3. 生成输出图片，记录推理开始/结束时间。
4. 先填写 `output_exists` 和 `edit_direction_correct`。
5. 查看 source/output 后填写五个 0～5 分维度。
6. 记录失败模式和备注。
7. 重复 seed 时追加新行，不覆盖旧结果。

前期建议人工填写 `evaluation.jsonl`。后续 case 数量和重复实验增加后，可以在前端增加独立的 annotation 面板；面板只写 evaluation 文件，不修改 testcase 设计 metadata。

## 6. 汇总规则

- `normal`、`extreme`、`boundary` 分开统计；
- `special_challenge`（文字、手部、全局风格等）单独列出；
- `AI-designed` 与 Kevin 原始 case 可以分别统计；
- `ai_E2` 作为 `case_2_3` 的 prompt variant，不与原 case 合并为一个无区分的平均值；
- `output_exists=false` 的记录不计算主观分数平均，但保留在失败率中；
- 不使用一个总平均分掩盖 boundary case 的失败。

## 7. 当前批次状态

`exp_001` 当前处于 `designed` 状态：metadata 和评价模板已准备，图片和实际运行结果尚未写入。生成第一批图片并完成人工评价后，将状态改为 `evaluated`，所有后续补充实验使用新的 `run_id` 或新的 `batch_id`。
