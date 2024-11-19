#!/usr/bin/env python

# Script type: Python-fu
# Script Title: Draw Flower Of Life v1
# Tested on GIMP version: 2.10.18, Windows 10, 64 bit.
#
# Updates:
#       1.01 - Removes the gradients from GIMP after creating them (October 27, 2020).
#
# Copyright:
#   Copyright (C) <2020>  <Charles Bartley>
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
#   On this image, the script will draw a user-defined Flower of Life symbol.
#
#   If colors are used in the flower, the script will output the colors
#   in GIMP's error console. This is useful to make a random color
#   symbol reproducible.
#
# What do Flower Of Life symbols represent?
#   A Flower of Life symbol is a symbol in sacred geometry. It is a Metatron's cube,
#   the Seed of Life, and the Tree of Life. It represents the connection
#   we feel to all living things.
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
#       This is the size of the flower. Pick a number that is divisible
#       by 2 and 3 for the best results.
#
#   Type:
#       Lines: The image will only have lines.
#       Petals: The image will be made from solid petals.
#       Circles: The image will be show the content of the circles.
#
#   Mode:
#       Black And White: The image is a black and white image.
#       Preset Color: The image is a colored image made with user-defined colors.
#       Random Color: The image is made from random colors.
#
#   Colors:
#       Set these colors if you want to use the Mode : Preset Color.
#       Otherwise, these are ignored by the script.
#       The colors are added to the image from the center of the image outwards in rings.
#       The seven colors are ordered by their sequence of use.
#
#   Line Width:
#       If you create a symbol of Type: Lines, then this value defines
#       the width of the lines.
#
#   Frame Width:
#       If you wish to add a frame to the image, then set this value to
#       be the frame's width. A frame with a width of zero is not shown.
#
#   Frame Color:
#       If there is a frame and the Mode: Preset Color is selected,
#       then this will be the frame's color. In Mode: Random Color,
#       the frame color is the average color from the random colors.
#
# Careful, this imports (reserving) the variable 't':
from gimpfu import *
import math
import random

# constants:
#-----------
# colors:
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# layer names:
BASE = "Base"
MASK = "Mask"
COLOR_LAYER = "Color-Layer"
GRADIENT = "Gradient"

# degrees:
DEGREE_30 = .523599
DEGREE_45 = .785398
DEGREE_60 = 1.0472
DEGREE_90 = 1.5708
DEGREE_120 = 2.0944
DEGREE_180 = 3.14159
DEGREE_240 = 4.18879
DEGREE_300 = 5.23599

# recycled focus points:
ring_center = [0] * 6
extra_ring = [0] * 12

# flower type:
LINES, PETALS, CIRCLES = 0, 1, 2

RING_COLORS_COUNT = 7

# mode:
RANDOM_COLORS = 2

# image up-scale multiplier:
SCALE = 2


def create_bw_alpha():
    """
    Masks out the extraneous flower imagery.
    """
    if flower_type == PETALS:
        bottom_layer = pdb.gimp_image_get_layer_by_name(image, BASE)
        pdb.plug_in_colortoalpha(image, bottom_layer, BLACK)

    dim1 = circle_diameter
    layer = make_new_layer(MASK, normal=True)

    fill_layer(layer, BLACK)

    if flower_type == LINES:
        dim1 += line_width
        line_w = int(line_width / 2)

    # Covers the perimeter:
    for i in range(12):
        x, y = extra_ring[i]
        x -= circle_radius
        y -= circle_radius

        if flower_type == LINES:
            x -= line_w
            y -= line_w

        pdb.gimp_image_select_ellipse(
            image,
            CHANNEL_OP_ADD,
            x, y,
            dim1, dim1)

    # Fill the center:
    x = y = image_center - circle_diameter
    dim = circle_diameter * 2

    pdb.gimp_image_select_ellipse(
        image,
        CHANNEL_OP_ADD,
        x, y,
        dim, dim)

    draw_circle_selection(x, y)
    fill_circle(layer, WHITE)
    pdb.gimp_selection_none(image)

    # Add the frame:
    draw_frame(WHITE)

    # Create mask and add it to bottom layer:
    layer = pdb.gimp_image_get_layer_by_name(image, MASK)

    base_layer = pdb.gimp_image_get_layer_by_name(image, BASE)

    pdb.gimp_image_select_color(image, CHANNEL_OP_ADD, layer, WHITE)

    mask = pdb.gimp_layer_create_mask(layer, ADD_MASK_SELECTION)

    pdb.gimp_layer_add_mask(base_layer, mask)
    pdb.gimp_selection_none(image)

    # Delete mask layer:
    pdb.gimp_image_remove_layer(image, layer)


def draw_1st_ring(color):
    """
    Draws the first ring around the image center.

    color : (r, g, b)
        the color of the circles
    """
    x = image_center
    y = image_center - circle_radius
    angle = 0

    for i in range(6):
        draw_flower_circle(x, y, color)
        angle += DEGREE_60
        x, y = get_point_on_circle(image_focus, angle, circle_radius)


def draw_2nd_ring(color):
    """
    Draw a ring of circles.

    color : (r, g, b)
        the color of the circle
    """
    ring_radius = circle_radius * 2
    x = image_center
    y = image_center - ring_radius
    angle = 0

    for _ in range(6):
        draw_flower_circle(x, y, color)

        angle += DEGREE_60
        x, y = get_point_on_circle(image_focus, angle, ring_radius)


def draw_3rd_ring(color):
    """
    Draw a ring of circles.

    color : (r, g, b)
        the color of the circle
    """
    angle1 = 0
    angle2 = DEGREE_60

    for i in range(6):
        x, y = get_point_on_circle(image_focus, angle1, circle_radius)
        x, y = get_point_on_circle((x, y), angle2, circle_radius)
        ring_center[i] = x, y

        draw_flower_circle(x, y, color)

        angle1 += DEGREE_60
        angle2 += DEGREE_60


def draw_4th_ring(color):
    """
    Draw a ring of circles.

    color : (r, g, b)
        the color of the circle
    """
    angle1 = 0
    angle2 = DEGREE_60

    for i in range(6):
        a, b = ring_center[i]
        x, y = get_point_on_circle((a, b), angle1, circle_radius)

        draw_flower_circle(x, y, color)

        x, y = get_point_on_circle((a, b), angle2, circle_radius)

        draw_flower_circle(x, y, color)

        angle1 += DEGREE_60
        angle2 += DEGREE_60


def draw_5th_ring(color):
    """
    Draw a ring of circles.

    color : (r, g, b)
        the color of the circle
    """
    radius = circle_radius * 3
    angle = 0

    for _ in range(6):
        x, y = get_point_on_circle(image_focus, angle, radius)
        angle += DEGREE_60
        draw_flower_circle(x, y, color)


def draw_6th_ring(color):
    """
    Draw a ring of circles.

    color : (r, g, b)
        the color of the circle
    """
    angle = -DEGREE_60

    for i in range(6):
        a, b = ring_center[i]
        extra_ring[i * 2 + 1] = a, b
        extra_ring[i * 2] = get_point_on_circle((a, b), angle, circle_radius)
        angle += DEGREE_60

    angle1 = 0
    angle2 = DEGREE_60

    # the last of the cube, the last edge:
    for j in range(2):
        k = (0, 2)[j]
        for i in range(3):
            a, b = extra_ring[i + k]
            c, d = get_point_on_circle((a, b), angle1, circle_radius)
            x, y = get_point_on_circle((c, d), angle2, circle_radius)
            draw_flower_circle(x, y, color)

        angle1 += DEGREE_60
        angle2 += DEGREE_60

    angle1 = DEGREE_120
    angle2 = DEGREE_180

    for j in range(2):
        k = (4, 6)[j]
        for i in range(3):
            a, b = extra_ring[i + k]
            c, d = get_point_on_circle((a, b), angle1, circle_radius)
            x, y = get_point_on_circle((c, d), angle2, circle_radius)
            draw_flower_circle(x, y, color)

        angle1 += DEGREE_60
        angle2 += DEGREE_60

    angle1 = DEGREE_240
    angle2 = DEGREE_300

    for j in range(2):
        k = (8, 10)[j]
        for i in range(3):
            if i + k > 11:
                i = k = 0

            a, b = extra_ring[i + k]
            c, d = get_point_on_circle((a, b), angle1, circle_radius)
            x, y = get_point_on_circle((c, d), angle2, circle_radius)
            draw_flower_circle(x, y, color)

        angle1 += DEGREE_60
        angle2 += DEGREE_60


def draw_black_and_white():
    """ Draws the flower in black and white. """
    draw_center_circle(WHITE)

    for f in (
                draw_1st_ring,
                draw_2nd_ring,
                draw_3rd_ring,
                draw_4th_ring,
                draw_5th_ring,
                draw_6th_ring
            ):
        f(WHITE)
        pdb.gimp_image_merge_visible_layers(
            image, CLIP_TO_BOTTOM_LAYER)
    draw_frame(WHITE)


def draw_center_circle(color):
    """
    Draws the a circle at the center of the image.

    color : (r, g, b)
        color of the circle
    """
    p = image_center
    draw_flower_circle(p, p, color)


def draw_circle_selection(x, y):
    """
    Draw a selection circle.
    """
    pdb.gimp_image_select_ellipse(
        image,
        CHANNEL_OP_ADD,
        x, y,
        circle_diameter, circle_diameter)


def draw_colored_flower():
    """
    Draws the flower with colors in 'ring_colors'.
    """
    draw_center_circle(ring_colors[0])

    for x, f in enumerate((
                draw_1st_ring,
                draw_2nd_ring,
                draw_3rd_ring,
                draw_4th_ring,
                draw_5th_ring,
                draw_6th_ring
            )):
        f(ring_colors[x + 1])
        pdb.gimp_image_merge_visible_layers(image, CLIP_TO_BOTTOM_LAYER)

    draw_frame(frame_color)
    layer = pdb.gimp_image_get_layer_by_name(image, BASE)
    layer.name = COLOR_LAYER


def draw_flower_circle(x, y, color):
    """
    Draws a flower circle.

    x, y : point
        top-left corner of the circle bounding box

    color : (r, g, b)
        color of the circle
    """
    x -= circle_radius
    y -= circle_radius

    if flower_type == LINES:
        layer = make_new_layer("Circle", normal=True)
        x = x - int(line_width / 2)
        y = y - int(line_width / 2)
        dim1 = circle_diameter + line_width
        dim2 = circle_diameter - line_width

        pdb.gimp_image_select_ellipse(
            image,
            CHANNEL_OP_ADD,
            x, y,
            dim1, dim1)

        x = x + line_width
        y = y + line_width

        # Create selection for circle line:
        pdb.gimp_image_select_ellipse(
            image,
            CHANNEL_OP_SUBTRACT,
            x, y,
            dim2, dim2)
        fill_circle(layer, color)

    else:
        layer = make_new_layer("Circle")
        draw_circle_selection(x, y)
        fill_circle(layer, color)
    pdb.gimp_selection_none(image)


def draw_frame(color):
    """
    Draws the frame that surrounds the flower.

    color : (r, g, b)
        frame color
    """
    if frame_width:
        flower_dim = int(flower_radius * 2)
        frame_dim = flower_dim + frame_width * 2
        y = x = image_center - flower_radius - frame_width

        if flower_type == LINES:
            flower_dim += line_width
            frame_dim += line_width
            y = x = x - int(line_width / 2)
            
        # Create selection for frame:
        pdb.gimp_image_select_ellipse(
            image,
            CHANNEL_OP_ADD,
            x, y,
            frame_dim, frame_dim)

        # Remove the center of the selection to create a ring-frame:
        y = x = image_center - flower_radius

        if flower_type == LINES:
            y = x = x - int(line_width / 2)

        # Create selection for frame:
        pdb.gimp_image_select_ellipse(
            image,
            CHANNEL_OP_SUBTRACT,
            x, y,
            flower_dim, flower_dim)

        layer = make_new_layer("Frame", normal=True)

        fill_circle(layer, color)
        pdb.gimp_image_merge_down(image, layer, CLIP_TO_BOTTOM_LAYER)
        pdb.gimp_selection_none(image)


def draw_gradient():
    """ Create radial gradient. """
    gradient_layer = make_new_layer(GRADIENT)
    center = float(image_center)
    gradient = pdb.gimp_gradient_new("flower")

    # perimeter:
    pdb.gimp_gradient_segment_set_right_color(gradient, 0, BLACK, 100.)

    # center:
    pdb.gimp_gradient_segment_set_left_color(gradient, 0, WHITE, 100.)

    pdb.gimp_context_set_gradient(gradient)
    pdb.gimp_drawable_edit_gradient_fill(
            gradient_layer,
            GRADIENT_RADIAL,
            .0,
            TRUE,
            1,
            0,
            TRUE,
            center,
            center,
            flower_radius * 2,
            flower_radius * 2
        )
    pdb.gimp_gradient_delete(gradient)


def fill_circle(layer, color):
    """
    Fills a selection with a color.

    layer : drawable
        layer with selection

    color : (r, g, b)
        color of the circle
    """
    pdb.gimp_context_set_foreground(color)
    pdb.gimp_edit_bucket_fill(
        layer,
        BUCKET_FILL_FG,
        LAYER_MODE_NORMAL,
        100,
        0, FALSE, 0, 0)     # unused parameters


def fill_layer(layer, color):
    """
    Fills a layer with color.

    layer : drawable
        the layer to fill

    color : (r, g, b)
        the fill color
    """
    pdb.gimp_context_set_foreground(color)
    pdb.gimp_drawable_fill(layer, FILL_FOREGROUND)


def get_point_on_circle(focus_point, angle, radius):
    """
    Returns a point on the circle that corresponds to a rotation angle.

    focus_point : point of (x, y) integers
        center of the circle

    angle : float
        the rotation angle

    radius : float
        the radius of the circle

    Returns:
        x : float
        y : float
        the point on the circle.
    """
    x = (math.sin(angle) * radius) + focus_point[0]
    y = (math.cos(angle) * -radius) + focus_point[1]
    return x, y


def info_msg (msg):
    """ Used to output messages to the error console. """
    current_handler = pdb.gimp_message_get_handler()
    pdb.gimp_message_set_handler(ERROR_CONSOLE)
    gimp.message(msg)
    pdb.gimp_message_set_handler(current_handler)


def make_new_layer(layer_name, normal=FALSE, offset=FALSE):
    """
    Creates a new layer.

    Returns the layer.

    normal : boolean
        If true, then the layer mode is normal,
        else the layer mode is difference.

    offset : boolean
        When true, the layer is below.
    """
    mode = LAYER_MODE_NORMAL if normal else LAYER_MODE_DIFFERENCE
    layer = pdb.gimp_layer_new(
        image,
        image_size,
        image_size,
        RGBA_IMAGE,
        layer_name,
        100,
        mode)

    image.add_layer(layer, 0 - int(offset))
    return layer


def render_flower(
        symbol_radius,
        mode,
        flower_part,
        color1,
        color2,
        color3,
        color4,
        color5,
        color6,
        color7,
        line_w,
        frame_w,
        frame_col
    ):
    """
    Called by GIMP when the user
    selects the OK button in the script's dialog.
    Starts drawing the Flower Of Life symbol.
    """
    global image, image_center, image_size, image_focus
    global circle_diameter, circle_radius, frame_width
    global flower_radius, flower_type, line_width
    global ring_colors, frame_color, color_mode

    # Init global variables:
    frame_width = int(frame_w * SCALE)
    flower_radius = int(symbol_radius * SCALE)
    flower_type = flower_part
    line_width = int(line_w * SCALE)
    frame_color = frame_col
    color_mode = mode
    ring_colors = [color1, color2, color3, color4, color5, color6, color7]

    # Save the interface context:
    pdb.gimp_context_push()

    # Image is scaled up for anti-aliasing issues:
    scale_size = int(symbol_radius * 2 + frame_w * 2) + 2

    if flower_type == LINES:
        scale_size += line_width

    image_size = int(scale_size * SCALE)
    image_center = int(image_size / 2)
    circle_radius = int(symbol_radius / 3 * SCALE)
    circle_diameter = int(circle_radius * 2)
    image_focus = image_center, image_center

    # for selections:
    pdb.gimp_context_set_antialias(FALSE)
    pdb.gimp_context_set_feather(FALSE)

    # Create a new image:
    image = gimp.Image(image_size, image_size, RGB)

    # Turn off undo functionality:
    pdb.gimp_image_undo_group_start(image)
    pdb.gimp_display_new(image)

    if mode:
        # Create a layer for the color circles:
        color_layer = make_new_layer(BASE, normal=True)

        if flower_type != LINES:
            fill_layer(color_layer, WHITE)

        # Create random colors?:
        if mode == RANDOM_COLORS:
            for i in range(RING_COLORS_COUNT):
                for j in range(3):
                    ring_colors[i][j] = random.randint(0, 255)

            # The frame color is set to the average color:
            r = g = b = 0

            for i in range(RING_COLORS_COUNT):
                r += ring_colors[i][0]
                g += ring_colors[i][1]
                b += ring_colors[i][2]

            r = int(r / RING_COLORS_COUNT)
            g = int(g / RING_COLORS_COUNT)
            b = int(b / RING_COLORS_COUNT)
            frame_color = (r, g, b)

        draw_colored_flower()
        draw_gradient()

        # Hide the color layer and the gradient layers:
        layer = pdb.gimp_image_get_layer_by_name(image, GRADIENT)
        pdb.gimp_item_set_visible(layer, FALSE)

        layer_copy = pdb.gimp_layer_copy(layer, TRUE)
        image.add_layer(layer_copy, 0)

        layer = pdb.gimp_image_get_layer_by_name(image, COLOR_LAYER)
        pdb.gimp_item_set_visible(layer, FALSE)

    base_layer = make_new_layer(BASE, normal=True, offset=mode > 0)

    if flower_type != LINES:
        fill_layer(base_layer, WHITE)

    draw_black_and_white()
    create_bw_alpha()

    # Merges the base's mask with the base layer:
    pdb.gimp_image_merge_visible_layers(image, CLIP_TO_BOTTOM_LAYER)

    if mode:
        # Transfer alpha to color layer:
        layer = pdb.gimp_image_get_layer_by_name(image, BASE)
        mask = pdb.gimp_layer_create_mask(layer, ADD_MASK_ALPHA)
        layer = pdb.gimp_image_get_layer_by_name(image, COLOR_LAYER)

        pdb.gimp_layer_add_mask(layer, mask)

        # Delete base layer:
        layer = pdb.gimp_image_get_layer_by_name(image, BASE)
        pdb.gimp_image_remove_layer(image, layer)

        # Make the three layers visible and merge:
        for i in (GRADIENT, GRADIENT + " copy", COLOR_LAYER):
            layer = pdb.gimp_image_get_layer_by_name(image, i)
            pdb.gimp_item_set_visible(layer, TRUE)

        pdb.gimp_image_merge_visible_layers(image, CLIP_TO_BOTTOM_LAYER)

        # Lets the user know about the color palette:
        msg = ""

        for i in ring_colors:
            msg += ("\t {r}, {g}, {b}\n").format(r=i[0], g=i[1], b=i[2])
        info_msg("The colors used in the flower:\n" + msg)

    else:
        # Invert the white image into black:
        layer = pdb.gimp_image_get_layer_by_name(image, BASE)
        pdb.gimp_drawable_invert(layer, TRUE)

    # Scale the image back to fix anti-aliasing issues:
    pdb.gimp_image_scale_full(image, scale_size, scale_size, INTERPOLATION_CUBIC)

    # Return undo functionality:
    pdb.gimp_image_undo_group_end(image)

    # Restore the interface context:
    pdb.gimp_context_pop()


register(
    # name
    # becomes dialog title as python-fu + name
    # Space character is not allowed.
    # 'name' is case-sensitive:
    "Render-Flower-Of-Life-Symbol",

    # tool-tip and window-tip text:
    "Renders a Flower Of Life symbol.",

    # help (describe how-to, exceptions and dependencies).
    # This info will display in the plug-in browser:
    "Creates a new image and does not require an open image.",

    # The author is displayed in the plug-in browser:
    "Charles Bartley",

    # The copyright is displayed in the plug-in browser:
    "Charles Bartley",

    # The date is displayed in the plug-in browser:
    "2020",

    # menu item descriptor:
    "Flower Of Life...",

    # image types
    # An empty string equates to no image:
    "",

    # dialog parameters:
    [
        (
            PF_SPINNER,
            "symbol_radius",
            "Symbol Radius:",
            600,
            (60, 18000, 10)),

        (
            PF_OPTION,
            "mode",
            "Mode:",
            2,
            (
                "Black And White",
                "Preset Colors",
                "Random Colors")),

        (
            PF_OPTION,
            "flower_type",
            "Flower Type:",
            2,
            (
                "Lines",
                "Petals",
                "Circles")),

        (
            PF_COLOR,
            "color1",
            "Preset Center:",
            (.0, 1.0, .0)),

        (
            PF_COLOR,
            "color2",
            "Preset Ring One:",
            (.0, .9, .0)),

        (
            PF_COLOR,
            "color3",
            "Preset Ring Two:",
            (.0, .8, .0)),

        (
            PF_COLOR,
            "color4",
            "Preset Ring Three:",
            (.0, .7, .0)),

        (
            PF_COLOR,
            "color5",
            "Preset Ring Four:",
            (.0, .6, .0)),

        (
            PF_COLOR,
            "color6",
            "Preset Ring Five:",
            (.0, .5, .0)),

        (
            PF_COLOR,
            "color7",
            "Preset Ring Six:",
            (.0, .4, .0)),

        (
            PF_SPINNER,
            "line_width",
            "Line Width:",
            8,
            (1, 20, 1)),

        (
            PF_SPINNER,
            "frame_width",
            "Frame Width:",
            0,
            (0, 100, 1)),

        (
            PF_COLOR,
            "frame_color",
            "Preset Frame Color:",
            (.0, .3, .0)),
    ],

    # results:
    [],

    # dialog function handler
    # The second item is the menu's location:
    render_flower, menu="<Image>/Filters/Render")

main()
