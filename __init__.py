import os

import numpy as np
import requests
from PIL import Image

import folder_paths
from moviepy.editor import ImageSequenceClip

class SendToDiscordWebhook:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "webhook_url": ("STRING", {"default": "https://discord.com/api/webhooks/YOUR_WEBHOOK_HASH"}),
                "frame_rate": (
                    "INT",
                    {"default": 12, "min": 1, "max": 60, "step": 1},
                ),
                "save_image": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    OUTPUT_NODE = True
    CATEGORY = "KytraWebhookHTTP"
    FUNCTION = "generate_and_upload_video"

    def generate_and_upload_video(
            self,
            images,
            webhook_url: str,
            frame_rate: int,
            save_image=True,
    ):

        output_dir = (
            folder_paths.get_output_directory()
            if save_image
            else folder_paths.get_temp_directory()
        )
        (
            full_output_folder,
            filename,
            counter,
            subfolder,
            _,
        ) = folder_paths.get_save_image_path("final", output_dir)

        if len(images) == 1:
            single_file_path = os.path.join(full_output_folder, f"{filename}_.png")
            single_image = 255.0 * images[0].cpu().numpy()
            single_image_pil = Image.fromarray(single_image.astype(np.uint8))
            single_image_pil.save(single_file_path)
            response = requests.post(
                webhook_url,
                files={"file": open(single_file_path, "rb")}
            )

            if response.status_code == 204:
                print("Successfully uploaded video to Discord.")
            else:
                print(f"Failed to upload video. Status code: {response.status_code} - {response.text}")
        else:
            frames = [255.0 * image.cpu().numpy() for image in images]

            print(f"Output directory: {output_dir}")
            clip = ImageSequenceClip(frames, fps=frame_rate)

            # Save video to file
            file_path = os.path.join(full_output_folder, f"{filename}_{counter:05}_.mp4")
            clip.write_videofile(file_path, codec="libx264", fps=frame_rate)

            # Uploading to Discord
            print("Uploading video to Discord")
            with open(file_path, 'rb') as file_data:
                response = requests.post(
                    webhook_url,
                    files={"file": file_data}
                )

            if response.status_code == 204:
                print("Successfully uploaded video to Discord.")
            else:
                print(f"Failed to upload video. Status code: {response.status_code} - {response.text}")

        return ("Yay! You did it!", )


# Add this new node to the dictionary of all nodes
NODE_CLASS_MAPPINGS = {
    "SendToDiscordWebhook": SendToDiscordWebhook,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SendToDiscordWebhook": "Send To Discord Webhook",
}
