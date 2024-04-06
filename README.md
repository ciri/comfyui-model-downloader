# Model Downloader for ComfyUI

## Introduction
This project provides an experimental model downloader node for ComfyUI, designed to simplify the process of downloading and managing models in environments with restricted access or complex setup requirements. It aims to enhance the flexibility and usability of ComfyUI by enabling seamless integration and management of machine learning models.

## Screenshot

![Alt text](doc/hf-downloader.png?raw=true "HF")
![Alt text](doc/civitai-downloader.png?raw=true "CivitAI")

## Features
- **Easy Model Downloading**: Simplify the process of downloading models directly within the ComfyUI environment.
- **Repositories**: Currently only supports hugging face and CivitAI.
- **User-friendly**: Designed with a focus on ease of use, making model management accessible to users of all skill levels.

## Installation

Clone the repository or download the extension directly into your ComfyUI project's `custom_nodes` folder:

```
git clone https://github.com/ciri/model-downloader-comfyui.git
```

Alternatively use ComfyUI Manager and install via "Install via Git URL". 

## Usage
To use the model downloader within your ComfyUI environment:
1. Open your ComfyUI project.
2. Find the `HF Downloader` or `CivitAI Downloader` node.
3. Configure the node properties with the URL or identifier of the model you wish to download and specify the destination path.
4. Execute the node to start the download process.
5. To avoid repeated downloading, make sure to bypass the node after you've downloaded a model.



## Support
For support, questions, or contributions, please open an issue on the GitHub repository page. Contributions are welcome!