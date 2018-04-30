# -*- coding: utf-8 -*-

"""Provide image manipulation functions for player category detection."""

import os

from PIL import Image


def get_category_palette(folder, main_categories):
    """Map colors to main categories."""
    print("Mapping colors to main categories... ", end='', flush=True)
    category_palette = {}
    for category in main_categories:
        file_path = os.path.join(folder, '.{category}.png'.format(category=category))
        if os.path.isfile(file_path):
            image = Image.open(file_path)
            image, _ = get_repaired_image(image)
            category_palette[category] = sorted(image.getcolors(), reverse=True)[0][1]
    print("Done.")
    return category_palette


def get_player_image(folder, file_name):
    """Load the PNG file assigned to a player."""
    image = Image.open(os.path.join(folder, file_name))
    image, repaired = get_repaired_image(image)
    return image, repaired


def get_repaired_image(image):
    """Replace minor colors of an image by its major colors."""
    image = image.convert('RGBA')
    allowed_conversion_count, repaired = len(image.getcolors()) - 1, False
    while len(get_major_minor_colors(image)[1]) > 0 and allowed_conversion_count > 0:
        image = image.convert('P', palette=Image.ADAPTIVE, colors=(len(image.getcolors()) - 1))
        image = image.convert('RGBA')  # For convert to palette fix and final output
        allowed_conversion_count -= 1
        repaired = True
    return image, repaired


def get_major_minor_colors(image):
    """Assign colors to major or minor color category."""
    major_colors, minor_colors = [], []
    image_size = image.size[0] * image.size[1]
    colors_data = image.getcolors()
    exp_color_ratio = 1 / len(colors_data)  # 1/n for n-colors image
    for color_data in colors_data:
        pixel_count, color = color_data
        color_ratio = pixel_count / image_size
        if color_ratio > 0.5 * exp_color_ratio:  # Major if more than half of exp ratio
            major_colors.append(color)
        else:
            minor_colors.append(color)
    return major_colors, minor_colors


def get_player_categories(player_image, category_palette):
    """Identify the category of a player."""
    player_categories = []
    for _, player_color in player_image.getcolors():
        closest_category, min_diff = None, float('inf')
        for category, category_color in category_palette.items():
            r_diff = abs(player_color[0] - category_color[0])
            g_diff = abs(player_color[1] - category_color[1])
            b_diff = abs(player_color[2] - category_color[2])
            color_diff = r_diff + g_diff + b_diff
            if color_diff < min_diff:
                closest_category, min_diff = category, color_diff
        player_categories.append(closest_category)
    return player_categories
