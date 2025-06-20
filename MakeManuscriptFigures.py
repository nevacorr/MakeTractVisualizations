from PIL import Image
from PIL import ImageDraw
import os.path as pt

source_fig_dir = '/Users/nevao/PycharmProjects/MakeTractVisualizations/panel_figures'

################################# MD FIGURE ##########################
metric = 'md'

# Define the regions and order of images per row for md
tract_names = [
    ["Thalamic_Radiation", "IFOF", "Callosum_Forceps_Major"],
    ["ILF", "Arcuate", "Callosum_Forceps_Minor"]
]

# Load images by row
rows_images = []
for row in tract_names:
    images = [Image.open(pt.join(source_fig_dir, f"combined_panel_figure_{metric}_{tract}.png")) for tract in row]
    rows_images.append(images)

# Concatenate images horizontally per row
row_concat_images = []
for images in rows_images:
    spacing = 40         # spacing between 2nd and 3rd image
    small_spacing = 1     # small spacing between 1st and 2nd image for vertical line

    total_width = sum(img.width for img in images) + spacing + small_spacing
    max_height = max(img.height for img in images)

    new_row_img = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 255))  # white background

    draw = ImageDraw.Draw(new_row_img)

    x_offset = 0
    for i, img in enumerate(images):

        # Add small spacing (1px) before second image (i==1)
        if i == 1:
            # Fill padding area with white
            draw.rectangle([x_offset, 0, x_offset + small_spacing - 1, max_height], fill='white')
            # Draw vertical black line centered in this padding
            draw.line([(x_offset + small_spacing // 2, 0), (x_offset + small_spacing // 2, max_height)], fill='black', width=3)
            x_offset += small_spacing

        # Add large spacing (10px) before third image (i==2)
        if i == 2:
            draw.rectangle([x_offset, 0, x_offset + spacing - 1, max_height], fill='white')
            draw.line([(x_offset + spacing // 2, 0), (x_offset + spacing // 2, max_height)], fill='black', width=3)
            x_offset += spacing

        new_row_img.paste(img, (x_offset, 0))
        x_offset += img.width

    # Draw horizontal top and bottom border lines for the entire row
    draw.line([(0, 0), (total_width - 1, 0)], fill='black', width=2)
    draw.line([(0, max_height - 1), (total_width - 1, max_height - 1)], fill='black', width=2)

    row_concat_images.append(new_row_img)

# Now concatenate the two rows vertically
total_width = max(row_img.width for row_img in row_concat_images)
total_height = sum(row_img.height for row_img in row_concat_images)

final_img = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 255))  # white background

y_offset = 0
for row_img in row_concat_images:
    final_img.paste(row_img, (0, y_offset))
    y_offset += row_img.height

# Draw a border around the full image
draw_final = ImageDraw.Draw(final_img)
draw_final.rectangle(
    [0, 0, final_img.width - 1, final_img.height - 1],
    outline='black',
    width=2
)
# Save or show
save_path = pt.join(source_fig_dir, f"{metric} combined figure with lines.png")
final_img.save(save_path, dpi=(300,300))
final_img.show()

################################# FA FIGURE #################################
metric = 'fa'

# Define the regions and order of images per row for md
tract_names = ["Arcuate", "ILF", "IFOF"]

# Load images

images = [Image.open(pt.join(source_fig_dir, f"combined_panel_figure_{metric}_{tract}.png")) for tract in tract_names]

# Concatenate images horizontally

small_spacing = 1     # small spacing between images for vertical line

# Compute total dimensions
total_width = sum(img.width for img in images) + small_spacing * (len(images) - 1)
max_height = max(img.height for img in images)

new_row_img = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 255))  # white background

draw = ImageDraw.Draw(new_row_img)

x_offset = 0
for i, img in enumerate(images):
    # Add spacing *before* pasting the 2nd and 3rd image
    if i > 0:
        x_offset += small_spacing
        draw.line([(x_offset - small_spacing // 2, 0), (x_offset - small_spacing // 2, max_height)], fill='black', width=3)

    new_row_img.paste(img, (x_offset, 0))
    x_offset += img.width

# Add a box around the full image
draw.rectangle(
    [0, 0, total_width - 1, max_height - 1],
    outline='black',
    width=2
)
# Save or show
save_path = pt.join(source_fig_dir, f"{metric} combined figure with lines.png")
new_row_img.save(save_path, dpi=(300,300))
new_row_img.show()

