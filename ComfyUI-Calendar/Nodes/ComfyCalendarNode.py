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
                "grid_line_style": ("STRING", {"default": "solid", "options": ["solid", "dashed", "dotted"]})
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "create_calendar"
    CATEGORY = "CALENDAR NODES"

    def create_calendar(self, month, year, width, height, bg_color, text_color, grid_color, title_font_size, day_font_size, grid_line_style):
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
            title_y = height // 20  # Add some margin from the top
            draw.text((title_x, title_y), title,
                      fill=text_color, font=title_font)

            # Step 4: Define the starting point and spacing for the weekday headers
            # Adjust vertical spacing between title and weekday headers
            days_header_top = title_y + title_bbox[3] + 30
            days_header_height = height // 10  # Allocate space for the weekday headers
            cell_width = width // 7  # 7 columns for each day of the week

            # Step 5: Draw weekday headers at the top of the grid
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for i, day in enumerate(days):
                day_x = i * cell_width + \
                    (cell_width - draw.textbbox((0, 0),
                     day, font=day_font)[2]) // 2
                draw.text((day_x, days_header_top), day,
                          fill=text_color, font=day_font)

            # Step 6: Define grid layout area below the headers for dates
            grid_top = days_header_top + days_header_height + \
                20  # Add margin between headers and date grid
            grid_height = height - grid_top - 20  # Leave padding at the bottom
            # 6 rows for dates (max number of weeks)
            cell_height = grid_height // 6

            # Step 7: Get the calendar for the month and plot dates
            cal = calendar.monthcalendar(year, month)
            for row, week in enumerate(cal):  # Up to 6 weeks (rows)
                for col, day in enumerate(week):  # 7 days (columns)
                    x1 = col * cell_width
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
            return (tensor_image.cpu(),)  # Return as CPU tensor

        except Exception as e:
            print(f"Error creating calendar: {e}")
            return (torch.zeros((3, 1, 1)),)  # Return as 1x1 pixel RGB tensor


NODE_CLASS_MAPPINGS = {
    "CALENDAR NODES": ComfyCalendarNode
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyCalendarNode": "CALENDAR NODE"
}
