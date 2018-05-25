'''Autogenerated by xml_generate script, do not edit!'''
from OpenGL import platform as _p, arrays
# Code generation uses this
from OpenGL.raw.GLES2 import _types as _cs
# End users want this...
from OpenGL.raw.GLES2._types import *
from OpenGL.raw.GLES2 import _errors
from OpenGL.constant import Constant as _C

import ctypes
_EXTENSION_NAME = 'GLES2_EXT_pvrtc_sRGB'
def _f( function ):
    return _p.createFunction( function,_p.PLATFORM.GLES2,'GLES2_EXT_pvrtc_sRGB',error_checker=_errors._error_checker)
GL_COMPRESSED_SRGB_ALPHA_PVRTC_2BPPV1_EXT=_C('GL_COMPRESSED_SRGB_ALPHA_PVRTC_2BPPV1_EXT',0x8A56)
GL_COMPRESSED_SRGB_ALPHA_PVRTC_4BPPV1_EXT=_C('GL_COMPRESSED_SRGB_ALPHA_PVRTC_4BPPV1_EXT',0x8A57)
GL_COMPRESSED_SRGB_PVRTC_2BPPV1_EXT=_C('GL_COMPRESSED_SRGB_PVRTC_2BPPV1_EXT',0x8A54)
GL_COMPRESSED_SRGB_PVRTC_4BPPV1_EXT=_C('GL_COMPRESSED_SRGB_PVRTC_4BPPV1_EXT',0x8A55)

