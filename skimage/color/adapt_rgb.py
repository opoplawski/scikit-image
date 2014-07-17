import functools

import numpy as np

from skimage import img_as_float
from skimage import color
from skimage.exposure import rescale_intensity
from skimage.util.dtype import convert


__all__ = ['adapt_rgb', 'hsv_value', 'each_channel']


def is_rgb_like(image):
    """Return True if the image *looks* like it's RGB.

    This function should not be public because it is only intended to be used
    for functions that don't accept volumes as input, since checking an image's
    shape is fragile.
    """
    return (image.ndim == 3) and (image.shape[2] in (3, 4))


def adapt_rgb(apply_to_rgb):
    """Return decorator that adapts to RGB images to a gray-scale filter.

    This function is only intended to be used for functions that don't accept
    volumes as input, since checking an image's shape is fragile.

    Parameters
    ----------
    apply_to_rgb : function
        Function that returns a filtered image from an image-filter and RGB
        image. This will only be called if the image is RGB-like.
    """
    def decorator(image_filter):
        # @functools.wraps
        def image_filter_adapted(image, *args, **kwargs):
            if is_rgb_like(image):
                return apply_to_rgb(image_filter, image, *args, **kwargs)
            else:
                return image_filter(image, *args, **kwargs)
        return image_filter_adapted
    return decorator


def hsv_value(image_filter, image, *args, **kwargs):
    """Return color image by applying `image_filter` on HSV-value of `image`.

    Note that this function is intended for use with `adapt_rgb`.

    Parameters
    ----------
    image_filter : function
        Function that filters a gray-scale image.
    image : array
        Input image. Note that RGBA images are treated as RGB.
    """
    # XXX: Are these 2 lines really necessary?
    image = img_as_float(image[:, :, :3])
    image = rescale_intensity(image)
    # Slice the first three channels so that we remove any alpha channels.
    hsv = color.rgb2hsv(image)
    value = hsv[:, :, 2].copy()
    value = image_filter(value, *args, **kwargs)
    hsv[:, :, 2] = convert(value, hsv.dtype)
    return color.hsv2rgb(hsv)


def each_channel(image_filter, image, *args, **kwargs):
    """Return color image by applying `image_filter` on channels of `image`.

    Note that this function is intended for use with `adapt_rgb`.

    Parameters
    ----------
    image_filter : function
        Function that filters a gray-scale image.
    image : array
        Input image.
    """
    c_new = [image_filter(c, *args, **kwargs) for c in image.T]
    return np.array(c_new).T
