import folder_paths


class DownloadedCheckpointLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "filename": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    RETURN_NAMES = ("model", "clip", "vae")
    FUNCTION = "load_checkpoint"
    CATEGORY = "loaders"

    def load_checkpoint(self, filename):
        checkpoint_path = folder_paths.get_full_path_or_raise("checkpoints", filename)

        from comfy import sd

        model, clip, vae, *_ = sd.load_checkpoint_guess_config(
            checkpoint_path,
            output_vae=True,
            output_clip=True,
            embedding_directory=folder_paths.get_folder_paths("embeddings"),
        )
        return model, clip, vae
