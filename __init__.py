# Import your node classes from the respective module
# from .FashionX.fashion_nodes import Fashion
from . import (
    ComfyCalendarNode
)


# Create a dictionary mapping node categories to their respective classes
NODE_CLASS_MAPPINGS = {
    "Comfy Calendar Node": ComfyCalendarNode
}

# Create a dictionary mapping display names to their readable names
NODE_DISPLAY_NAME_MAPPINGS = {
    "SportyStyleNode": "Sporty Style Node"
}

# Function to load nodes and print their status


def load_calendar_nodes():
    print("Calendar Nodes Loading...")
    for display_name, readable_name in NODE_DISPLAY_NAME_MAPPINGS.items():
        print(f"Loading: {readable_name} as {display_name}")


# Execute the function to load nodes and confirm their status
load_calendar_nodes()
