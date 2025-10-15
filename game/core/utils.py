"""
Utility functions for game operations
"""
import pygame
import math


def clamp(value, min_val, max_val):
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(start, end, t):
    """Linear interpolation"""
    return start + (end - start) * t


def ease_in_quad(t):
    """Quadratic ease-in"""
    return t * t


def ease_out_quad(t):
    """Quadratic ease-out"""
    return 1 - (1 - t) * (1 - t)


def ease_in_out_quad(t):
    """Quadratic ease-in-out"""
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - pow(-2 * t + 2, 2) / 2


def rect_overlaps(rect1, rect2):
    """Check if two pygame Rects overlap"""
    return rect1.colliderect(rect2)


def point_in_rect(point, rect):
    """Check if point (x, y) is inside rect"""
    return rect.collidepoint(point)


def distance(p1, p2):
    """Euclidean distance between two points"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)


def normalize_vector(vx, vy):
    """Normalize a 2D vector"""
    mag = math.sqrt(vx * vx + vy * vy)
    if mag == 0:
        return 0, 0
    return vx / mag, vy / mag


def sign(value):
    """Return sign of value: -1, 0, or 1"""
    if value > 0:
        return 1
    elif value < 0:
        return -1
    return 0
