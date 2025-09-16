/**
 * Standard WebGL, WebGL2 and extension constants (OpenGL constants)
 * @note (Most) of these constants are also defined on the WebGLRenderingContext interface.
 * @see https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/Constants
 * @privateRemarks Locally called `GLEnum` instead of `GL`, because `babel-plugin-inline-webl-constants`
 *  both depends on and processes this module, but shouldn't replace these declarations.
 */
declare enum GLEnum {
    /** Passed to clear to clear the current depth buffer. */
    DEPTH_BUFFER_BIT = 256,
    /** Passed to clear to clear the current stencil buffer. */
    STENCIL_BUFFER_BIT = 1024,
    /** Passed to clear to clear the current color buffer. */
    COLOR_BUFFER_BIT = 16384,
    /** Passed to drawElements or drawArrays to draw single points. */
    POINTS = 0,
    /** Passed to drawElements or drawArrays to draw lines. Each vertex connects to the one after it. */
    LINES = 1,
    /** Passed to drawElements or drawArrays to draw lines. Each set of two vertices is treated as a separate line segment. */
    LINE_LOOP = 2,
    /** Passed to drawElements or drawArrays to draw a connected group of line segments from the first vertex to the last. */
    LINE_STRIP = 3,
    /** Passed to drawElements or drawArrays to draw triangles. Each set of three vertices creates a separate triangle. */
    TRIANGLES = 4,
    /** Passed to drawElements or drawArrays to draw a connected group of triangles. */
    TRIANGLE_STRIP = 5,
    /** Passed to drawElements or drawArrays to draw a connected group of triangles. Each vertex connects to the previous and the first vertex in the fan. */
    TRIANGLE_FAN = 6,
    /** Passed to blendFunc or blendFuncSeparate to turn off a component. */
    ZERO = 0,
    /** Passed to blendFunc or blendFuncSeparate to turn on a component. */
    ONE = 1,
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the source elements color. */
    SRC_COLOR = 768,
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by one minus the source elements color. */
    ONE_MINUS_SRC_COLOR = 769,
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the source's alpha. */
    SRC_ALPHA = 770,
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by one minus the source's alpha. */
    ONE_MINUS_SRC_ALPHA = 771,
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the destination's alpha. */
    DST_ALPHA = 772,
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by one minus the destination's alpha. */
    ONE_MINUS_DST_ALPHA = 773,
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the destination's color. */
    DST_COLOR = 774,
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by one minus the destination's color. */
    ONE_MINUS_DST_COLOR = 775,
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the minimum of source's alpha or one minus the destination's alpha. */
    SRC_ALPHA_SATURATE = 776,
    /** Passed to blendFunc or blendFuncSeparate to specify a constant color blend function. */
    CONSTANT_COLOR = 32769,
    /** Passed to blendFunc or blendFuncSeparate to specify one minus a constant color blend function. */
    ONE_MINUS_CONSTANT_COLOR = 32770,
    /** Passed to blendFunc or blendFuncSeparate to specify a constant alpha blend function. */
    CONSTANT_ALPHA = 32771,
    /** Passed to blendFunc or blendFuncSeparate to specify one minus a constant alpha blend function. */
    ONE_MINUS_CONSTANT_ALPHA = 32772,
    /** Passed to blendEquation or blendEquationSeparate to set an addition blend function. */
    /** Passed to blendEquation or blendEquationSeparate to specify a subtraction blend function (source - destination). */
    /** Passed to blendEquation or blendEquationSeparate to specify a reverse subtraction blend function (destination - source). */
    FUNC_ADD = 32774,
    FUNC_SUBTRACT = 32778,
    FUNC_REVERSE_SUBTRACT = 32779,
    /** Passed to getParameter to get the current RGB blend function. */
    BLEND_EQUATION = 32777,
    /** Passed to getParameter to get the current RGB blend function. Same as BLEND_EQUATION */
    BLEND_EQUATION_RGB = 32777,
    /** Passed to getParameter to get the current alpha blend function. Same as BLEND_EQUATION */
    BLEND_EQUATION_ALPHA = 34877,
    /** Passed to getParameter to get the current destination RGB blend function. */
    BLEND_DST_RGB = 32968,
    /** Passed to getParameter to get the current destination RGB blend function. */
    BLEND_SRC_RGB = 32969,
    /** Passed to getParameter to get the current destination alpha blend function. */
    BLEND_DST_ALPHA = 32970,
    /** Passed to getParameter to get the current source alpha blend function. */
    BLEND_SRC_ALPHA = 32971,
    /** Passed to getParameter to return a the current blend color. */
    BLEND_COLOR = 32773,
    /** Passed to getParameter to get the array buffer binding. */
    ARRAY_BUFFER_BINDING = 34964,
    /** Passed to getParameter to get the current element array buffer. */
    ELEMENT_ARRAY_BUFFER_BINDING = 34965,
    /** Passed to getParameter to get the current lineWidth (set by the lineWidth method). */
    LINE_WIDTH = 2849,
    /** Passed to getParameter to get the current size of a point drawn with gl.POINTS */
    ALIASED_POINT_SIZE_RANGE = 33901,
    /** Passed to getParameter to get the range of available widths for a line. Returns a length-2 array with the lo value at 0, and high at 1. */
    ALIASED_LINE_WIDTH_RANGE = 33902,
    /** Passed to getParameter to get the current value of cullFace. Should return FRONT, BACK, or FRONT_AND_BACK */
    CULL_FACE_MODE = 2885,
    /** Passed to getParameter to determine the current value of frontFace. Should return CW or CCW. */
    FRONT_FACE = 2886,
    /** Passed to getParameter to return a length-2 array of floats giving the current depth range. */
    DEPTH_RANGE = 2928,
    /** Passed to getParameter to determine if the depth write mask is enabled. */
    DEPTH_WRITEMASK = 2930,
    /** Passed to getParameter to determine the current depth clear value. */
    DEPTH_CLEAR_VALUE = 2931,
    /** Passed to getParameter to get the current depth function. Returns NEVER, ALWAYS, LESS, EQUAL, LEQUAL, GREATER, GEQUAL, or NOTEQUAL. */
    DEPTH_FUNC = 2932,
    /** Passed to getParameter to get the value the stencil will be cleared to. */
    STENCIL_CLEAR_VALUE = 2961,
    /** Passed to getParameter to get the current stencil function. Returns NEVER, ALWAYS, LESS, EQUAL, LEQUAL, GREATER, GEQUAL, or NOTEQUAL. */
    STENCIL_FUNC = 2962,
    /** Passed to getParameter to get the current stencil fail function. Should return KEEP, REPLACE, INCR, DECR, INVERT, INCR_WRAP, or DECR_WRAP. */
    STENCIL_FAIL = 2964,
    /** Passed to getParameter to get the current stencil fail function should the depth buffer test fail. Should return KEEP, REPLACE, INCR, DECR, INVERT, INCR_WRAP, or DECR_WRAP. */
    STENCIL_PASS_DEPTH_FAIL = 2965,
    /** Passed to getParameter to get the current stencil fail function should the depth buffer test pass. Should return KEEP, REPLACE, INCR, DECR, INVERT, INCR_WRAP, or DECR_WRAP. */
    STENCIL_PASS_DEPTH_PASS = 2966,
    /** Passed to getParameter to get the reference value used for stencil tests. */
    STENCIL_REF = 2967,
    STENCIL_VALUE_MASK = 2963,
    STENCIL_WRITEMASK = 2968,
    STENCIL_BACK_FUNC = 34816,
    STENCIL_BACK_FAIL = 34817,
    STENCIL_BACK_PASS_DEPTH_FAIL = 34818,
    STENCIL_BACK_PASS_DEPTH_PASS = 34819,
    STENCIL_BACK_REF = 36003,
    STENCIL_BACK_VALUE_MASK = 36004,
    STENCIL_BACK_WRITEMASK = 36005,
    /** An Int32Array with four elements for the current viewport dimensions. */
    VIEWPORT = 2978,
    /** An Int32Array with four elements for the current scissor box dimensions. */
    SCISSOR_BOX = 3088,
    COLOR_CLEAR_VALUE = 3106,
    COLOR_WRITEMASK = 3107,
    UNPACK_ALIGNMENT = 3317,
    PACK_ALIGNMENT = 3333,
    MAX_TEXTURE_SIZE = 3379,
    MAX_VIEWPORT_DIMS = 3386,
    SUBPIXEL_BITS = 3408,
    RED_BITS = 3410,
    GREEN_BITS = 3411,
    BLUE_BITS = 3412,
    ALPHA_BITS = 3413,
    DEPTH_BITS = 3414,
    STENCIL_BITS = 3415,
    POLYGON_OFFSET_UNITS = 10752,
    POLYGON_OFFSET_FACTOR = 32824,
    TEXTURE_BINDING_2D = 32873,
    SAMPLE_BUFFERS = 32936,
    SAMPLES = 32937,
    SAMPLE_COVERAGE_VALUE = 32938,
    SAMPLE_COVERAGE_INVERT = 32939,
    COMPRESSED_TEXTURE_FORMATS = 34467,
    VENDOR = 7936,
    RENDERER = 7937,
    VERSION = 7938,
    IMPLEMENTATION_COLOR_READ_TYPE = 35738,
    IMPLEMENTATION_COLOR_READ_FORMAT = 35739,
    BROWSER_DEFAULT_WEBGL = 37444,
    /** Passed to bufferData as a hint about whether the contents of the buffer are likely to be used often and not change often. */
    STATIC_DRAW = 35044,
    /** Passed to bufferData as a hint about whether the contents of the buffer are likely to not be used often. */
    STREAM_DRAW = 35040,
    /** Passed to bufferData as a hint about whether the contents of the buffer are likely to be used often and change often. */
    DYNAMIC_DRAW = 35048,
    /** Passed to bindBuffer or bufferData to specify the type of buffer being used. */
    ARRAY_BUFFER = 34962,
    /** Passed to bindBuffer or bufferData to specify the type of buffer being used. */
    ELEMENT_ARRAY_BUFFER = 34963,
    /** Passed to getBufferParameter to get a buffer's size. */
    BUFFER_SIZE = 34660,
    /** Passed to getBufferParameter to get the hint for the buffer passed in when it was created. */
    BUFFER_USAGE = 34661,
    /** Passed to getVertexAttrib to read back the current vertex attribute. */
    CURRENT_VERTEX_ATTRIB = 34342,
    VERTEX_ATTRIB_ARRAY_ENABLED = 34338,
    VERTEX_ATTRIB_ARRAY_SIZE = 34339,
    VERTEX_ATTRIB_ARRAY_STRIDE = 34340,
    VERTEX_ATTRIB_ARRAY_TYPE = 34341,
    VERTEX_ATTRIB_ARRAY_NORMALIZED = 34922,
    VERTEX_ATTRIB_ARRAY_POINTER = 34373,
    VERTEX_ATTRIB_ARRAY_BUFFER_BINDING = 34975,
    /** Passed to enable/disable to turn on/off culling. Can also be used with getParameter to find the current culling method. */
    CULL_FACE = 2884,
    /** Passed to cullFace to specify that only front faces should be culled. */
    FRONT = 1028,
    /** Passed to cullFace to specify that only back faces should be culled. */
    BACK = 1029,
    /** Passed to cullFace to specify that front and back faces should be culled. */
    FRONT_AND_BACK = 1032,
    /** Passed to enable/disable to turn on/off blending. Can also be used with getParameter to find the current blending method. */
    BLEND = 3042,
    /** Passed to enable/disable to turn on/off the depth test. Can also be used with getParameter to query the depth test. */
    DEPTH_TEST = 2929,
    /** Passed to enable/disable to turn on/off dithering. Can also be used with getParameter to find the current dithering method. */
    DITHER = 3024,
    /** Passed to enable/disable to turn on/off the polygon offset. Useful for rendering hidden-line images, decals, and or solids with highlighted edges. Can also be used with getParameter to query the scissor test. */
    POLYGON_OFFSET_FILL = 32823,
    /** Passed to enable/disable to turn on/off the alpha to coverage. Used in multi-sampling alpha channels. */
    SAMPLE_ALPHA_TO_COVERAGE = 32926,
    /** Passed to enable/disable to turn on/off the sample coverage. Used in multi-sampling. */
    SAMPLE_COVERAGE = 32928,
    /** Passed to enable/disable to turn on/off the scissor test. Can also be used with getParameter to query the scissor test. */
    SCISSOR_TEST = 3089,
    /** Passed to enable/disable to turn on/off the stencil test. Can also be used with getParameter to query the stencil test. */
    STENCIL_TEST = 2960,
    /** Returned from getError(). */
    NO_ERROR = 0,
    /** Returned from getError(). */
    INVALID_ENUM = 1280,
    /** Returned from getError(). */
    INVALID_VALUE = 1281,
    /** Returned from getError(). */
    INVALID_OPERATION = 1282,
    /** Returned from getError(). */
    OUT_OF_MEMORY = 1285,
    /** Returned from getError(). */
    CONTEXT_LOST_WEBGL = 37442,
    /** Passed to frontFace to specify the front face of a polygon is drawn in the clockwise direction */
    CW = 2304,
    /** Passed to frontFace to specify the front face of a polygon is drawn in the counter clockwise direction */
    CCW = 2305,
    /** There is no preference for this behavior. */
    DONT_CARE = 4352,
    /** The most efficient behavior should be used. */
    FASTEST = 4353,
    /** The most correct or the highest quality option should be used. */
    NICEST = 4354,
    /** Hint for the quality of filtering when generating mipmap images with WebGLRenderingContext.generateMipmap(). */
    GENERATE_MIPMAP_HINT = 33170,
    BYTE = 5120,
    UNSIGNED_BYTE = 5121,
    SHORT = 5122,
    UNSIGNED_SHORT = 5123,
    INT = 5124,
    UNSIGNED_INT = 5125,
    FLOAT = 5126,
    DOUBLE = 5130,
    DEPTH_COMPONENT = 6402,
    ALPHA = 6406,
    RGB = 6407,
    RGBA = 6408,
    LUMINANCE = 6409,
    LUMINANCE_ALPHA = 6410,
    UNSIGNED_SHORT_4_4_4_4 = 32819,
    UNSIGNED_SHORT_5_5_5_1 = 32820,
    UNSIGNED_SHORT_5_6_5 = 33635,
    /** Passed to createShader to define a fragment shader. */
    FRAGMENT_SHADER = 35632,
    /** Passed to createShader to define a vertex shader */
    VERTEX_SHADER = 35633,
    /** Passed to getShaderParameter to get the status of the compilation. Returns false if the shader was not compiled. You can then query getShaderInfoLog to find the exact error */
    COMPILE_STATUS = 35713,
    /** Passed to getShaderParameter to determine if a shader was deleted via deleteShader. Returns true if it was, false otherwise. */
    DELETE_STATUS = 35712,
    /** Passed to getProgramParameter after calling linkProgram to determine if a program was linked correctly. Returns false if there were errors. Use getProgramInfoLog to find the exact error. */
    LINK_STATUS = 35714,
    /** Passed to getProgramParameter after calling validateProgram to determine if it is valid. Returns false if errors were found. */
    VALIDATE_STATUS = 35715,
    /** Passed to getProgramParameter after calling attachShader to determine if the shader was attached correctly. Returns false if errors occurred. */
    ATTACHED_SHADERS = 35717,
    /** Passed to getProgramParameter to get the number of attributes active in a program. */
    ACTIVE_ATTRIBUTES = 35721,
    /** Passed to getProgramParameter to get the number of uniforms active in a program. */
    ACTIVE_UNIFORMS = 35718,
    /** The maximum number of entries possible in the vertex attribute list. */
    MAX_VERTEX_ATTRIBS = 34921,
    MAX_VERTEX_UNIFORM_VECTORS = 36347,
    MAX_VARYING_VECTORS = 36348,
    MAX_COMBINED_TEXTURE_IMAGE_UNITS = 35661,
    MAX_VERTEX_TEXTURE_IMAGE_UNITS = 35660,
    /** Implementation dependent number of maximum texture units. At least 8. */
    MAX_TEXTURE_IMAGE_UNITS = 34930,
    MAX_FRAGMENT_UNIFORM_VECTORS = 36349,
    SHADER_TYPE = 35663,
    SHADING_LANGUAGE_VERSION = 35724,
    CURRENT_PROGRAM = 35725,
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will never pass, i.e., nothing will be drawn. */
    NEVER = 512,
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is less than the stored value. */
    LESS = 513,
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is equals to the stored value. */
    EQUAL = 514,
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is less than or equal to the stored value. */
    LEQUAL = 515,
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is greater than the stored value. */
    GREATER = 516,
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is not equal to the stored value. */
    NOTEQUAL = 517,
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is greater than or equal to the stored value. */
    GEQUAL = 518,
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will always pass, i.e., pixels will be drawn in the order they are drawn. */
    ALWAYS = 519,
    KEEP = 7680,
    REPLACE = 7681,
    INCR = 7682,
    DECR = 7683,
    INVERT = 5386,
    INCR_WRAP = 34055,
    DECR_WRAP = 34056,
    NEAREST = 9728,
    LINEAR = 9729,
    NEAREST_MIPMAP_NEAREST = 9984,
    LINEAR_MIPMAP_NEAREST = 9985,
    NEAREST_MIPMAP_LINEAR = 9986,
    LINEAR_MIPMAP_LINEAR = 9987,
    /** The texture magnification function is used when the pixel being textured maps to an area less than or equal to one texture element. It sets the texture magnification function to either GL_NEAREST or GL_LINEAR (see below). GL_NEAREST is generally faster than GL_LINEAR, but it can produce textured images with sharper edges because the transition between texture elements is not as smooth. Default: GL_LINEAR.  */
    TEXTURE_MAG_FILTER = 10240,
    /** The texture minifying function is used whenever the pixel being textured maps to an area greater than one texture element. There are six defined minifying functions. Two of them use the nearest one or nearest four texture elements to compute the texture value. The other four use mipmaps. Default: GL_NEAREST_MIPMAP_LINEAR */
    TEXTURE_MIN_FILTER = 10241,
    /** Sets the wrap parameter for texture coordinate  to either GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, or GL_REPEAT. G */
    TEXTURE_WRAP_S = 10242,
    /** Sets the wrap parameter for texture coordinate  to either GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, or GL_REPEAT. G */
    TEXTURE_WRAP_T = 10243,
    TEXTURE_2D = 3553,
    TEXTURE = 5890,
    TEXTURE_CUBE_MAP = 34067,
    TEXTURE_BINDING_CUBE_MAP = 34068,
    TEXTURE_CUBE_MAP_POSITIVE_X = 34069,
    TEXTURE_CUBE_MAP_NEGATIVE_X = 34070,
    TEXTURE_CUBE_MAP_POSITIVE_Y = 34071,
    TEXTURE_CUBE_MAP_NEGATIVE_Y = 34072,
    TEXTURE_CUBE_MAP_POSITIVE_Z = 34073,
    TEXTURE_CUBE_MAP_NEGATIVE_Z = 34074,
    MAX_CUBE_MAP_TEXTURE_SIZE = 34076,
    TEXTURE0 = 33984,
    ACTIVE_TEXTURE = 34016,
    REPEAT = 10497,
    CLAMP_TO_EDGE = 33071,
    MIRRORED_REPEAT = 33648,
    TEXTURE_WIDTH = 4096,
    TEXTURE_HEIGHT = 4097,
    FLOAT_VEC2 = 35664,
    FLOAT_VEC3 = 35665,
    FLOAT_VEC4 = 35666,
    INT_VEC2 = 35667,
    INT_VEC3 = 35668,
    INT_VEC4 = 35669,
    BOOL = 35670,
    BOOL_VEC2 = 35671,
    BOOL_VEC3 = 35672,
    BOOL_VEC4 = 35673,
    FLOAT_MAT2 = 35674,
    FLOAT_MAT3 = 35675,
    FLOAT_MAT4 = 35676,
    SAMPLER_2D = 35678,
    SAMPLER_CUBE = 35680,
    LOW_FLOAT = 36336,
    MEDIUM_FLOAT = 36337,
    HIGH_FLOAT = 36338,
    LOW_INT = 36339,
    MEDIUM_INT = 36340,
    HIGH_INT = 36341,
    FRAMEBUFFER = 36160,
    RENDERBUFFER = 36161,
    RGBA4 = 32854,
    RGB5_A1 = 32855,
    RGB565 = 36194,
    DEPTH_COMPONENT16 = 33189,
    STENCIL_INDEX = 6401,
    STENCIL_INDEX8 = 36168,
    DEPTH_STENCIL = 34041,
    RENDERBUFFER_WIDTH = 36162,
    RENDERBUFFER_HEIGHT = 36163,
    RENDERBUFFER_INTERNAL_FORMAT = 36164,
    RENDERBUFFER_RED_SIZE = 36176,
    RENDERBUFFER_GREEN_SIZE = 36177,
    RENDERBUFFER_BLUE_SIZE = 36178,
    RENDERBUFFER_ALPHA_SIZE = 36179,
    RENDERBUFFER_DEPTH_SIZE = 36180,
    RENDERBUFFER_STENCIL_SIZE = 36181,
    FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE = 36048,
    FRAMEBUFFER_ATTACHMENT_OBJECT_NAME = 36049,
    FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL = 36050,
    FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE = 36051,
    COLOR_ATTACHMENT0 = 36064,
    DEPTH_ATTACHMENT = 36096,
    STENCIL_ATTACHMENT = 36128,
    DEPTH_STENCIL_ATTACHMENT = 33306,
    NONE = 0,
    FRAMEBUFFER_COMPLETE = 36053,
    FRAMEBUFFER_INCOMPLETE_ATTACHMENT = 36054,
    FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT = 36055,
    FRAMEBUFFER_INCOMPLETE_DIMENSIONS = 36057,
    FRAMEBUFFER_UNSUPPORTED = 36061,
    FRAMEBUFFER_BINDING = 36006,
    RENDERBUFFER_BINDING = 36007,
    READ_FRAMEBUFFER = 36008,
    DRAW_FRAMEBUFFER = 36009,
    MAX_RENDERBUFFER_SIZE = 34024,
    INVALID_FRAMEBUFFER_OPERATION = 1286,
    UNPACK_FLIP_Y_WEBGL = 37440,
    UNPACK_PREMULTIPLY_ALPHA_WEBGL = 37441,
    UNPACK_COLORSPACE_CONVERSION_WEBGL = 37443,
    READ_BUFFER = 3074,
    UNPACK_ROW_LENGTH = 3314,
    UNPACK_SKIP_ROWS = 3315,
    UNPACK_SKIP_PIXELS = 3316,
    PACK_ROW_LENGTH = 3330,
    PACK_SKIP_ROWS = 3331,
    PACK_SKIP_PIXELS = 3332,
    TEXTURE_BINDING_3D = 32874,
    UNPACK_SKIP_IMAGES = 32877,
    UNPACK_IMAGE_HEIGHT = 32878,
    MAX_3D_TEXTURE_SIZE = 32883,
    MAX_ELEMENTS_VERTICES = 33000,
    MAX_ELEMENTS_INDICES = 33001,
    MAX_TEXTURE_LOD_BIAS = 34045,
    MAX_FRAGMENT_UNIFORM_COMPONENTS = 35657,
    MAX_VERTEX_UNIFORM_COMPONENTS = 35658,
    MAX_ARRAY_TEXTURE_LAYERS = 35071,
    MIN_PROGRAM_TEXEL_OFFSET = 35076,
    MAX_PROGRAM_TEXEL_OFFSET = 35077,
    MAX_VARYING_COMPONENTS = 35659,
    FRAGMENT_SHADER_DERIVATIVE_HINT = 35723,
    RASTERIZER_DISCARD = 35977,
    VERTEX_ARRAY_BINDING = 34229,
    MAX_VERTEX_OUTPUT_COMPONENTS = 37154,
    MAX_FRAGMENT_INPUT_COMPONENTS = 37157,
    MAX_SERVER_WAIT_TIMEOUT = 37137,
    MAX_ELEMENT_INDEX = 36203,
    RED = 6403,
    RGB8 = 32849,
    RGBA8 = 32856,
    RGB10_A2 = 32857,
    TEXTURE_3D = 32879,
    /** Sets the wrap parameter for texture coordinate  to either GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, or GL_REPEAT. G */
    TEXTURE_WRAP_R = 32882,
    TEXTURE_MIN_LOD = 33082,
    TEXTURE_MAX_LOD = 33083,
    TEXTURE_BASE_LEVEL = 33084,
    TEXTURE_MAX_LEVEL = 33085,
    TEXTURE_COMPARE_MODE = 34892,
    TEXTURE_COMPARE_FUNC = 34893,
    SRGB = 35904,
    SRGB8 = 35905,
    SRGB8_ALPHA8 = 35907,
    COMPARE_REF_TO_TEXTURE = 34894,
    RGBA32F = 34836,
    RGB32F = 34837,
    RGBA16F = 34842,
    RGB16F = 34843,
    TEXTURE_2D_ARRAY = 35866,
    TEXTURE_BINDING_2D_ARRAY = 35869,
    R11F_G11F_B10F = 35898,
    RGB9_E5 = 35901,
    RGBA32UI = 36208,
    RGB32UI = 36209,
    RGBA16UI = 36214,
    RGB16UI = 36215,
    RGBA8UI = 36220,
    RGB8UI = 36221,
    RGBA32I = 36226,
    RGB32I = 36227,
    RGBA16I = 36232,
    RGB16I = 36233,
    RGBA8I = 36238,
    RGB8I = 36239,
    RED_INTEGER = 36244,
    RGB_INTEGER = 36248,
    RGBA_INTEGER = 36249,
    R8 = 33321,
    RG8 = 33323,
    R16F = 33325,
    R32F = 33326,
    RG16F = 33327,
    RG32F = 33328,
    R8I = 33329,
    R8UI = 33330,
    R16I = 33331,
    R16UI = 33332,
    R32I = 33333,
    R32UI = 33334,
    RG8I = 33335,
    RG8UI = 33336,
    RG16I = 33337,
    RG16UI = 33338,
    RG32I = 33339,
    RG32UI = 33340,
    R8_SNORM = 36756,
    RG8_SNORM = 36757,
    RGB8_SNORM = 36758,
    RGBA8_SNORM = 36759,
    RGB10_A2UI = 36975,
    TEXTURE_IMMUTABLE_FORMAT = 37167,
    TEXTURE_IMMUTABLE_LEVELS = 33503,
    UNSIGNED_INT_2_10_10_10_REV = 33640,
    UNSIGNED_INT_10F_11F_11F_REV = 35899,
    UNSIGNED_INT_5_9_9_9_REV = 35902,
    FLOAT_32_UNSIGNED_INT_24_8_REV = 36269,
    UNSIGNED_INT_24_8 = 34042,
    HALF_FLOAT = 5131,
    RG = 33319,
    RG_INTEGER = 33320,
    INT_2_10_10_10_REV = 36255,
    CURRENT_QUERY = 34917,
    /** Returns a GLuint containing the query result. */
    QUERY_RESULT = 34918,
    /** Whether query result is available. */
    QUERY_RESULT_AVAILABLE = 34919,
    /** Occlusion query (if drawing passed depth test)  */
    ANY_SAMPLES_PASSED = 35887,
    /** Occlusion query less accurate/faster version */
    ANY_SAMPLES_PASSED_CONSERVATIVE = 36202,
    MAX_DRAW_BUFFERS = 34852,
    DRAW_BUFFER0 = 34853,
    DRAW_BUFFER1 = 34854,
    DRAW_BUFFER2 = 34855,
    DRAW_BUFFER3 = 34856,
    DRAW_BUFFER4 = 34857,
    DRAW_BUFFER5 = 34858,
    DRAW_BUFFER6 = 34859,
    DRAW_BUFFER7 = 34860,
    DRAW_BUFFER8 = 34861,
    DRAW_BUFFER9 = 34862,
    DRAW_BUFFER10 = 34863,
    DRAW_BUFFER11 = 34864,
    DRAW_BUFFER12 = 34865,
    DRAW_BUFFER13 = 34866,
    DRAW_BUFFER14 = 34867,
    DRAW_BUFFER15 = 34868,
    MAX_COLOR_ATTACHMENTS = 36063,
    COLOR_ATTACHMENT1 = 36065,
    COLOR_ATTACHMENT2 = 36066,
    COLOR_ATTACHMENT3 = 36067,
    COLOR_ATTACHMENT4 = 36068,
    COLOR_ATTACHMENT5 = 36069,
    COLOR_ATTACHMENT6 = 36070,
    COLOR_ATTACHMENT7 = 36071,
    COLOR_ATTACHMENT8 = 36072,
    COLOR_ATTACHMENT9 = 36073,
    COLOR_ATTACHMENT10 = 36074,
    COLOR_ATTACHMENT11 = 36075,
    COLOR_ATTACHMENT12 = 36076,
    COLOR_ATTACHMENT13 = 36077,
    COLOR_ATTACHMENT14 = 36078,
    COLOR_ATTACHMENT15 = 36079,
    SAMPLER_3D = 35679,
    SAMPLER_2D_SHADOW = 35682,
    SAMPLER_2D_ARRAY = 36289,
    SAMPLER_2D_ARRAY_SHADOW = 36292,
    SAMPLER_CUBE_SHADOW = 36293,
    INT_SAMPLER_2D = 36298,
    INT_SAMPLER_3D = 36299,
    INT_SAMPLER_CUBE = 36300,
    INT_SAMPLER_2D_ARRAY = 36303,
    UNSIGNED_INT_SAMPLER_2D = 36306,
    UNSIGNED_INT_SAMPLER_3D = 36307,
    UNSIGNED_INT_SAMPLER_CUBE = 36308,
    UNSIGNED_INT_SAMPLER_2D_ARRAY = 36311,
    MAX_SAMPLES = 36183,
    SAMPLER_BINDING = 35097,
    PIXEL_PACK_BUFFER = 35051,
    PIXEL_UNPACK_BUFFER = 35052,
    PIXEL_PACK_BUFFER_BINDING = 35053,
    PIXEL_UNPACK_BUFFER_BINDING = 35055,
    COPY_READ_BUFFER = 36662,
    COPY_WRITE_BUFFER = 36663,
    COPY_READ_BUFFER_BINDING = 36662,
    COPY_WRITE_BUFFER_BINDING = 36663,
    FLOAT_MAT2x3 = 35685,
    FLOAT_MAT2x4 = 35686,
    FLOAT_MAT3x2 = 35687,
    FLOAT_MAT3x4 = 35688,
    FLOAT_MAT4x2 = 35689,
    FLOAT_MAT4x3 = 35690,
    UNSIGNED_INT_VEC2 = 36294,
    UNSIGNED_INT_VEC3 = 36295,
    UNSIGNED_INT_VEC4 = 36296,
    UNSIGNED_NORMALIZED = 35863,
    SIGNED_NORMALIZED = 36764,
    VERTEX_ATTRIB_ARRAY_INTEGER = 35069,
    VERTEX_ATTRIB_ARRAY_DIVISOR = 35070,
    TRANSFORM_FEEDBACK_BUFFER_MODE = 35967,
    MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS = 35968,
    TRANSFORM_FEEDBACK_VARYINGS = 35971,
    TRANSFORM_FEEDBACK_BUFFER_START = 35972,
    TRANSFORM_FEEDBACK_BUFFER_SIZE = 35973,
    TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN = 35976,
    MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS = 35978,
    MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS = 35979,
    INTERLEAVED_ATTRIBS = 35980,
    SEPARATE_ATTRIBS = 35981,
    TRANSFORM_FEEDBACK_BUFFER = 35982,
    TRANSFORM_FEEDBACK_BUFFER_BINDING = 35983,
    TRANSFORM_FEEDBACK = 36386,
    TRANSFORM_FEEDBACK_PAUSED = 36387,
    TRANSFORM_FEEDBACK_ACTIVE = 36388,
    TRANSFORM_FEEDBACK_BINDING = 36389,
    FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING = 33296,
    FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE = 33297,
    FRAMEBUFFER_ATTACHMENT_RED_SIZE = 33298,
    FRAMEBUFFER_ATTACHMENT_GREEN_SIZE = 33299,
    FRAMEBUFFER_ATTACHMENT_BLUE_SIZE = 33300,
    FRAMEBUFFER_ATTACHMENT_ALPHA_SIZE = 33301,
    FRAMEBUFFER_ATTACHMENT_DEPTH_SIZE = 33302,
    FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE = 33303,
    FRAMEBUFFER_DEFAULT = 33304,
    DEPTH24_STENCIL8 = 35056,
    DRAW_FRAMEBUFFER_BINDING = 36006,
    READ_FRAMEBUFFER_BINDING = 36010,
    RENDERBUFFER_SAMPLES = 36011,
    FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER = 36052,
    FRAMEBUFFER_INCOMPLETE_MULTISAMPLE = 36182,
    UNIFORM_BUFFER = 35345,
    UNIFORM_BUFFER_BINDING = 35368,
    UNIFORM_BUFFER_START = 35369,
    UNIFORM_BUFFER_SIZE = 35370,
    MAX_VERTEX_UNIFORM_BLOCKS = 35371,
    MAX_FRAGMENT_UNIFORM_BLOCKS = 35373,
    MAX_COMBINED_UNIFORM_BLOCKS = 35374,
    MAX_UNIFORM_BUFFER_BINDINGS = 35375,
    MAX_UNIFORM_BLOCK_SIZE = 35376,
    MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS = 35377,
    MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS = 35379,
    UNIFORM_BUFFER_OFFSET_ALIGNMENT = 35380,
    ACTIVE_UNIFORM_BLOCKS = 35382,
    UNIFORM_TYPE = 35383,
    UNIFORM_SIZE = 35384,
    UNIFORM_BLOCK_INDEX = 35386,
    UNIFORM_OFFSET = 35387,
    UNIFORM_ARRAY_STRIDE = 35388,
    UNIFORM_MATRIX_STRIDE = 35389,
    UNIFORM_IS_ROW_MAJOR = 35390,
    UNIFORM_BLOCK_BINDING = 35391,
    UNIFORM_BLOCK_DATA_SIZE = 35392,
    UNIFORM_BLOCK_ACTIVE_UNIFORMS = 35394,
    UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES = 35395,
    UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER = 35396,
    UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER = 35398,
    OBJECT_TYPE = 37138,
    SYNC_CONDITION = 37139,
    SYNC_STATUS = 37140,
    SYNC_FLAGS = 37141,
    SYNC_FENCE = 37142,
    SYNC_GPU_COMMANDS_COMPLETE = 37143,
    UNSIGNALED = 37144,
    SIGNALED = 37145,
    ALREADY_SIGNALED = 37146,
    TIMEOUT_EXPIRED = 37147,
    CONDITION_SATISFIED = 37148,
    WAIT_FAILED = 37149,
    SYNC_FLUSH_COMMANDS_BIT = 1,
    COLOR = 6144,
    DEPTH = 6145,
    STENCIL = 6146,
    MIN = 32775,
    MAX = 32776,
    DEPTH_COMPONENT24 = 33190,
    STREAM_READ = 35041,
    STREAM_COPY = 35042,
    STATIC_READ = 35045,
    STATIC_COPY = 35046,
    DYNAMIC_READ = 35049,
    DYNAMIC_COPY = 35050,
    DEPTH_COMPONENT32F = 36012,
    DEPTH32F_STENCIL8 = 36013,
    INVALID_INDEX = 4294967295,
    TIMEOUT_IGNORED = -1,
    MAX_CLIENT_WAIT_TIMEOUT_WEBGL = 37447,
    /** Passed to getParameter to get the vendor string of the graphics driver. */
    UNMASKED_VENDOR_WEBGL = 37445,
    /** Passed to getParameter to get the renderer string of the graphics driver. */
    UNMASKED_RENDERER_WEBGL = 37446,
    /** Returns the maximum available anisotropy. */
    MAX_TEXTURE_MAX_ANISOTROPY_EXT = 34047,
    /** Passed to texParameter to set the desired maximum anisotropy for a texture. */
    TEXTURE_MAX_ANISOTROPY_EXT = 34046,
    R16_EXT = 33322,
    RG16_EXT = 33324,
    RGB16_EXT = 32852,
    RGBA16_EXT = 32859,
    R16_SNORM_EXT = 36760,
    RG16_SNORM_EXT = 36761,
    RGB16_SNORM_EXT = 36762,
    RGBA16_SNORM_EXT = 36763,
    /** A DXT1-compressed image in an RGB image format. */
    COMPRESSED_RGB_S3TC_DXT1_EXT = 33776,
    /** A DXT1-compressed image in an RGB image format with a simple on/off alpha value. */
    COMPRESSED_RGBA_S3TC_DXT1_EXT = 33777,
    /** A DXT3-compressed image in an RGBA image format. Compared to a 32-bit RGBA texture, it offers 4:1 compression. */
    COMPRESSED_RGBA_S3TC_DXT3_EXT = 33778,
    /** A DXT5-compressed image in an RGBA image format. It also provides a 4:1 compression, but differs to the DXT3 compression in how the alpha compression is done. */
    COMPRESSED_RGBA_S3TC_DXT5_EXT = 33779,
    COMPRESSED_SRGB_S3TC_DXT1_EXT = 35916,
    COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT = 35917,
    COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT = 35918,
    COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT = 35919,
    COMPRESSED_RED_RGTC1_EXT = 36283,
    COMPRESSED_SIGNED_RED_RGTC1_EXT = 36284,
    COMPRESSED_RED_GREEN_RGTC2_EXT = 36285,
    COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT = 36286,
    COMPRESSED_RGBA_BPTC_UNORM_EXT = 36492,
    COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT = 36493,
    COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT = 36494,
    COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT = 36495,
    /** One-channel (red) unsigned format compression. */
    COMPRESSED_R11_EAC = 37488,
    /** One-channel (red) signed format compression. */
    COMPRESSED_SIGNED_R11_EAC = 37489,
    /** Two-channel (red and green) unsigned format compression. */
    COMPRESSED_RG11_EAC = 37490,
    /** Two-channel (red and green) signed format compression. */
    COMPRESSED_SIGNED_RG11_EAC = 37491,
    /** Compresses RGB8 data with no alpha channel. */
    COMPRESSED_RGB8_ETC2 = 37492,
    /** Compresses RGBA8 data. The RGB part is encoded the same as RGB_ETC2, but the alpha part is encoded separately. */
    COMPRESSED_RGBA8_ETC2_EAC = 37493,
    /** Compresses sRGB8 data with no alpha channel. */
    COMPRESSED_SRGB8_ETC2 = 37494,
    /** Compresses sRGBA8 data. The sRGB part is encoded the same as SRGB_ETC2, but the alpha part is encoded separately. */
    COMPRESSED_SRGB8_ALPHA8_ETC2_EAC = 37495,
    /** Similar to RGB8_ETC, but with ability to punch through the alpha channel, which means to make it completely opaque or transparent. */
    COMPRESSED_RGB8_PUNCHTHROUGH_ALPHA1_ETC2 = 37496,
    /** Similar to SRGB8_ETC, but with ability to punch through the alpha channel, which means to make it completely opaque or transparent. */
    COMPRESSED_SRGB8_PUNCHTHROUGH_ALPHA1_ETC2 = 37497,
    /** RGB compression in 4-bit mode. One block for each 4×4 pixels. */
    COMPRESSED_RGB_PVRTC_4BPPV1_IMG = 35840,
    /** RGBA compression in 4-bit mode. One block for each 4×4 pixels. */
    COMPRESSED_RGBA_PVRTC_4BPPV1_IMG = 35842,
    /** RGB compression in 2-bit mode. One block for each 8×4 pixels. */
    COMPRESSED_RGB_PVRTC_2BPPV1_IMG = 35841,
    /** RGBA compression in 2-bit mode. One block for each 8×4 pixels. */
    COMPRESSED_RGBA_PVRTC_2BPPV1_IMG = 35843,
    /** Compresses 24-bit RGB data with no alpha channel. */
    COMPRESSED_RGB_ETC1_WEBGL = 36196,
    COMPRESSED_RGB_ATC_WEBGL = 35986,
    COMPRESSED_RGBA_ATC_EXPLICIT_ALPHA_WEBGL = 35986,
    COMPRESSED_RGBA_ATC_INTERPOLATED_ALPHA_WEBGL = 34798,
    COMPRESSED_RGBA_ASTC_4x4_KHR = 37808,
    COMPRESSED_RGBA_ASTC_5x4_KHR = 37809,
    COMPRESSED_RGBA_ASTC_5x5_KHR = 37810,
    COMPRESSED_RGBA_ASTC_6x5_KHR = 37811,
    COMPRESSED_RGBA_ASTC_6x6_KHR = 37812,
    COMPRESSED_RGBA_ASTC_8x5_KHR = 37813,
    COMPRESSED_RGBA_ASTC_8x6_KHR = 37814,
    COMPRESSED_RGBA_ASTC_8x8_KHR = 37815,
    COMPRESSED_RGBA_ASTC_10x5_KHR = 37816,
    COMPRESSED_RGBA_ASTC_10x6_KHR = 37817,
    COMPRESSED_RGBA_ASTC_10x8_KHR = 37818,
    COMPRESSED_RGBA_ASTC_10x10_KHR = 37819,
    COMPRESSED_RGBA_ASTC_12x10_KHR = 37820,
    COMPRESSED_RGBA_ASTC_12x12_KHR = 37821,
    COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR = 37840,
    COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR = 37841,
    COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR = 37842,
    COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR = 37843,
    COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR = 37844,
    COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR = 37845,
    COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR = 37846,
    COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR = 37847,
    COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR = 37848,
    COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR = 37849,
    COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR = 37850,
    COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR = 37851,
    COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR = 37852,
    COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR = 37853,
    /** The number of bits used to hold the query result for the given target. */
    QUERY_COUNTER_BITS_EXT = 34916,
    /** The currently active query. */
    CURRENT_QUERY_EXT = 34917,
    /** The query result. */
    QUERY_RESULT_EXT = 34918,
    /** A Boolean indicating whether or not a query result is available. */
    QUERY_RESULT_AVAILABLE_EXT = 34919,
    /** Elapsed time (in nanoseconds). */
    TIME_ELAPSED_EXT = 35007,
    /** The current time. */
    TIMESTAMP_EXT = 36392,
    /** A Boolean indicating whether or not the GPU performed any disjoint operation (lost context) */
    GPU_DISJOINT_EXT = 36795,
    /** a non-blocking poll operation, so that compile/link status availability can be queried without potentially incurring stalls */
    COMPLETION_STATUS_KHR = 37297,
    /** Disables depth clipping */
    DEPTH_CLAMP_EXT = 34383,
    /** Values of first vertex in primitive are used for flat shading */
    FIRST_VERTEX_CONVENTION_WEBGL = 36429,
    /** Values of first vertex in primitive are used for flat shading */
    LAST_VERTEX_CONVENTION_WEBGL = 36430,// default
    /** Controls which vertex in primitive is used for flat shading */
    PROVOKING_VERTEX_WEBL = 36431,
    POLYGON_MODE_WEBGL = 2880,
    POLYGON_OFFSET_LINE_WEBGL = 10754,
    LINE_WEBGL = 6913,
    FILL_WEBGL = 6914,
    /** Max clip distances */
    MAX_CLIP_DISTANCES_WEBGL = 3378,
    /** Max cull distances */
    MAX_CULL_DISTANCES_WEBGL = 33529,
    /** Max clip and cull distances */
    MAX_COMBINED_CLIP_AND_CULL_DISTANCES_WEBGL = 33530,
    /** Enable gl_ClipDistance[0] and gl_CullDistance[0] */
    CLIP_DISTANCE0_WEBGL = 12288,
    /** Enable gl_ClipDistance[1] and gl_CullDistance[1] */
    CLIP_DISTANCE1_WEBGL = 12289,
    /** Enable gl_ClipDistance[2] and gl_CullDistance[2] */
    CLIP_DISTANCE2_WEBGL = 12290,
    /** Enable gl_ClipDistance[3] and gl_CullDistance[3] */
    CLIP_DISTANCE3_WEBGL = 12291,
    /** Enable gl_ClipDistance[4] and gl_CullDistance[4] */
    CLIP_DISTANCE4_WEBGL = 12292,
    /** Enable gl_ClipDistance[5] and gl_CullDistance[5] */
    CLIP_DISTANCE5_WEBGL = 12293,
    /** Enable gl_ClipDistance[6] and gl_CullDistance[6] */
    CLIP_DISTANCE6_WEBGL = 12294,
    /** Enable gl_ClipDistance[7] and gl_CullDistance[7] */
    CLIP_DISTANCE7_WEBGL = 12295,
    /** EXT_polygon_offset_clamp https://registry.khronos.org/webgl/extensions/EXT_polygon_offset_clamp/ */
    POLYGON_OFFSET_CLAMP_EXT = 36379,
    /** EXT_clip_control https://registry.khronos.org/webgl/extensions/EXT_clip_control/ */
    LOWER_LEFT_EXT = 36001,
    UPPER_LEFT_EXT = 36002,
    NEGATIVE_ONE_TO_ONE_EXT = 37726,
    ZERO_TO_ONE_EXT = 37727,
    CLIP_ORIGIN_EXT = 37724,
    CLIP_DEPTH_MODE_EXT = 37725,
    /** WEBGL_blend_func_extended https://registry.khronos.org/webgl/extensions/WEBGL_blend_func_extended/ */
    SRC1_COLOR_WEBGL = 35065,
    SRC1_ALPHA_WEBGL = 34185,
    ONE_MINUS_SRC1_COLOR_WEBGL = 35066,
    ONE_MINUS_SRC1_ALPHA_WEBGL = 35067,
    MAX_DUAL_SOURCE_DRAW_BUFFERS_WEBGL = 35068,
    /** EXT_texture_mirror_clamp_to_edge https://registry.khronos.org/webgl/extensions/EXT_texture_mirror_clamp_to_edge/ */
    MIRROR_CLAMP_TO_EDGE_EXT = 34627
}
export { GLEnum as GL };
//# sourceMappingURL=lumagl.d.ts.map