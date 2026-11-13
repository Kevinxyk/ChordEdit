from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

import torch
from diffusers import AutoencoderKL, EulerDiscreteScheduler, StableDiffusionPipeline, UNet2DConditionModel
from transformers import AutoTokenizer, CLIPTextModel


LOGGER = logging.getLogger("generate_sources")
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_MANIFEST = SCRIPT_DIR / "source_generation_manifest.jsonl"
DEFAULT_MODEL_ROOT = Path("/root/models/sd-turbo")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch-generate canonical source images for ChordEdit cases.")
    parser.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--device", type=str, default=None, help="Torch device, e.g. cuda:0 or cpu.")
    parser.add_argument("--dtype", choices=["fp16", "fp32"], default="fp16")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--max-samples", type=int, default=None)
    return parser.parse_args()


def read_manifest(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_num, raw_line in enumerate(handle, start=1):
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{line_num}: {exc}") from exc
            records.append(record)
    return records


def resolve_repo_path(path_value: str | Path) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def parse_resolution(value: str) -> tuple[int, int]:
    try:
        width, height = (int(part) for part in value.lower().split("x", maxsplit=1))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Resolution must look like 512x512, got {value!r}") from exc
    return width, height


def load_pipeline(model_root: Path, device: str, dtype: torch.dtype) -> StableDiffusionPipeline:
    component_root = model_root.expanduser().resolve()
    unet = UNet2DConditionModel.from_pretrained(component_root / "unet", torch_dtype=dtype)
    vae = AutoencoderKL.from_pretrained(component_root / "vae", torch_dtype=dtype)
    tokenizer = AutoTokenizer.from_pretrained(component_root / "tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(component_root / "text_encoder", torch_dtype=dtype)
    scheduler = EulerDiscreteScheduler.from_pretrained(component_root / "scheduler")

    pipeline = StableDiffusionPipeline(
        vae=vae,
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        unet=unet,
        scheduler=scheduler,
        safety_checker=None,
        feature_extractor=None,
        requires_safety_checker=False,
    )
    pipeline = pipeline.to(device)
    pipeline.set_progress_bar_config(disable=True)
    return pipeline


def update_source_metadata(
    metadata_path: Path,
    *,
    model_root: Path,
    steps: int,
    seed: int,
    resolution: str,
) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["status"] = "generated"
    metadata["source_generator"] = {
        "model": str(model_root),
        "steps": steps,
        "seed": seed,
        "resolution": resolution,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    metadata["source_image_size"] = resolution
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate_sources(
    pipeline: StableDiffusionPipeline,
    records: Iterable[Dict[str, Any]],
    *,
    model_root: Path,
    device: str,
    overwrite: bool,
) -> tuple[int, int]:
    generated = 0
    skipped = 0
    for record in records:
        if record.get("action") != "generate_source":
            LOGGER.info("Skipping %s (%s)", record.get("case_id"), record.get("action"))
            skipped += 1
            continue

        source_path = resolve_repo_path(record["source_image_path"])
        metadata_path = resolve_repo_path(record["source_metadata_path"])
        if source_path.exists() and not overwrite:
            LOGGER.info("Skipping existing source image %s", source_path)
            skipped += 1
            continue

        width, height = parse_resolution(record["resolution"])
        seed = int(record["seed"])
        steps = int(record.get("generator_steps") or 1)
        generator = torch.Generator(device=device).manual_seed(seed)
        result = pipeline(
            prompt=record["source_prompt"],
            num_inference_steps=steps,
            guidance_scale=0.0,
            generator=generator,
            width=width,
            height=height,
        )
        source_path.parent.mkdir(parents=True, exist_ok=True)
        result.images[0].convert("RGB").save(source_path)
        update_source_metadata(
            metadata_path,
            model_root=model_root,
            steps=steps,
            seed=seed,
            resolution=record["resolution"],
        )
        generated += 1
        LOGGER.info("Generated %s -> %s", record["case_id"], source_path)
    return generated, skipped


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    manifest_path = args.manifest.expanduser().resolve()
    records = read_manifest(manifest_path)
    records = [record for record in records if record.get("action") == "generate_source"]
    if args.max_samples is not None:
        records = records[: args.max_samples]
    if not records:
        LOGGER.info("No generated-source records found in %s", manifest_path)
        return

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if args.dtype == "fp16" else torch.float32
    LOGGER.info("Loading source-generation pipeline from %s on %s", args.model_root, device)
    pipeline = load_pipeline(args.model_root, device, dtype)
    generated, skipped = generate_sources(
        pipeline,
        records,
        model_root=args.model_root,
        device=device,
        overwrite=args.overwrite,
    )
    LOGGER.info("Finished source generation: generated=%d skipped=%d", generated, skipped)


if __name__ == "__main__":
    main()
