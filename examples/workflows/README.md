# Tiny ComfyUI test workflows

These workflows are intentionally public and credential-free. Load one by dragging its `.json` file into ComfyUI, then queue it.

| Workflow | What it verifies | Download size |
| --- | --- | --- |
| `auto-model-finder-scan.json` | Workflow scan, Hugging Face lookup, and discovered repository | no download |
| `civitai-demo.json` | CivitAI checkpoint download, load, and 512×512 image preview | about 2.0 GB |
| `hf-demo.json` | Hugging Face checkpoint download, load, and 512×512 image preview | about 2.1 GB |

## Full image-generation smoke test

`hf-demo.json` and `civitai-demo.json` are complete, one-click ComfyUI graphs. Each downloader returns a filename to **Load Downloaded Checkpoint**, which loads the checkpoint's model, CLIP, and VAE before previewing a 512×512 image. They use 20 Euler/exponential steps with CFG 20 and denoise 1. The first run can take longer on CPU.

## Run the auto-model-finder flow from scratch

Before loading `auto-model-finder-scan.json`, delete `model.safetensors` from the selected `checkpoints` directory. The unconnected **Load Checkpoint** node is deliberate: it gives the model finder a missing filename to scan without attempting to load it. Queue the workflow, then inspect the three previews: repository ID, filename, and target model path.

The finder no longer has a free-text model-name input. It scans all model-like filenames in the workflow that are absent from ComfyUI's configured model paths, searches Hugging Face for each filename, and populates **select_model** with every resolved filename. Select one result to update the three outputs. The fixture deliberately does not connect its result to a downloader; inspect the selected repository before deciding whether to download it. The download workflows above remain the deterministic, small end-to-end tests.

## Loading a downloaded checkpoint

**Load Downloaded Checkpoint** accepts a downloader's filename output and resolves it in ComfyUI's `checkpoints` path. It is intentionally separate from the downloader nodes, so the existing downloader interfaces remain download-only.

## CivitAI version pin

The CivitAI workflow pins model `71`, version `80`, which provides the public SD 1.5-compatible `tinyPlanets_V1.ckpt` checkpoint. The API key field is intentionally blank; enter your own key only if CivitAI requires one for your account or region.
