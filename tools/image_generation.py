# Image generation tool
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mistralai.models import ToolFileChunk

from tools.configs import client


def _save_image_chunk(chunk: ToolFileChunk, timestamp: str, index: int) -> str | None:
    """Save an image chunk to disk and return the path."""
    try:
        file_bytes = client.files.download(file_id=chunk.file_id).read()
        image_path = Path(f"generated_images/meal_{timestamp}_{index}.png")
        image_path.write_bytes(file_bytes)
        print(f"Successfully saved image to: {image_path}")
        return str(image_path)
    except Exception as e:
        print(f"Error processing image chunk: {e!s}")
        return None


def _process_outputs(outputs: list[Any], timestamp: str) -> list[str]:
    """Process response outputs and extract image paths."""
    image_paths: list[str] = []
    print(f"Processing {len(outputs)} outputs")
    for output in outputs:
        if not hasattr(output, "content"):
            continue
        content = output.content
        print(f"Processing content of type: {type(content)}")
        if not isinstance(content, list):
            print(f"Content is not a list: {content}")
            continue
        for i, chunk in enumerate(content):
            print(f"Processing chunk {i} of type: {type(chunk)}")
            if isinstance(chunk, ToolFileChunk):
                print(f"Found ToolFileChunk with file_id: {chunk.file_id}")
                if path := _save_image_chunk(chunk, timestamp, i):
                    image_paths.append(path)
    return image_paths


def generate_food_image(meal_description: str) -> str:
    """Generate a food image based on the meal description."""
    try:
        print(f"Starting image generation for: {meal_description}")
        image_agent = client.beta.agents.create(
            model="mistral-medium-latest",
            name="Food Image Generation Agent",
            description="Agent used to generate food images.",
            instructions=(
                "Use the image generation tool to create appetizing food images. "
                "Generate realistic and appetizing images of meals."
            ),
            tools=[{"type": "image_generation"}],
            completion_args={"temperature": 0.3, "top_p": 0.95},
        )
        print("Created image generation agent")
        response = client.beta.conversations.start(
            agent_id=image_agent.id,
            inputs=f"Generate an appetizing image of: {meal_description}",
            stream=False,
        )
        print("Got response from image generation")
        Path("generated_images").mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")

        if hasattr(response, "outputs"):
            image_paths = _process_outputs(response.outputs, timestamp)
            if image_paths:
                print(f"Successfully generated {len(image_paths)} images")
                return image_paths[0]

        print("No images were generated")
        return "No image was generated"
    except Exception as e:
        print(f"Error during image generation: {e!s}")
        if hasattr(e, "__dict__"):
            print(f"Error details: {e.__dict__}")
        return f"Error generating image: {e!s}"
