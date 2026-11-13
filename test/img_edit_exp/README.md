# Image asset layout

This directory contains the image assets and run records for the ChordEdit testcase experiments.

## Layout

```text
img_edit_exp/
├── assets/source/{case_id}/
│   ├── source.png
│   ├── meta.jsonl
│   └── source_metadata.json
├── runs/{run_id}/
│   ├── outputs/{case_id}/seed_{seed}.png
│   └── run_records.jsonl
├── test_metadata.json
├── evaluation_template.jsonl
└── evaluation.jsonl
```

The first prepared run is `exp_001_run_001`. Keep one canonical source image per case and never overwrite it when testing another seed or model. Put those outputs under a new `run_id` instead.

Each case directory already has a `meta.jsonl` compatible with the project's existing example loader. For generated source images, fill `source_metadata.json` using `source_metadata_template.json`. The official webpage is only prompt/case provenance; its screenshot is not used as the canonical source image. All 30 source images are therefore generated at 512x512, with the first three retaining `prompt_source=official_web_example`. The server-side batch generation plan is `source_generation_manifest.jsonl`.

After the repository is available on the server, run:

```bash
python test/img_edit_exp/generate_sources.py \
  --model-root /root/models/sd-turbo \
  --manifest test/img_edit_exp/source_generation_manifest.jsonl
```

The script loads the model once, generates the `generate_source` records, saves each image as `source.png`, and updates its `source_metadata.json`. Existing images are skipped unless `--overwrite` is supplied.

