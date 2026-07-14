# Tiny ComfyUI test workflows

These workflows are intentionally small, public, and credential-free. Load one by dragging its `.json` file into ComfyUI, then queue it. Each workflow is wired to ComfyUI's core **Preview Any** node so the downstream value is visible after execution.

| Workflow | What it verifies | Download size |
| --- | --- | --- |
| `huggingface-tiny-download.json` | Hugging Face download, in-node progress, and returned filename | about 520 KB |
| `civitai-tiny-download.json` | CivitAI metadata lookup, download, public access, and returned filename | about 250 bytes |
| `auto-model-finder-scan.json` | Workflow scan, Hugging Face lookup, and discovered repository | no download |

## Run the auto-model-finder flow from scratch

Before loading `auto-model-finder-scan.json`, delete `model.safetensors` from the selected `checkpoints` directory. The unconnected **Load Checkpoint** node is deliberate: it gives the model finder a missing filename to scan without attempting to load it. Queue the workflow, then confirm that the **Auto Model Finder** widget changes from `Scan First` to a discovered filename.

The finder uses a filename search, so the discovered repository may vary over time. The fixture deliberately does not connect its result to a downloader; inspect the selected repository before deciding whether to download it. The download workflows above remain the deterministic, small end-to-end tests.

## Why the examples preview a filename

ComfyUI's built-in model loaders use typed dropdown inputs and do not accept a generic filename link. The downloader output is therefore connected to **Preview Any**, which proves that a completed download is available to downstream nodes. Use the returned filename to select the model in the appropriate ComfyUI loader after the download completes.

## CivitAI version pin

The CivitAI workflow pins model `723360`, version `1047814`, whose first public file is `styles.zip`. Pinning avoids selecting a newer, potentially large version. The API key field is intentionally blank; enter your own key only if CivitAI requires one for your account or region.
