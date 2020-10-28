#!/usr/bin/env python

# Script type: Python-fu
# Script Title: Yin-Yang 1.05
# Tested on GIMP version: 2.10.18, Windows 7, 64 bit.
#
# Note:
#   It appears that the latest GIMP version 2.10.18, has a broken PF Pattern-chooser dialog
#   (discovered by clicking on the pattern/browse button in the yin-yang window).
#   This means this option will be unavailable until
#   the GIMP development team fixes the bug in a later release.
#
# Updates:
#   1.01 - Updated documentation.
#   1.02 - Added crop. Renamed 'lightness' to 'color' in mode menu.
#   1.03 - Added 'lightness' to mode menu (a correct one).
#   1.04 - Improved anti-aliasing (April 11, 2020).
#   1.05 - Removes the new gradients from GIMP as a clean-up (October 27, 2020).

# Copyright:
#   Copyright (C) <2019>  <Charles Bartley>
#
#   This script is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   To receive a full copy of the GNU General Public License
#   see <http://www.gnu.org/licenses/>.
#
# What is Does:
#   This script creates a user-defined new image.
#   On this image, the script will draw a user-defined yin-yang symbol.
#
# What do yin-yang symbols represent?
#   A yin-yang symbol represents energy, reflection,
#   the interaction of dual forces, and reproduction.
#
# Where The Script Installs:
#   The script is accessed through
#   the main image window and the Filters / Render menus.
#
#   Place the script in GIMP's Python-Fu folder. You can discover where this
#   folder is by opening the Preference dialog (Edit / Preferences). In
#   this dialog, find Folders / Plug-ins (scroll down). On the right-panel
#   are two paths. The first path listed is the Python-Fu.
#
# Dialog Breakdown:
#   The dialog will ask for the following information:
#   Symbol Diameter:
#       This is the size of the image and symbol.
#
#   Mode:
#       These are different ways that the yin-yang symbol can be generated.
#
#       Flow Color 1 and Flow Color 2 / Solid:
#           Flow Color 1 and Flow Color 2 are used unchanged.
#
#      Flow Color 1 and Flow Color 2 / Gradient:
#           Flow Color 1 and Flow Color 2 are used, but
#           they are applied as a gradient.
#
#       Flow Color 1 and Polar Color:
#           Flow Color 2 becomes Flow Color 1's color inverted.
#
#       Flow Color 1 and Polar Hue:
#           Flow Color 2 becomes Flow Color 1's color
#           with its hue property inverted.
#
#       Flow Color 1 and Polar Lightness:
#           Flow Color 2 becomes Flow Color 1's color
#           with its lightness property inverted.
#
#       Flow Color 1 and Polar Saturation:
#           Flow Color 2 becomes Flow Color 1's color
#           with its saturation property inverted.
#
#   Flow Color 1:
#       This is a fill color for one half of the symbol.
#
#   Flow Color 2:
#       This is a fill color for the other half of the symbol.
#
#   Rim Color:
#       This will be the color of the symbol's rim (outside edge).
#
#   Rim Width:
#       This is the scale of the rim. The rim reduces the flow size.
#       The rim will be skipped when its width is zero.
#
#   Eye Divisor:
#       This value is used to calculate the size of the eye.
#       The formula is: eye radius = flow diameter / eye divisor.
#       It's confusing, but not so much if you remember a
#       larger divisor makes for a smaller eye.
#
#   Direction:
#       This changes the appearance of the rotation.
#
#   Frame Count:
#       Frame count is used to make an animated '.gif' or '.webp'
#       graphic. If more than one frame is specified, multiple
#       layers are created. Each new layer has an incremental
#       rotation applied (360 degrees / frame count) to the symbol.
#
#       If only one layer is indicated, then tge file is not animated
#       and can be saved as a '.png' file to preserve the transparency.
#
#       If more than one layer is created, the resulting file
#       can be exported as a '.gif' or '.webp' (superior) file-type,
#       so that it can used as a web-page animation.
#
#       If you wish to view your animation while in GIMP,
#       Select Filters / Animation / Animation Playback.
#
#   Frame Timer:
#       If your intention is to create an animation, this value will
#       be used by image exporter to set the time delay between frame updates.

# Careful, this imports (reserving) the variable 't':
from gimpfu import *
import colorsys
import math

# constants
# gap around the symbol:
FRAME_WIDTH_INT = 2
FRAME_WIDTH = float(FRAME_WIDTH_INT)

_, YY_GRADIENT, YY_INVERTED_COLOR, YY_POLAR_HUE, YY_POLAR_LIGHTNESS, \
    YY_POLAR_SATURATION, YY_PATTERN = range(7)

# a fix for anti-aliasing, scaling up the image:
SCALE = 4


class yy():
    """ Organizes common variables. """
    image = None

    # floats:
    head_diameter = head_radius = 0
    center = symbol_dimension = .0
    eye_radius = eye_diameter = 0
    flow_offset = 0

    # integers:
    flow_size = symbol_size = image_size = 0

    # the first layer:
    base = None


def draw_flow_selection(operation):
    """ Draw a selection circle at the scale of the flow.
    'operation' is either an replacement, an addition or a subtraction. """
    a = FRAME_WIDTH + yy.rim_width
    pdb.gimp_image_select_ellipse(
        yy.image,
        operation,
        a, a,
        yy.flow_size, yy.flow_size)


def draw_side(flow_color, gradient, pattern, i):
    """ Draws a side of the yin-yang symbol.
    'i' is a side index (0..1). """
    draw_flow_selection(CHANNEL_OP_REPLACE)

    eye_offset = yy.head_diameter / 2

    # Remove half:
    pdb.gimp_image_select_rectangle(
        yy.image,
        CHANNEL_OP_SUBTRACT,
        (.0, yy.center)[i], .0,
        yy.center, yy.image_size)

    # Add first head selection:
    pdb.gimp_image_select_ellipse(
        yy.image,
        CHANNEL_OP_ADD,
        yy.center - yy.head_radius, (yy.center, yy.flow_offset)[i],
        yy.head_diameter, yy.head_diameter)

    # Remove the tail selection:
    pdb.gimp_image_select_ellipse(
        yy.image,
        CHANNEL_OP_SUBTRACT,
        yy.center - yy.head_radius, (yy.flow_offset, yy.center)[i],
        yy.head_diameter, yy.head_diameter)

    eye_x = yy.center - yy.eye_radius
    eye_y = (
        yy.center + eye_offset - yy.eye_radius,
        yy.center - eye_offset - yy.eye_radius)[i]

    # Remove the eye selection:
    pdb.gimp_image_select_ellipse(
        yy.image,
        CHANNEL_OP_SUBTRACT,
        eye_x, eye_y,
        yy.eye_diameter, yy.eye_diameter)

    eye_y = (
        yy.center - eye_offset - yy.eye_radius,
        yy.center + eye_offset - yy.eye_radius)[i]

    # Add the reflection-eye selection:
    pdb.gimp_image_select_ellipse(
        yy.image,
        CHANNEL_OP_ADD,
        eye_x, eye_y,
        yy.eye_diameter, yy.eye_diameter)

    if yy.mode == YY_GRADIENT:
        # gradient:
        pdb.gimp_context_set_gradient(gradient)
        pdb.gimp_drawable_edit_gradient_fill(
            yy.base,
            GRADIENT_RADIAL,
            .0,
            TRUE,
            1,
            0,
            TRUE,
            (yy.center - yy.head_radius, yy.center + yy.head_radius)[i],
            (yy.center + yy.head_radius, yy.center - yy.head_radius)[i],
            (float(yy.image_size) - FRAME_WIDTH, FRAME_WIDTH)[i],
            (FRAME_WIDTH, float(yy.image_size) - FRAME_WIDTH)[i])

    elif yy.mode == YY_PATTERN:
        # Pattern fill.
        # Set the active pattern:
        pdb.gimp_context_set_pattern(pattern)
        fill(flow_color, BUCKET_FILL_PATTERN)

    else:
        # Fill the selection:
        fill(flow_color, BUCKET_FILL_FG)


def fill(color, material):
    """ Fills a selection on 'yy.base' with a 'color'.
    'material' is the source material of the bucket fill. """
    pdb.gimp_context_set_foreground(color)
    pdb.gimp_edit_bucket_fill(
        yy.base,
        material,
        LAYER_MODE_NORMAL,
        100,
        0, FALSE, 0, 0)     # unused parameters


def new_gradient(left_color, right_color, i):
    """ Creates a new linear-type gradient from the colors.
    The gradient is prepped, but not drawn.
    'i' is used to distinguish the two gradients used in the script. """
    gradient = pdb.gimp_gradient_new("yin-yang" + str(i))

    pdb.gimp_gradient_segment_set_right_color(gradient, 0, right_color, 100.)
    pdb.gimp_gradient_segment_set_left_color(gradient, 0, left_color, 100.)
    pdb.gimp_gradient_segment_range_set_blending_function(
        gradient,
        0,
        -1,
        GRADIENT_SEGMENT_LINEAR)

    pdb.gimp_gradient_segment_range_set_coloring_type(
        gradient,
        0,
        -1,
        GRADIENT_SEGMENT_RGB)
    return gradient


def render_yin_yang(
        symbol_diameter,
        mode,
        flow_color_1,
        flow_color_2,
        rim_color,
        flow_pattern_1,
        flow_pattern_2,
        rim_width,
        eye_divisor,
        direction,
        frame_count,
        frame_timer):

    """ Called by GIMP when the user
    selects the OK button in the script's dialog.
    Starts drawing the yin-yang symbol. """
    pdb.gimp_context_push()

    # Initialize yy:
    yy.rim_width = int(rim_width * SCALE)
    yy.symbol_size = int(symbol_diameter * SCALE)
    yy.symbol_dimension = int(symbol_diameter * SCALE)
    yy.mode = mode

    # measurements:
    yy.image_size = yy.symbol_size + 2 * FRAME_WIDTH_INT
    yy.center = yy.image_size / 2
    yy.flow_size = yy.symbol_size - yy.rim_width * 2
    yy.head_diameter = yy.flow_size / 2.
    yy.head_radius = yy.head_diameter / 2
    yy.eye_radius = yy.flow_size / eye_divisor
    yy.eye_diameter = yy.eye_radius * 2
    yy.flow_offset = FRAME_WIDTH + rim_width
    timer = ("", " (" + str(int(frame_timer)) + "ms)")[int(frame_count > 1)]

    # for selections:
    pdb.gimp_context_set_antialias(FALSE)
    pdb.gimp_context_set_feather(FALSE)

    # Set colors:
    if yy.mode == YY_INVERTED_COLOR:
        # Invert the RGB:
        flow_color_2 = (
            255 - flow_color_1[0],
            255 - flow_color_1[1],
            255 - flow_color_1[2])

    elif yy.mode in (YY_POLAR_HUE, YY_POLAR_LIGHTNESS, YY_POLAR_SATURATION):
        # Invert hue or saturation:
        c = [0, 0, 0]

        for i in range(3):
            c[i] = flow_color_1[i] / 255.0

        hls = colorsys.rgb_to_hls(c[0], c[1], c[2])

        if yy.mode == YY_POLAR_HUE:
            # Invert hue:
            h = 1 - hls[0]
            hls = h, hls[1], hls[2]

        elif yy.mode == YY_POLAR_LIGHTNESS:
            # Invert lightness:
            light = 1 - hls[1]
            hls = hls[0], light, hls[2]

        else:
            # Invert saturation:
            s = 1 - hls[2]
            hls = hls[0], hls[1], s

        rgb = colorsys.hls_to_rgb(hls[0], hls[1], hls[2])

        for i in range(3):
            c[i] = int(rgb[i] * 255)
        flow_color_2 = tuple(c)

    # Create a new image:
    yy.image = gimp.Image(yy.image_size, yy.image_size, RGB)
    yy.base = pdb.gimp_layer_new(
        yy.image,
        yy.image_size,
        yy.image_size,
        RGBA_IMAGE,
        "Base" + timer,
        100,
        LAYER_MODE_NORMAL)

    yy.image.add_layer(yy.base, 0)
    pdb.gimp_display_new(yy.image)
    pdb.gimp_image_undo_group_start(yy.image)

    gradient_1 = gradient_2 = None

    if yy.mode == 1:
        # Create two gradients:
        gradient_1 = new_gradient(flow_color_1, flow_color_2, 1)
        gradient_2 = new_gradient(flow_color_2, flow_color_1, 2)

    draw_side(flow_color_1, gradient_1, flow_pattern_1, 0)
    draw_side(flow_color_2, gradient_2, flow_pattern_2, 1)

    if yy.rim_width:
        # Draw rim:
        pdb.gimp_image_select_ellipse(
            yy.image,
            CHANNEL_OP_REPLACE,
            FRAME_WIDTH, FRAME_WIDTH,
            yy.symbol_dimension, yy.symbol_dimension)

        draw_flow_selection(CHANNEL_OP_SUBTRACT)
        fill(rim_color, BUCKET_FILL_FG)

    pdb.gimp_selection_none(yy.image)

    # Counter-clockwise flips the image:
    if direction:
        pdb.gimp_item_transform_flip_simple(
            yy.base,
            ORIENTATION_HORIZONTAL,
            TRUE,
            0)

    yy.image_size = int(yy.image_size / SCALE)

    # Scale the image back to fix anti-aliasing issues:
    pdb.gimp_image_scale_full(yy.image, yy.image_size, yy.image_size, INTERPOLATION_CUBIC)

    # Process frame count:
    if frame_count > 1:
        rotation = angle = 360 / frame_count * (1, -1)[direction]

        f = int(frame_count)
        for frame in range(f - 1):
            layer_copy = pdb.gimp_layer_copy(yy.base, TRUE)
            yy.image.add_layer(layer_copy, 0)

            # Keep angle in GIMP rotation bounds:
            if angle > 180:
                angle = -360 + angle

            elif angle < -180:
                angle = 360 + angle

            layer_copy.name = str(int(angle)) + timer
            pdb.gimp_item_transform_rotate(
                layer_copy,
                math.radians(angle),
                TRUE,
                yy.center, yy.center)

            angle += rotation

            # The flush is critical because
            # the display can get over-extended
            # when a lot layers are created:
            pdb.gimp_displays_flush()

            # Remove the unwanted empty-space created from the rotation:
            pdb.gimp_image_crop(yy.image, yy.image_size, yy.image_size, 0, 0)

    # Clean-up:
    [pdb.gimp_gradient_delete(n) for n in (gradient_1, gradient_2) if n]
    pdb.gimp_image_undo_group_end(yy.image)
    pdb.gimp_context_pop()


register(
    # name
    # becomes dialog title as python-fu + name
    # Space character is not allowed.
    # 'name' is case-sensitive:
    "Render-Yin-Yang-Symbol",

    # tool-tip and window-tip text:
    "Renders a yin-yang symbol or animation.",

    # help (describe how-to, exceptions and dependencies).
    # This info will display in the plug-in browser:
    "Creates a new image and does not require an open image.",

    # The author is displayed in the plug-in browser:
    "Charles Bartley",

    # The copyright is displayed in the plug-in browser:
    "Charles Bartley",

    # The date is displayed in the plug-in browser:
    "2019",

    # menu item descriptor:
    "Yin-Yang...",

    # image types
    # An empty string equates to no image:
    "",

    # dialog parameters:
    [
        (
            PF_SPINNER,
            "symbol_diameter",
            "Symbol Diameter:",
            500,
            (80, 1000, 10)),

        (
            PF_OPTION,
            "mode",
            "Mode:",
            0,
            (
                "Flow Color 1 and Flow Color 2 / Solid",
                "Flow Color 1 and Flow Color 2 / Gradient",
                "Flow Color 1 and Polar Color",
                "Flow Color 1 and Polar Hue",
                "Flow Color 1 and Polar Lightness",
                "Flow Color 1 and Polar Saturation",
                "Flow Pattern 1 and Flow Pattern 2")),

        (
            PF_COLOR,
            "flow_color_1",
            "Flow Color 1:",
            (.0, .0, .0)),

        (
            PF_COLOR,
            "flow_color_2",
            "Flow Color 2:",
            (1.0, 1.0, 1.0)),

        (
            PF_COLOR,
            "rim_color",
            "Rim Color:",
            (.5, .5, .5)),

        (
            PF_PATTERN,
            "flow_pattern_1",
            "Flow Pattern 1:",
            None),

        (
            PF_PATTERN,
            "flow_pattern_2",
            "Flow Pattern 2:",
            None),

        (
            PF_SPINNER,
            "rim_width",
            "Rim Width:",
            0,
            (0, 20, 1)),

        (
            PF_SPINNER,
            "eye_divisor",
            "Eye Divisor:",
            14,
            (6, 25, 1)),

        (
            PF_OPTION,
            "direction",
            "Direction:",
            0,
            (
                "Clockwise",
                "Counter-Clockwise")),

        (
            PF_SPINNER,
            "frame_count",
            "Frame Count:",
            1,
            (1, 60, 1)),

        (
            PF_SPINNER,
            "frame_timer",
            "Frame Timer in Milliseconds:",
            100,
            (10, 1000, 1)),     # arbitrary limitations
    ],

    # results:
    [],

    # dialog function handler
    # The second item is the menu's location:
    render_yin_yang, menu="<Image>/Filters/Render")

main()
