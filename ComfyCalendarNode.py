import calendar
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


class ComfyCalendarNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "month": ("INT", {"default": 1, "min": 1, "max": 12}),
                "year": ("INT", {"default": 2024, "min": 1900, "max": 2100}),
                "width": ("INT", {"default": 800, "min": 400, "max": 4000}),
                "height": ("INT", {"default": 600, "min": 300, "max": 3000}),
                "bg_color": ("STRING", {"default": "white"}),
                "text_color": ("STRING", {"default": "black"}),
                "grid_color": ("STRING", {"default": "gray"}),
                "title_font_size": ("INT", {"default": 24, "min": 12, "max": 48}),
                "day_font_size": ("INT", {"default": 18, "min": 12, "max": 36}),
                "grid_line_style": ("STRING", {"default": "solid", "options": ["solid", "dashed", "dotted"]}),

                # Padding options
                "padding_top": ("INT", {"default": 20, "min": 0, "max": 200}),
                "padding_left": ("INT", {"default": 20, "min": 0, "max": 200}),
                "padding_right": ("INT", {"default": 20, "min": 0, "max": 200}),
                "padding_bottom": ("INT", {"default": 20, "min": 0, "max": 200}),

                # More specific padding options for fine-tuned control
                "title_padding": ("INT", {"default": 20, "min": 0, "max": 200}),
                "week_header_padding": ("INT", {"default": 10, "min": 0, "max": 100}),
                "day_cell_padding": ("INT", {"default": 5, "min": 0, "max": 50}),
                "grid_padding": ("INT", {"default": 20, "min": 0, "max": 100}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "create_calendar"
    CATEGORY = "CALENDAR NODES"

    def create_calendar(self, month, year, width, height, bg_color, text_color, grid_color, title_font_size, day_font_size, grid_line_style, padding_top, padding_left, padding_right, padding_bottom, title_padding, week_header_padding, day_cell_padding, grid_padding):
        try:
            # Step 1: Create a blank image with the specified background color
            image = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(image)

            # Step 2: Load fonts or use default fonts if unavailable
            try:
                title_font = ImageFont.truetype("arial.ttf", title_font_size)
                day_font = ImageFont.truetype("arial.ttf", day_font_size)
            except IOError:
                title_font = ImageFont.load_default()
                day_font = ImageFont.load_default()

            # Step 3: Draw the title (e.g., "January 2024") at the top center
            month_name = calendar.month_name[month]
            title = f"{month_name} {year}"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_x = (width - title_bbox[2]) // 2
            title_y = padding_top + title_padding  # Adjusted title padding
            draw.text((title_x, title_y), title,
                      fill=text_color, font=title_font)

            # Step 4: Define the starting point and spacing for the weekday headers
            # Adjusted for more space control
            days_header_top = title_y + title_bbox[3] + week_header_padding
            days_header_height = height // 10  # Allocate space for the weekday headers
            # 7 columns for each day of the week
            cell_width = (width - padding_left - padding_right) // 7

            # Step 5: Draw weekday headers at the top of the grid
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for i, day in enumerate(days):
                day_x = padding_left + i * cell_width + \
                    (cell_width - draw.textbbox((0, 0),
                     day, font=day_font)[2]) // 2
                draw.text((day_x, days_header_top), day,
                          fill=text_color, font=day_font)

            # Step 6: Define grid layout area below the headers for dates
            grid_top = days_header_top + days_header_height + \
                grid_padding  # Add margin between headers and date grid
            grid_height = height - grid_top - padding_bottom  # Leave padding at the bottom
            # 6 rows for dates (max number of weeks)
            cell_height = grid_height // 6

            # Step 7: Get the calendar for the month and plot dates
            cal = calendar.monthcalendar(year, month)
            for row, week in enumerate(cal):  # Up to 6 weeks (rows)
                for col, day in enumerate(week):  # 7 days (columns)
                    x1 = padding_left + col * cell_width
                    y1 = grid_top + row * cell_height
                    x2, y2 = x1 + cell_width, y1 + cell_height

                    # Draw grid lines
                    if grid_line_style == "solid":
                        draw.rectangle([x1, y1, x2, y2], outline=grid_color)
                    elif grid_line_style == "dashed":
                        for i in range(x1, x2, 5):
                            draw.line([(i, y1), (i, y2)], fill=grid_color)
                        for j in range(y1, y2, 5):
                            draw.line([(x1, j), (x2, j)], fill=grid_color)
                    elif grid_line_style == "dotted":
                        for i in range(x1, x2, 4):
                            draw.point((i, y1), fill=grid_color)
                            draw.point((i, y2), fill=grid_color)
                        for j in range(y1, y2, 4):
                            draw.point((x1, j), fill=grid_color)
                            draw.point((x2, j), fill=grid_color)

                    # Place date text in each cell if there is a date for that cell
                    if day != 0:
                        date_text = str(day)
                        date_bbox = draw.textbbox(
                            (0, 0), date_text, font=day_font)
                        date_x = x1 + (cell_width - date_bbox[2]) // 2
                        date_y = y1 + (cell_height - date_bbox[3]) // 2
                        draw.text((date_x, date_y), date_text,
                                  fill=text_color, font=day_font)

            # Step 8: Convert PIL image to a PyTorch tensor in CxHxW format
            result_image = np.array(image)
            tensor_image = torch.tensor(result_image).permute(
                2, 0, 1).float() / 255  # Normalize to [0,1] range

            # Step 9: Set the image preview
            self.image_preview = tensor_image  # Store it for later previewing in the node

            return (tensor_image.cpu(),)  # Return the single image as a tensor

        except Exception as e:
            print(f"Error creating calendar: {e}")
            # Return a default empty image if there's an error
            return (torch.zeros((3, 1, 1)),)

    # Optional: Method for rendering the preview of the image inside the node
    def draw_node_gui(self, gui_context):
        if hasattr(self, 'image_preview') and self.image_preview is not None:
            # Add a preview image to the node GUI (you may need to adapt this depending on the system you're using)
            # This is a placeholder function for rendering
            gui_context.draw_image(self.image_preview)
