# Model Downloader for ComfyUI

<div align="center">
    <picture>
        <source media="(prefers-color-scheme: light)" srcset="https://github.com/ciri/comfyui-model-downloader/blob/main/assets/logo.svg?raw=true">
    </picture>
</div>


## Introduction
This project provides an experimental model downloader node for ComfyUI, designed to simplify the process of downloading and managing models in environments with restricted access or complex setup requirements. It aims to enhance the flexibility and usability of ComfyUI by enabling seamless integration and management of machine learning models.

## Features
- **Easy Model Downloading**: Simplify the process of downloading models directly within the ComfyUI environment.
- **Repositories**: Currently supports hugging face and CivitAI.
- **User-friendly**: Designed with a focus on ease of use, making model management accessible to users of all skill levels.

## Available Nodes

### HF Downloader
![HF|250](assets/hf-downloader.png?raw=true)

Parameters:

* repo_id: Hugging Face repo ID
* filename: filename to download from the repository
* save_dir: destination directory
* overwrite: overwrite existing file if it exists

### CivitAI Downloader
![CivitAI|250](assets/civitai-downloader.png?raw=true)

Parameters:
* model_id: CivitAI model ID
* version_id: CivitAI model version ID
* token_id: CivitAI token ID
* save_dir: destination directory

## Auto Model Finder (Experimental)

![Auto](assets/auto-downloader.png?raw=true)

Automatically searches for known files (e.g., .safetensors, .ckpt, etc) files in your canvas and looks for repositories containing them on Hugging Face. Ideally, you should use this together with the HF Downloader node to automatically download any missing models.

Troubleshooting: this node is experimental and may not work as expected. If it doesn't work, try removing the node and adding it again.

## Installation

### Via ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Select Custom Nodes Manager
3. Search for "ComfyUI Model Downloader"
4. Install

### Via Git Clone

Clone the repository or download the extension directly into your ComfyUI project's `custom_nodes` folder:

```
git clone https://github.com/ciri/comfyui-model-downloader.git
```

## Usage
To use the model downloader within your ComfyUI environment:
1. Open your ComfyUI project.
2. Find the `HF Downloader` or `CivitAI Downloader` node.
3. Configure the node properties with the URL or identifier of the model you wish to download and specify the destination path.
4. Execute the node to start the download process.
5. To avoid repeated downloading, make sure to bypass the node after you've downloaded a model.

## Roadmap (tentative)
- [x] Add persistance for auto model finder between runs
- [ ] Add more model finders (including CivitAI)
- [ ] Add more downloaders
- [ ] Add authentication for HF Downloader



## Contributing
Contributions are welcome! Please:

* Fork the repository
* Create a feature branch
* Submit a pull request

## Support
For support, questions, or contributions, please open an issue on the GitHub repository page. Contributions are welcome!

## License


GNU Affero General Public License v3.0
