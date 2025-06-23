from PIL import Image, ImageDraw
import os.path as pt

source_fig_dir = '/Users/nevao/PycharmProjects/MakeTractVisualizations/panel_figures'

metric = 'md'

tract_names = [
    ["Thalamic_Radiation", "IFOF", "ILF"],
    ["Arcuate", "SLF", "Callosum_Forceps_Major", "Callosum_Forceps_Minor"]
]

# Load images by row
rows_images = []
for row in tract_names:
    images = [Image.open(pt.join(source_fig_dir, f"combined_panel_figure_{metric}_{tract}.png")) for tract in row]
    rows_images.append(images)

# Calculate widths of each row including spacings
small_spacing = 1
large_spacing = 40

row_widths = []
for row_index, images in enumerate(rows_images):
    # Sum widths of images
    row_width = sum(img.width for img in images)
    # Add small spacing between 1st and 2nd images
    if len(images) > 1:
        row_width += small_spacing
    # Add large spacing before 3rd and 4th images ONLY in bottom row
    if row_index == 1:
        # Add before 3rd and 4th images (2 spacings)
        row_width += large_spacing * 2
    row_widths.append(row_width)

# Calculate the max width for final image (equalize both rows)
final_width = max(row_widths)

row_concat_images = []

for row_index, images in enumerate(rows_images):

    max_height = max(img.height for img in images)
    row_width = row_widths[row_index]

    # Calculate horizontal shift to center narrower top row
    shift = (final_width - row_width) // 2 if row_index == 0 else 0

    # Create blank canvas for this row
    new_row_img = Image.new("RGBA", (final_width, max_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(new_row_img)

    x_offset = shift
    for i, img in enumerate(images):

        # Add small spacing before 2nd image
        if i == 1:
            draw.rectangle([x_offset, 0, x_offset + small_spacing - 1, max_height], fill='white')
            draw.line([(x_offset + small_spacing // 2, 0), (x_offset + small_spacing // 2, max_height)], fill='black', width=3)
            x_offset += small_spacing

        # add spacing before third image (top row only)
        if row_index == 0 and i == 2:
            draw.rectangle([x_offset, 0, x_offset + small_spacing - 1, max_height], fill='white')
            draw.line([(x_offset + small_spacing // 2, 0), (x_offset + small_spacing // 2, max_height)], fill='black',
                      width=3)
            x_offset += small_spacing

        # Add large spacing before 3rd and 4th images in bottom row only
        if row_index == 1 and (i == 2 or i == 3):
            draw.rectangle([x_offset, 0, x_offset + large_spacing - 1, max_height], fill='white')
            draw.line([(x_offset + large_spacing // 2, 0), (x_offset + large_spacing // 2, max_height)], fill='black', width=3)
            x_offset += large_spacing

        new_row_img.paste(img, (x_offset, 0))
        x_offset += img.width

    # Draw horizontal top and bottom border lines for the entire row
    draw.line([(0, 0), (final_width - 1, 0)], fill='black', width=2)
    draw.line([(0, max_height - 1), (final_width - 1, max_height - 1)], fill='black', width=2)

    # Add vertical lines at left and right edges of top row images only
    if row_index == 0:
        # Left vertical line at left edge of first image (shift)
        draw.line([(shift, 0), (shift, max_height)], fill='black', width=3)
        # Right vertical line at right edge of last image
        right_edge = shift + row_width
        draw.line([(right_edge - 1, 0), (right_edge - 1, max_height)], fill='black', width=3)

    row_concat_images.append(new_row_img)

# Now concatenate the two rows vertically
total_height = sum(img.height for img in row_concat_images)

final_img = Image.new("RGBA", (final_width, total_height), (255, 255, 255, 255))
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

# Save and show
save_path = pt.join(source_fig_dir, f"{metric}_combined_figure_with_lines.png")
final_img.save(save_path, dpi=(300, 300))
final_img.show()
