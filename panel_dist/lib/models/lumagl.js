// luma.gl
// SPDX-License-Identifier: MIT
// Copyright (c) vis.gl contributors
/* eslint-disable key-spacing, max-len, no-inline-comments, camelcase */
/**
 * Standard WebGL, WebGL2 and extension constants (OpenGL constants)
 * @note (Most) of these constants are also defined on the WebGLRenderingContext interface.
 * @see https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/Constants
 * @privateRemarks Locally called `GLEnum` instead of `GL`, because `babel-plugin-inline-webl-constants`
 *  both depends on and processes this module, but shouldn't replace these declarations.
 */
var GLEnum;
(function (GLEnum) {
    // Clearing buffers
    // Constants passed to clear() to clear buffer masks.
    /** Passed to clear to clear the current depth buffer. */
    GLEnum[GLEnum["DEPTH_BUFFER_BIT"] = 256] = "DEPTH_BUFFER_BIT";
    /** Passed to clear to clear the current stencil buffer. */
    GLEnum[GLEnum["STENCIL_BUFFER_BIT"] = 1024] = "STENCIL_BUFFER_BIT";
    /** Passed to clear to clear the current color buffer. */
    GLEnum[GLEnum["COLOR_BUFFER_BIT"] = 16384] = "COLOR_BUFFER_BIT";
    // Rendering primitives
    // Constants passed to drawElements() or drawArrays() to specify what kind of primitive to render.
    /** Passed to drawElements or drawArrays to draw single points. */
    GLEnum[GLEnum["POINTS"] = 0] = "POINTS";
    /** Passed to drawElements or drawArrays to draw lines. Each vertex connects to the one after it. */
    GLEnum[GLEnum["LINES"] = 1] = "LINES";
    /** Passed to drawElements or drawArrays to draw lines. Each set of two vertices is treated as a separate line segment. */
    GLEnum[GLEnum["LINE_LOOP"] = 2] = "LINE_LOOP";
    /** Passed to drawElements or drawArrays to draw a connected group of line segments from the first vertex to the last. */
    GLEnum[GLEnum["LINE_STRIP"] = 3] = "LINE_STRIP";
    /** Passed to drawElements or drawArrays to draw triangles. Each set of three vertices creates a separate triangle. */
    GLEnum[GLEnum["TRIANGLES"] = 4] = "TRIANGLES";
    /** Passed to drawElements or drawArrays to draw a connected group of triangles. */
    GLEnum[GLEnum["TRIANGLE_STRIP"] = 5] = "TRIANGLE_STRIP";
    /** Passed to drawElements or drawArrays to draw a connected group of triangles. Each vertex connects to the previous and the first vertex in the fan. */
    GLEnum[GLEnum["TRIANGLE_FAN"] = 6] = "TRIANGLE_FAN";
    // Blending modes
    // Constants passed to blendFunc() or blendFuncSeparate() to specify the blending mode (for both, RBG and alpha, or separately).
    /** Passed to blendFunc or blendFuncSeparate to turn off a component. */
    GLEnum[GLEnum["ZERO"] = 0] = "ZERO";
    /** Passed to blendFunc or blendFuncSeparate to turn on a component. */
    GLEnum[GLEnum["ONE"] = 1] = "ONE";
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the source elements color. */
    GLEnum[GLEnum["SRC_COLOR"] = 768] = "SRC_COLOR";
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by one minus the source elements color. */
    GLEnum[GLEnum["ONE_MINUS_SRC_COLOR"] = 769] = "ONE_MINUS_SRC_COLOR";
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the source's alpha. */
    GLEnum[GLEnum["SRC_ALPHA"] = 770] = "SRC_ALPHA";
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by one minus the source's alpha. */
    GLEnum[GLEnum["ONE_MINUS_SRC_ALPHA"] = 771] = "ONE_MINUS_SRC_ALPHA";
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the destination's alpha. */
    GLEnum[GLEnum["DST_ALPHA"] = 772] = "DST_ALPHA";
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by one minus the destination's alpha. */
    GLEnum[GLEnum["ONE_MINUS_DST_ALPHA"] = 773] = "ONE_MINUS_DST_ALPHA";
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the destination's color. */
    GLEnum[GLEnum["DST_COLOR"] = 774] = "DST_COLOR";
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by one minus the destination's color. */
    GLEnum[GLEnum["ONE_MINUS_DST_COLOR"] = 775] = "ONE_MINUS_DST_COLOR";
    /** Passed to blendFunc or blendFuncSeparate to multiply a component by the minimum of source's alpha or one minus the destination's alpha. */
    GLEnum[GLEnum["SRC_ALPHA_SATURATE"] = 776] = "SRC_ALPHA_SATURATE";
    /** Passed to blendFunc or blendFuncSeparate to specify a constant color blend function. */
    GLEnum[GLEnum["CONSTANT_COLOR"] = 32769] = "CONSTANT_COLOR";
    /** Passed to blendFunc or blendFuncSeparate to specify one minus a constant color blend function. */
    GLEnum[GLEnum["ONE_MINUS_CONSTANT_COLOR"] = 32770] = "ONE_MINUS_CONSTANT_COLOR";
    /** Passed to blendFunc or blendFuncSeparate to specify a constant alpha blend function. */
    GLEnum[GLEnum["CONSTANT_ALPHA"] = 32771] = "CONSTANT_ALPHA";
    /** Passed to blendFunc or blendFuncSeparate to specify one minus a constant alpha blend function. */
    GLEnum[GLEnum["ONE_MINUS_CONSTANT_ALPHA"] = 32772] = "ONE_MINUS_CONSTANT_ALPHA";
    // Blending equations
    // Constants passed to blendEquation() or blendEquationSeparate() to control
    // how the blending is calculated (for both, RBG and alpha, or separately).
    /** Passed to blendEquation or blendEquationSeparate to set an addition blend function. */
    /** Passed to blendEquation or blendEquationSeparate to specify a subtraction blend function (source - destination). */
    /** Passed to blendEquation or blendEquationSeparate to specify a reverse subtraction blend function (destination - source). */
    GLEnum[GLEnum["FUNC_ADD"] = 32774] = "FUNC_ADD";
    GLEnum[GLEnum["FUNC_SUBTRACT"] = 32778] = "FUNC_SUBTRACT";
    GLEnum[GLEnum["FUNC_REVERSE_SUBTRACT"] = 32779] = "FUNC_REVERSE_SUBTRACT";
    // Getting GL parameter information
    // Constants passed to getParameter() to specify what information to return.
    /** Passed to getParameter to get the current RGB blend function. */
    GLEnum[GLEnum["BLEND_EQUATION"] = 32777] = "BLEND_EQUATION";
    /** Passed to getParameter to get the current RGB blend function. Same as BLEND_EQUATION */
    GLEnum[GLEnum["BLEND_EQUATION_RGB"] = 32777] = "BLEND_EQUATION_RGB";
    /** Passed to getParameter to get the current alpha blend function. Same as BLEND_EQUATION */
    GLEnum[GLEnum["BLEND_EQUATION_ALPHA"] = 34877] = "BLEND_EQUATION_ALPHA";
    /** Passed to getParameter to get the current destination RGB blend function. */
    GLEnum[GLEnum["BLEND_DST_RGB"] = 32968] = "BLEND_DST_RGB";
    /** Passed to getParameter to get the current destination RGB blend function. */
    GLEnum[GLEnum["BLEND_SRC_RGB"] = 32969] = "BLEND_SRC_RGB";
    /** Passed to getParameter to get the current destination alpha blend function. */
    GLEnum[GLEnum["BLEND_DST_ALPHA"] = 32970] = "BLEND_DST_ALPHA";
    /** Passed to getParameter to get the current source alpha blend function. */
    GLEnum[GLEnum["BLEND_SRC_ALPHA"] = 32971] = "BLEND_SRC_ALPHA";
    /** Passed to getParameter to return a the current blend color. */
    GLEnum[GLEnum["BLEND_COLOR"] = 32773] = "BLEND_COLOR";
    /** Passed to getParameter to get the array buffer binding. */
    GLEnum[GLEnum["ARRAY_BUFFER_BINDING"] = 34964] = "ARRAY_BUFFER_BINDING";
    /** Passed to getParameter to get the current element array buffer. */
    GLEnum[GLEnum["ELEMENT_ARRAY_BUFFER_BINDING"] = 34965] = "ELEMENT_ARRAY_BUFFER_BINDING";
    /** Passed to getParameter to get the current lineWidth (set by the lineWidth method). */
    GLEnum[GLEnum["LINE_WIDTH"] = 2849] = "LINE_WIDTH";
    /** Passed to getParameter to get the current size of a point drawn with gl.POINTS */
    GLEnum[GLEnum["ALIASED_POINT_SIZE_RANGE"] = 33901] = "ALIASED_POINT_SIZE_RANGE";
    /** Passed to getParameter to get the range of available widths for a line. Returns a length-2 array with the lo value at 0, and high at 1. */
    GLEnum[GLEnum["ALIASED_LINE_WIDTH_RANGE"] = 33902] = "ALIASED_LINE_WIDTH_RANGE";
    /** Passed to getParameter to get the current value of cullFace. Should return FRONT, BACK, or FRONT_AND_BACK */
    GLEnum[GLEnum["CULL_FACE_MODE"] = 2885] = "CULL_FACE_MODE";
    /** Passed to getParameter to determine the current value of frontFace. Should return CW or CCW. */
    GLEnum[GLEnum["FRONT_FACE"] = 2886] = "FRONT_FACE";
    /** Passed to getParameter to return a length-2 array of floats giving the current depth range. */
    GLEnum[GLEnum["DEPTH_RANGE"] = 2928] = "DEPTH_RANGE";
    /** Passed to getParameter to determine if the depth write mask is enabled. */
    GLEnum[GLEnum["DEPTH_WRITEMASK"] = 2930] = "DEPTH_WRITEMASK";
    /** Passed to getParameter to determine the current depth clear value. */
    GLEnum[GLEnum["DEPTH_CLEAR_VALUE"] = 2931] = "DEPTH_CLEAR_VALUE";
    /** Passed to getParameter to get the current depth function. Returns NEVER, ALWAYS, LESS, EQUAL, LEQUAL, GREATER, GEQUAL, or NOTEQUAL. */
    GLEnum[GLEnum["DEPTH_FUNC"] = 2932] = "DEPTH_FUNC";
    /** Passed to getParameter to get the value the stencil will be cleared to. */
    GLEnum[GLEnum["STENCIL_CLEAR_VALUE"] = 2961] = "STENCIL_CLEAR_VALUE";
    /** Passed to getParameter to get the current stencil function. Returns NEVER, ALWAYS, LESS, EQUAL, LEQUAL, GREATER, GEQUAL, or NOTEQUAL. */
    GLEnum[GLEnum["STENCIL_FUNC"] = 2962] = "STENCIL_FUNC";
    /** Passed to getParameter to get the current stencil fail function. Should return KEEP, REPLACE, INCR, DECR, INVERT, INCR_WRAP, or DECR_WRAP. */
    GLEnum[GLEnum["STENCIL_FAIL"] = 2964] = "STENCIL_FAIL";
    /** Passed to getParameter to get the current stencil fail function should the depth buffer test fail. Should return KEEP, REPLACE, INCR, DECR, INVERT, INCR_WRAP, or DECR_WRAP. */
    GLEnum[GLEnum["STENCIL_PASS_DEPTH_FAIL"] = 2965] = "STENCIL_PASS_DEPTH_FAIL";
    /** Passed to getParameter to get the current stencil fail function should the depth buffer test pass. Should return KEEP, REPLACE, INCR, DECR, INVERT, INCR_WRAP, or DECR_WRAP. */
    GLEnum[GLEnum["STENCIL_PASS_DEPTH_PASS"] = 2966] = "STENCIL_PASS_DEPTH_PASS";
    /** Passed to getParameter to get the reference value used for stencil tests. */
    GLEnum[GLEnum["STENCIL_REF"] = 2967] = "STENCIL_REF";
    GLEnum[GLEnum["STENCIL_VALUE_MASK"] = 2963] = "STENCIL_VALUE_MASK";
    GLEnum[GLEnum["STENCIL_WRITEMASK"] = 2968] = "STENCIL_WRITEMASK";
    GLEnum[GLEnum["STENCIL_BACK_FUNC"] = 34816] = "STENCIL_BACK_FUNC";
    GLEnum[GLEnum["STENCIL_BACK_FAIL"] = 34817] = "STENCIL_BACK_FAIL";
    GLEnum[GLEnum["STENCIL_BACK_PASS_DEPTH_FAIL"] = 34818] = "STENCIL_BACK_PASS_DEPTH_FAIL";
    GLEnum[GLEnum["STENCIL_BACK_PASS_DEPTH_PASS"] = 34819] = "STENCIL_BACK_PASS_DEPTH_PASS";
    GLEnum[GLEnum["STENCIL_BACK_REF"] = 36003] = "STENCIL_BACK_REF";
    GLEnum[GLEnum["STENCIL_BACK_VALUE_MASK"] = 36004] = "STENCIL_BACK_VALUE_MASK";
    GLEnum[GLEnum["STENCIL_BACK_WRITEMASK"] = 36005] = "STENCIL_BACK_WRITEMASK";
    /** An Int32Array with four elements for the current viewport dimensions. */
    GLEnum[GLEnum["VIEWPORT"] = 2978] = "VIEWPORT";
    /** An Int32Array with four elements for the current scissor box dimensions. */
    GLEnum[GLEnum["SCISSOR_BOX"] = 3088] = "SCISSOR_BOX";
    GLEnum[GLEnum["COLOR_CLEAR_VALUE"] = 3106] = "COLOR_CLEAR_VALUE";
    GLEnum[GLEnum["COLOR_WRITEMASK"] = 3107] = "COLOR_WRITEMASK";
    GLEnum[GLEnum["UNPACK_ALIGNMENT"] = 3317] = "UNPACK_ALIGNMENT";
    GLEnum[GLEnum["PACK_ALIGNMENT"] = 3333] = "PACK_ALIGNMENT";
    GLEnum[GLEnum["MAX_TEXTURE_SIZE"] = 3379] = "MAX_TEXTURE_SIZE";
    GLEnum[GLEnum["MAX_VIEWPORT_DIMS"] = 3386] = "MAX_VIEWPORT_DIMS";
    GLEnum[GLEnum["SUBPIXEL_BITS"] = 3408] = "SUBPIXEL_BITS";
    GLEnum[GLEnum["RED_BITS"] = 3410] = "RED_BITS";
    GLEnum[GLEnum["GREEN_BITS"] = 3411] = "GREEN_BITS";
    GLEnum[GLEnum["BLUE_BITS"] = 3412] = "BLUE_BITS";
    GLEnum[GLEnum["ALPHA_BITS"] = 3413] = "ALPHA_BITS";
    GLEnum[GLEnum["DEPTH_BITS"] = 3414] = "DEPTH_BITS";
    GLEnum[GLEnum["STENCIL_BITS"] = 3415] = "STENCIL_BITS";
    GLEnum[GLEnum["POLYGON_OFFSET_UNITS"] = 10752] = "POLYGON_OFFSET_UNITS";
    GLEnum[GLEnum["POLYGON_OFFSET_FACTOR"] = 32824] = "POLYGON_OFFSET_FACTOR";
    GLEnum[GLEnum["TEXTURE_BINDING_2D"] = 32873] = "TEXTURE_BINDING_2D";
    GLEnum[GLEnum["SAMPLE_BUFFERS"] = 32936] = "SAMPLE_BUFFERS";
    GLEnum[GLEnum["SAMPLES"] = 32937] = "SAMPLES";
    GLEnum[GLEnum["SAMPLE_COVERAGE_VALUE"] = 32938] = "SAMPLE_COVERAGE_VALUE";
    GLEnum[GLEnum["SAMPLE_COVERAGE_INVERT"] = 32939] = "SAMPLE_COVERAGE_INVERT";
    GLEnum[GLEnum["COMPRESSED_TEXTURE_FORMATS"] = 34467] = "COMPRESSED_TEXTURE_FORMATS";
    GLEnum[GLEnum["VENDOR"] = 7936] = "VENDOR";
    GLEnum[GLEnum["RENDERER"] = 7937] = "RENDERER";
    GLEnum[GLEnum["VERSION"] = 7938] = "VERSION";
    GLEnum[GLEnum["IMPLEMENTATION_COLOR_READ_TYPE"] = 35738] = "IMPLEMENTATION_COLOR_READ_TYPE";
    GLEnum[GLEnum["IMPLEMENTATION_COLOR_READ_FORMAT"] = 35739] = "IMPLEMENTATION_COLOR_READ_FORMAT";
    GLEnum[GLEnum["BROWSER_DEFAULT_WEBGL"] = 37444] = "BROWSER_DEFAULT_WEBGL";
    // Buffers
    // Constants passed to bufferData(), bufferSubData(), bindBuffer(), or
    // getBufferParameter().
    /** Passed to bufferData as a hint about whether the contents of the buffer are likely to be used often and not change often. */
    GLEnum[GLEnum["STATIC_DRAW"] = 35044] = "STATIC_DRAW";
    /** Passed to bufferData as a hint about whether the contents of the buffer are likely to not be used often. */
    GLEnum[GLEnum["STREAM_DRAW"] = 35040] = "STREAM_DRAW";
    /** Passed to bufferData as a hint about whether the contents of the buffer are likely to be used often and change often. */
    GLEnum[GLEnum["DYNAMIC_DRAW"] = 35048] = "DYNAMIC_DRAW";
    /** Passed to bindBuffer or bufferData to specify the type of buffer being used. */
    GLEnum[GLEnum["ARRAY_BUFFER"] = 34962] = "ARRAY_BUFFER";
    /** Passed to bindBuffer or bufferData to specify the type of buffer being used. */
    GLEnum[GLEnum["ELEMENT_ARRAY_BUFFER"] = 34963] = "ELEMENT_ARRAY_BUFFER";
    /** Passed to getBufferParameter to get a buffer's size. */
    GLEnum[GLEnum["BUFFER_SIZE"] = 34660] = "BUFFER_SIZE";
    /** Passed to getBufferParameter to get the hint for the buffer passed in when it was created. */
    GLEnum[GLEnum["BUFFER_USAGE"] = 34661] = "BUFFER_USAGE";
    // Vertex attributes
    // Constants passed to getVertexAttrib().
    /** Passed to getVertexAttrib to read back the current vertex attribute. */
    GLEnum[GLEnum["CURRENT_VERTEX_ATTRIB"] = 34342] = "CURRENT_VERTEX_ATTRIB";
    GLEnum[GLEnum["VERTEX_ATTRIB_ARRAY_ENABLED"] = 34338] = "VERTEX_ATTRIB_ARRAY_ENABLED";
    GLEnum[GLEnum["VERTEX_ATTRIB_ARRAY_SIZE"] = 34339] = "VERTEX_ATTRIB_ARRAY_SIZE";
    GLEnum[GLEnum["VERTEX_ATTRIB_ARRAY_STRIDE"] = 34340] = "VERTEX_ATTRIB_ARRAY_STRIDE";
    GLEnum[GLEnum["VERTEX_ATTRIB_ARRAY_TYPE"] = 34341] = "VERTEX_ATTRIB_ARRAY_TYPE";
    GLEnum[GLEnum["VERTEX_ATTRIB_ARRAY_NORMALIZED"] = 34922] = "VERTEX_ATTRIB_ARRAY_NORMALIZED";
    GLEnum[GLEnum["VERTEX_ATTRIB_ARRAY_POINTER"] = 34373] = "VERTEX_ATTRIB_ARRAY_POINTER";
    GLEnum[GLEnum["VERTEX_ATTRIB_ARRAY_BUFFER_BINDING"] = 34975] = "VERTEX_ATTRIB_ARRAY_BUFFER_BINDING";
    // Culling
    // Constants passed to cullFace().
    /** Passed to enable/disable to turn on/off culling. Can also be used with getParameter to find the current culling method. */
    GLEnum[GLEnum["CULL_FACE"] = 2884] = "CULL_FACE";
    /** Passed to cullFace to specify that only front faces should be culled. */
    GLEnum[GLEnum["FRONT"] = 1028] = "FRONT";
    /** Passed to cullFace to specify that only back faces should be culled. */
    GLEnum[GLEnum["BACK"] = 1029] = "BACK";
    /** Passed to cullFace to specify that front and back faces should be culled. */
    GLEnum[GLEnum["FRONT_AND_BACK"] = 1032] = "FRONT_AND_BACK";
    // Enabling and disabling
    // Constants passed to enable() or disable().
    /** Passed to enable/disable to turn on/off blending. Can also be used with getParameter to find the current blending method. */
    GLEnum[GLEnum["BLEND"] = 3042] = "BLEND";
    /** Passed to enable/disable to turn on/off the depth test. Can also be used with getParameter to query the depth test. */
    GLEnum[GLEnum["DEPTH_TEST"] = 2929] = "DEPTH_TEST";
    /** Passed to enable/disable to turn on/off dithering. Can also be used with getParameter to find the current dithering method. */
    GLEnum[GLEnum["DITHER"] = 3024] = "DITHER";
    /** Passed to enable/disable to turn on/off the polygon offset. Useful for rendering hidden-line images, decals, and or solids with highlighted edges. Can also be used with getParameter to query the scissor test. */
    GLEnum[GLEnum["POLYGON_OFFSET_FILL"] = 32823] = "POLYGON_OFFSET_FILL";
    /** Passed to enable/disable to turn on/off the alpha to coverage. Used in multi-sampling alpha channels. */
    GLEnum[GLEnum["SAMPLE_ALPHA_TO_COVERAGE"] = 32926] = "SAMPLE_ALPHA_TO_COVERAGE";
    /** Passed to enable/disable to turn on/off the sample coverage. Used in multi-sampling. */
    GLEnum[GLEnum["SAMPLE_COVERAGE"] = 32928] = "SAMPLE_COVERAGE";
    /** Passed to enable/disable to turn on/off the scissor test. Can also be used with getParameter to query the scissor test. */
    GLEnum[GLEnum["SCISSOR_TEST"] = 3089] = "SCISSOR_TEST";
    /** Passed to enable/disable to turn on/off the stencil test. Can also be used with getParameter to query the stencil test. */
    GLEnum[GLEnum["STENCIL_TEST"] = 2960] = "STENCIL_TEST";
    // Errors
    // Constants returned from getError().
    /** Returned from getError(). */
    GLEnum[GLEnum["NO_ERROR"] = 0] = "NO_ERROR";
    /** Returned from getError(). */
    GLEnum[GLEnum["INVALID_ENUM"] = 1280] = "INVALID_ENUM";
    /** Returned from getError(). */
    GLEnum[GLEnum["INVALID_VALUE"] = 1281] = "INVALID_VALUE";
    /** Returned from getError(). */
    GLEnum[GLEnum["INVALID_OPERATION"] = 1282] = "INVALID_OPERATION";
    /** Returned from getError(). */
    GLEnum[GLEnum["OUT_OF_MEMORY"] = 1285] = "OUT_OF_MEMORY";
    /** Returned from getError(). */
    GLEnum[GLEnum["CONTEXT_LOST_WEBGL"] = 37442] = "CONTEXT_LOST_WEBGL";
    // Front face directions
    // Constants passed to frontFace().
    /** Passed to frontFace to specify the front face of a polygon is drawn in the clockwise direction */
    GLEnum[GLEnum["CW"] = 2304] = "CW";
    /** Passed to frontFace to specify the front face of a polygon is drawn in the counter clockwise direction */
    GLEnum[GLEnum["CCW"] = 2305] = "CCW";
    // Hints
    // Constants passed to hint()
    /** There is no preference for this behavior. */
    GLEnum[GLEnum["DONT_CARE"] = 4352] = "DONT_CARE";
    /** The most efficient behavior should be used. */
    GLEnum[GLEnum["FASTEST"] = 4353] = "FASTEST";
    /** The most correct or the highest quality option should be used. */
    GLEnum[GLEnum["NICEST"] = 4354] = "NICEST";
    /** Hint for the quality of filtering when generating mipmap images with WebGLRenderingContext.generateMipmap(). */
    GLEnum[GLEnum["GENERATE_MIPMAP_HINT"] = 33170] = "GENERATE_MIPMAP_HINT";
    // Data types
    GLEnum[GLEnum["BYTE"] = 5120] = "BYTE";
    GLEnum[GLEnum["UNSIGNED_BYTE"] = 5121] = "UNSIGNED_BYTE";
    GLEnum[GLEnum["SHORT"] = 5122] = "SHORT";
    GLEnum[GLEnum["UNSIGNED_SHORT"] = 5123] = "UNSIGNED_SHORT";
    GLEnum[GLEnum["INT"] = 5124] = "INT";
    GLEnum[GLEnum["UNSIGNED_INT"] = 5125] = "UNSIGNED_INT";
    GLEnum[GLEnum["FLOAT"] = 5126] = "FLOAT";
    GLEnum[GLEnum["DOUBLE"] = 5130] = "DOUBLE";
    // Pixel formats
    GLEnum[GLEnum["DEPTH_COMPONENT"] = 6402] = "DEPTH_COMPONENT";
    GLEnum[GLEnum["ALPHA"] = 6406] = "ALPHA";
    GLEnum[GLEnum["RGB"] = 6407] = "RGB";
    GLEnum[GLEnum["RGBA"] = 6408] = "RGBA";
    GLEnum[GLEnum["LUMINANCE"] = 6409] = "LUMINANCE";
    GLEnum[GLEnum["LUMINANCE_ALPHA"] = 6410] = "LUMINANCE_ALPHA";
    // Pixel types
    // UNSIGNED_BYTE = 0x1401,
    GLEnum[GLEnum["UNSIGNED_SHORT_4_4_4_4"] = 32819] = "UNSIGNED_SHORT_4_4_4_4";
    GLEnum[GLEnum["UNSIGNED_SHORT_5_5_5_1"] = 32820] = "UNSIGNED_SHORT_5_5_5_1";
    GLEnum[GLEnum["UNSIGNED_SHORT_5_6_5"] = 33635] = "UNSIGNED_SHORT_5_6_5";
    // Shaders
    // Constants passed to createShader() or getShaderParameter()
    /** Passed to createShader to define a fragment shader. */
    GLEnum[GLEnum["FRAGMENT_SHADER"] = 35632] = "FRAGMENT_SHADER";
    /** Passed to createShader to define a vertex shader */
    GLEnum[GLEnum["VERTEX_SHADER"] = 35633] = "VERTEX_SHADER";
    /** Passed to getShaderParameter to get the status of the compilation. Returns false if the shader was not compiled. You can then query getShaderInfoLog to find the exact error */
    GLEnum[GLEnum["COMPILE_STATUS"] = 35713] = "COMPILE_STATUS";
    /** Passed to getShaderParameter to determine if a shader was deleted via deleteShader. Returns true if it was, false otherwise. */
    GLEnum[GLEnum["DELETE_STATUS"] = 35712] = "DELETE_STATUS";
    /** Passed to getProgramParameter after calling linkProgram to determine if a program was linked correctly. Returns false if there were errors. Use getProgramInfoLog to find the exact error. */
    GLEnum[GLEnum["LINK_STATUS"] = 35714] = "LINK_STATUS";
    /** Passed to getProgramParameter after calling validateProgram to determine if it is valid. Returns false if errors were found. */
    GLEnum[GLEnum["VALIDATE_STATUS"] = 35715] = "VALIDATE_STATUS";
    /** Passed to getProgramParameter after calling attachShader to determine if the shader was attached correctly. Returns false if errors occurred. */
    GLEnum[GLEnum["ATTACHED_SHADERS"] = 35717] = "ATTACHED_SHADERS";
    /** Passed to getProgramParameter to get the number of attributes active in a program. */
    GLEnum[GLEnum["ACTIVE_ATTRIBUTES"] = 35721] = "ACTIVE_ATTRIBUTES";
    /** Passed to getProgramParameter to get the number of uniforms active in a program. */
    GLEnum[GLEnum["ACTIVE_UNIFORMS"] = 35718] = "ACTIVE_UNIFORMS";
    /** The maximum number of entries possible in the vertex attribute list. */
    GLEnum[GLEnum["MAX_VERTEX_ATTRIBS"] = 34921] = "MAX_VERTEX_ATTRIBS";
    GLEnum[GLEnum["MAX_VERTEX_UNIFORM_VECTORS"] = 36347] = "MAX_VERTEX_UNIFORM_VECTORS";
    GLEnum[GLEnum["MAX_VARYING_VECTORS"] = 36348] = "MAX_VARYING_VECTORS";
    GLEnum[GLEnum["MAX_COMBINED_TEXTURE_IMAGE_UNITS"] = 35661] = "MAX_COMBINED_TEXTURE_IMAGE_UNITS";
    GLEnum[GLEnum["MAX_VERTEX_TEXTURE_IMAGE_UNITS"] = 35660] = "MAX_VERTEX_TEXTURE_IMAGE_UNITS";
    /** Implementation dependent number of maximum texture units. At least 8. */
    GLEnum[GLEnum["MAX_TEXTURE_IMAGE_UNITS"] = 34930] = "MAX_TEXTURE_IMAGE_UNITS";
    GLEnum[GLEnum["MAX_FRAGMENT_UNIFORM_VECTORS"] = 36349] = "MAX_FRAGMENT_UNIFORM_VECTORS";
    GLEnum[GLEnum["SHADER_TYPE"] = 35663] = "SHADER_TYPE";
    GLEnum[GLEnum["SHADING_LANGUAGE_VERSION"] = 35724] = "SHADING_LANGUAGE_VERSION";
    GLEnum[GLEnum["CURRENT_PROGRAM"] = 35725] = "CURRENT_PROGRAM";
    // Depth or stencil tests
    // Constants passed to depthFunc() or stencilFunc().
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will never pass, i.e., nothing will be drawn. */
    GLEnum[GLEnum["NEVER"] = 512] = "NEVER";
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is less than the stored value. */
    GLEnum[GLEnum["LESS"] = 513] = "LESS";
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is equals to the stored value. */
    GLEnum[GLEnum["EQUAL"] = 514] = "EQUAL";
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is less than or equal to the stored value. */
    GLEnum[GLEnum["LEQUAL"] = 515] = "LEQUAL";
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is greater than the stored value. */
    GLEnum[GLEnum["GREATER"] = 516] = "GREATER";
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is not equal to the stored value. */
    GLEnum[GLEnum["NOTEQUAL"] = 517] = "NOTEQUAL";
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will pass if the new depth value is greater than or equal to the stored value. */
    GLEnum[GLEnum["GEQUAL"] = 518] = "GEQUAL";
    /** Passed to depthFunction or stencilFunction to specify depth or stencil tests will always pass, i.e., pixels will be drawn in the order they are drawn. */
    GLEnum[GLEnum["ALWAYS"] = 519] = "ALWAYS";
    // Stencil actions
    // Constants passed to stencilOp().
    GLEnum[GLEnum["KEEP"] = 7680] = "KEEP";
    GLEnum[GLEnum["REPLACE"] = 7681] = "REPLACE";
    GLEnum[GLEnum["INCR"] = 7682] = "INCR";
    GLEnum[GLEnum["DECR"] = 7683] = "DECR";
    GLEnum[GLEnum["INVERT"] = 5386] = "INVERT";
    GLEnum[GLEnum["INCR_WRAP"] = 34055] = "INCR_WRAP";
    GLEnum[GLEnum["DECR_WRAP"] = 34056] = "DECR_WRAP";
    // Textures
    // Constants passed to texParameteri(),
    // texParameterf(), bindTexture(), texImage2D(), and others.
    GLEnum[GLEnum["NEAREST"] = 9728] = "NEAREST";
    GLEnum[GLEnum["LINEAR"] = 9729] = "LINEAR";
    GLEnum[GLEnum["NEAREST_MIPMAP_NEAREST"] = 9984] = "NEAREST_MIPMAP_NEAREST";
    GLEnum[GLEnum["LINEAR_MIPMAP_NEAREST"] = 9985] = "LINEAR_MIPMAP_NEAREST";
    GLEnum[GLEnum["NEAREST_MIPMAP_LINEAR"] = 9986] = "NEAREST_MIPMAP_LINEAR";
    GLEnum[GLEnum["LINEAR_MIPMAP_LINEAR"] = 9987] = "LINEAR_MIPMAP_LINEAR";
    /** The texture magnification function is used when the pixel being textured maps to an area less than or equal to one texture element. It sets the texture magnification function to either GL_NEAREST or GL_LINEAR (see below). GL_NEAREST is generally faster than GL_LINEAR, but it can produce textured images with sharper edges because the transition between texture elements is not as smooth. Default: GL_LINEAR.  */
    GLEnum[GLEnum["TEXTURE_MAG_FILTER"] = 10240] = "TEXTURE_MAG_FILTER";
    /** The texture minifying function is used whenever the pixel being textured maps to an area greater than one texture element. There are six defined minifying functions. Two of them use the nearest one or nearest four texture elements to compute the texture value. The other four use mipmaps. Default: GL_NEAREST_MIPMAP_LINEAR */
    GLEnum[GLEnum["TEXTURE_MIN_FILTER"] = 10241] = "TEXTURE_MIN_FILTER";
    /** Sets the wrap parameter for texture coordinate  to either GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, or GL_REPEAT. G */
    GLEnum[GLEnum["TEXTURE_WRAP_S"] = 10242] = "TEXTURE_WRAP_S";
    /** Sets the wrap parameter for texture coordinate  to either GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, or GL_REPEAT. G */
    GLEnum[GLEnum["TEXTURE_WRAP_T"] = 10243] = "TEXTURE_WRAP_T";
    GLEnum[GLEnum["TEXTURE_2D"] = 3553] = "TEXTURE_2D";
    GLEnum[GLEnum["TEXTURE"] = 5890] = "TEXTURE";
    GLEnum[GLEnum["TEXTURE_CUBE_MAP"] = 34067] = "TEXTURE_CUBE_MAP";
    GLEnum[GLEnum["TEXTURE_BINDING_CUBE_MAP"] = 34068] = "TEXTURE_BINDING_CUBE_MAP";
    GLEnum[GLEnum["TEXTURE_CUBE_MAP_POSITIVE_X"] = 34069] = "TEXTURE_CUBE_MAP_POSITIVE_X";
    GLEnum[GLEnum["TEXTURE_CUBE_MAP_NEGATIVE_X"] = 34070] = "TEXTURE_CUBE_MAP_NEGATIVE_X";
    GLEnum[GLEnum["TEXTURE_CUBE_MAP_POSITIVE_Y"] = 34071] = "TEXTURE_CUBE_MAP_POSITIVE_Y";
    GLEnum[GLEnum["TEXTURE_CUBE_MAP_NEGATIVE_Y"] = 34072] = "TEXTURE_CUBE_MAP_NEGATIVE_Y";
    GLEnum[GLEnum["TEXTURE_CUBE_MAP_POSITIVE_Z"] = 34073] = "TEXTURE_CUBE_MAP_POSITIVE_Z";
    GLEnum[GLEnum["TEXTURE_CUBE_MAP_NEGATIVE_Z"] = 34074] = "TEXTURE_CUBE_MAP_NEGATIVE_Z";
    GLEnum[GLEnum["MAX_CUBE_MAP_TEXTURE_SIZE"] = 34076] = "MAX_CUBE_MAP_TEXTURE_SIZE";
    // TEXTURE0 - 31 0x84C0 - 0x84DF A texture unit.
    GLEnum[GLEnum["TEXTURE0"] = 33984] = "TEXTURE0";
    GLEnum[GLEnum["ACTIVE_TEXTURE"] = 34016] = "ACTIVE_TEXTURE";
    GLEnum[GLEnum["REPEAT"] = 10497] = "REPEAT";
    GLEnum[GLEnum["CLAMP_TO_EDGE"] = 33071] = "CLAMP_TO_EDGE";
    GLEnum[GLEnum["MIRRORED_REPEAT"] = 33648] = "MIRRORED_REPEAT";
    // Emulation
    GLEnum[GLEnum["TEXTURE_WIDTH"] = 4096] = "TEXTURE_WIDTH";
    GLEnum[GLEnum["TEXTURE_HEIGHT"] = 4097] = "TEXTURE_HEIGHT";
    // Uniform types
    GLEnum[GLEnum["FLOAT_VEC2"] = 35664] = "FLOAT_VEC2";
    GLEnum[GLEnum["FLOAT_VEC3"] = 35665] = "FLOAT_VEC3";
    GLEnum[GLEnum["FLOAT_VEC4"] = 35666] = "FLOAT_VEC4";
    GLEnum[GLEnum["INT_VEC2"] = 35667] = "INT_VEC2";
    GLEnum[GLEnum["INT_VEC3"] = 35668] = "INT_VEC3";
    GLEnum[GLEnum["INT_VEC4"] = 35669] = "INT_VEC4";
    GLEnum[GLEnum["BOOL"] = 35670] = "BOOL";
    GLEnum[GLEnum["BOOL_VEC2"] = 35671] = "BOOL_VEC2";
    GLEnum[GLEnum["BOOL_VEC3"] = 35672] = "BOOL_VEC3";
    GLEnum[GLEnum["BOOL_VEC4"] = 35673] = "BOOL_VEC4";
    GLEnum[GLEnum["FLOAT_MAT2"] = 35674] = "FLOAT_MAT2";
    GLEnum[GLEnum["FLOAT_MAT3"] = 35675] = "FLOAT_MAT3";
    GLEnum[GLEnum["FLOAT_MAT4"] = 35676] = "FLOAT_MAT4";
    GLEnum[GLEnum["SAMPLER_2D"] = 35678] = "SAMPLER_2D";
    GLEnum[GLEnum["SAMPLER_CUBE"] = 35680] = "SAMPLER_CUBE";
    // Shader precision-specified types
    GLEnum[GLEnum["LOW_FLOAT"] = 36336] = "LOW_FLOAT";
    GLEnum[GLEnum["MEDIUM_FLOAT"] = 36337] = "MEDIUM_FLOAT";
    GLEnum[GLEnum["HIGH_FLOAT"] = 36338] = "HIGH_FLOAT";
    GLEnum[GLEnum["LOW_INT"] = 36339] = "LOW_INT";
    GLEnum[GLEnum["MEDIUM_INT"] = 36340] = "MEDIUM_INT";
    GLEnum[GLEnum["HIGH_INT"] = 36341] = "HIGH_INT";
    // Framebuffers and renderbuffers
    GLEnum[GLEnum["FRAMEBUFFER"] = 36160] = "FRAMEBUFFER";
    GLEnum[GLEnum["RENDERBUFFER"] = 36161] = "RENDERBUFFER";
    GLEnum[GLEnum["RGBA4"] = 32854] = "RGBA4";
    GLEnum[GLEnum["RGB5_A1"] = 32855] = "RGB5_A1";
    GLEnum[GLEnum["RGB565"] = 36194] = "RGB565";
    GLEnum[GLEnum["DEPTH_COMPONENT16"] = 33189] = "DEPTH_COMPONENT16";
    GLEnum[GLEnum["STENCIL_INDEX"] = 6401] = "STENCIL_INDEX";
    GLEnum[GLEnum["STENCIL_INDEX8"] = 36168] = "STENCIL_INDEX8";
    GLEnum[GLEnum["DEPTH_STENCIL"] = 34041] = "DEPTH_STENCIL";
    GLEnum[GLEnum["RENDERBUFFER_WIDTH"] = 36162] = "RENDERBUFFER_WIDTH";
    GLEnum[GLEnum["RENDERBUFFER_HEIGHT"] = 36163] = "RENDERBUFFER_HEIGHT";
    GLEnum[GLEnum["RENDERBUFFER_INTERNAL_FORMAT"] = 36164] = "RENDERBUFFER_INTERNAL_FORMAT";
    GLEnum[GLEnum["RENDERBUFFER_RED_SIZE"] = 36176] = "RENDERBUFFER_RED_SIZE";
    GLEnum[GLEnum["RENDERBUFFER_GREEN_SIZE"] = 36177] = "RENDERBUFFER_GREEN_SIZE";
    GLEnum[GLEnum["RENDERBUFFER_BLUE_SIZE"] = 36178] = "RENDERBUFFER_BLUE_SIZE";
    GLEnum[GLEnum["RENDERBUFFER_ALPHA_SIZE"] = 36179] = "RENDERBUFFER_ALPHA_SIZE";
    GLEnum[GLEnum["RENDERBUFFER_DEPTH_SIZE"] = 36180] = "RENDERBUFFER_DEPTH_SIZE";
    GLEnum[GLEnum["RENDERBUFFER_STENCIL_SIZE"] = 36181] = "RENDERBUFFER_STENCIL_SIZE";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE"] = 36048] = "FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_OBJECT_NAME"] = 36049] = "FRAMEBUFFER_ATTACHMENT_OBJECT_NAME";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL"] = 36050] = "FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE"] = 36051] = "FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE";
    GLEnum[GLEnum["COLOR_ATTACHMENT0"] = 36064] = "COLOR_ATTACHMENT0";
    GLEnum[GLEnum["DEPTH_ATTACHMENT"] = 36096] = "DEPTH_ATTACHMENT";
    GLEnum[GLEnum["STENCIL_ATTACHMENT"] = 36128] = "STENCIL_ATTACHMENT";
    GLEnum[GLEnum["DEPTH_STENCIL_ATTACHMENT"] = 33306] = "DEPTH_STENCIL_ATTACHMENT";
    GLEnum[GLEnum["NONE"] = 0] = "NONE";
    GLEnum[GLEnum["FRAMEBUFFER_COMPLETE"] = 36053] = "FRAMEBUFFER_COMPLETE";
    GLEnum[GLEnum["FRAMEBUFFER_INCOMPLETE_ATTACHMENT"] = 36054] = "FRAMEBUFFER_INCOMPLETE_ATTACHMENT";
    GLEnum[GLEnum["FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT"] = 36055] = "FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT";
    GLEnum[GLEnum["FRAMEBUFFER_INCOMPLETE_DIMENSIONS"] = 36057] = "FRAMEBUFFER_INCOMPLETE_DIMENSIONS";
    GLEnum[GLEnum["FRAMEBUFFER_UNSUPPORTED"] = 36061] = "FRAMEBUFFER_UNSUPPORTED";
    GLEnum[GLEnum["FRAMEBUFFER_BINDING"] = 36006] = "FRAMEBUFFER_BINDING";
    GLEnum[GLEnum["RENDERBUFFER_BINDING"] = 36007] = "RENDERBUFFER_BINDING";
    GLEnum[GLEnum["READ_FRAMEBUFFER"] = 36008] = "READ_FRAMEBUFFER";
    GLEnum[GLEnum["DRAW_FRAMEBUFFER"] = 36009] = "DRAW_FRAMEBUFFER";
    GLEnum[GLEnum["MAX_RENDERBUFFER_SIZE"] = 34024] = "MAX_RENDERBUFFER_SIZE";
    GLEnum[GLEnum["INVALID_FRAMEBUFFER_OPERATION"] = 1286] = "INVALID_FRAMEBUFFER_OPERATION";
    // Pixel storage modes
    // Constants passed to pixelStorei().
    GLEnum[GLEnum["UNPACK_FLIP_Y_WEBGL"] = 37440] = "UNPACK_FLIP_Y_WEBGL";
    GLEnum[GLEnum["UNPACK_PREMULTIPLY_ALPHA_WEBGL"] = 37441] = "UNPACK_PREMULTIPLY_ALPHA_WEBGL";
    GLEnum[GLEnum["UNPACK_COLORSPACE_CONVERSION_WEBGL"] = 37443] = "UNPACK_COLORSPACE_CONVERSION_WEBGL";
    // Additional constants defined WebGL 2
    // These constants are defined on the WebGL2RenderingContext interface.
    // All WebGL 1 constants are also available in a WebGL 2 context.
    // Getting GL parameter information
    // Constants passed to getParameter()
    // to specify what information to return.
    GLEnum[GLEnum["READ_BUFFER"] = 3074] = "READ_BUFFER";
    GLEnum[GLEnum["UNPACK_ROW_LENGTH"] = 3314] = "UNPACK_ROW_LENGTH";
    GLEnum[GLEnum["UNPACK_SKIP_ROWS"] = 3315] = "UNPACK_SKIP_ROWS";
    GLEnum[GLEnum["UNPACK_SKIP_PIXELS"] = 3316] = "UNPACK_SKIP_PIXELS";
    GLEnum[GLEnum["PACK_ROW_LENGTH"] = 3330] = "PACK_ROW_LENGTH";
    GLEnum[GLEnum["PACK_SKIP_ROWS"] = 3331] = "PACK_SKIP_ROWS";
    GLEnum[GLEnum["PACK_SKIP_PIXELS"] = 3332] = "PACK_SKIP_PIXELS";
    GLEnum[GLEnum["TEXTURE_BINDING_3D"] = 32874] = "TEXTURE_BINDING_3D";
    GLEnum[GLEnum["UNPACK_SKIP_IMAGES"] = 32877] = "UNPACK_SKIP_IMAGES";
    GLEnum[GLEnum["UNPACK_IMAGE_HEIGHT"] = 32878] = "UNPACK_IMAGE_HEIGHT";
    GLEnum[GLEnum["MAX_3D_TEXTURE_SIZE"] = 32883] = "MAX_3D_TEXTURE_SIZE";
    GLEnum[GLEnum["MAX_ELEMENTS_VERTICES"] = 33000] = "MAX_ELEMENTS_VERTICES";
    GLEnum[GLEnum["MAX_ELEMENTS_INDICES"] = 33001] = "MAX_ELEMENTS_INDICES";
    GLEnum[GLEnum["MAX_TEXTURE_LOD_BIAS"] = 34045] = "MAX_TEXTURE_LOD_BIAS";
    GLEnum[GLEnum["MAX_FRAGMENT_UNIFORM_COMPONENTS"] = 35657] = "MAX_FRAGMENT_UNIFORM_COMPONENTS";
    GLEnum[GLEnum["MAX_VERTEX_UNIFORM_COMPONENTS"] = 35658] = "MAX_VERTEX_UNIFORM_COMPONENTS";
    GLEnum[GLEnum["MAX_ARRAY_TEXTURE_LAYERS"] = 35071] = "MAX_ARRAY_TEXTURE_LAYERS";
    GLEnum[GLEnum["MIN_PROGRAM_TEXEL_OFFSET"] = 35076] = "MIN_PROGRAM_TEXEL_OFFSET";
    GLEnum[GLEnum["MAX_PROGRAM_TEXEL_OFFSET"] = 35077] = "MAX_PROGRAM_TEXEL_OFFSET";
    GLEnum[GLEnum["MAX_VARYING_COMPONENTS"] = 35659] = "MAX_VARYING_COMPONENTS";
    GLEnum[GLEnum["FRAGMENT_SHADER_DERIVATIVE_HINT"] = 35723] = "FRAGMENT_SHADER_DERIVATIVE_HINT";
    GLEnum[GLEnum["RASTERIZER_DISCARD"] = 35977] = "RASTERIZER_DISCARD";
    GLEnum[GLEnum["VERTEX_ARRAY_BINDING"] = 34229] = "VERTEX_ARRAY_BINDING";
    GLEnum[GLEnum["MAX_VERTEX_OUTPUT_COMPONENTS"] = 37154] = "MAX_VERTEX_OUTPUT_COMPONENTS";
    GLEnum[GLEnum["MAX_FRAGMENT_INPUT_COMPONENTS"] = 37157] = "MAX_FRAGMENT_INPUT_COMPONENTS";
    GLEnum[GLEnum["MAX_SERVER_WAIT_TIMEOUT"] = 37137] = "MAX_SERVER_WAIT_TIMEOUT";
    GLEnum[GLEnum["MAX_ELEMENT_INDEX"] = 36203] = "MAX_ELEMENT_INDEX";
    // Textures
    // Constants passed to texParameteri(),
    // texParameterf(), bindTexture(), texImage2D(), and others.
    GLEnum[GLEnum["RED"] = 6403] = "RED";
    GLEnum[GLEnum["RGB8"] = 32849] = "RGB8";
    GLEnum[GLEnum["RGBA8"] = 32856] = "RGBA8";
    GLEnum[GLEnum["RGB10_A2"] = 32857] = "RGB10_A2";
    GLEnum[GLEnum["TEXTURE_3D"] = 32879] = "TEXTURE_3D";
    /** Sets the wrap parameter for texture coordinate  to either GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, or GL_REPEAT. G */
    GLEnum[GLEnum["TEXTURE_WRAP_R"] = 32882] = "TEXTURE_WRAP_R";
    GLEnum[GLEnum["TEXTURE_MIN_LOD"] = 33082] = "TEXTURE_MIN_LOD";
    GLEnum[GLEnum["TEXTURE_MAX_LOD"] = 33083] = "TEXTURE_MAX_LOD";
    GLEnum[GLEnum["TEXTURE_BASE_LEVEL"] = 33084] = "TEXTURE_BASE_LEVEL";
    GLEnum[GLEnum["TEXTURE_MAX_LEVEL"] = 33085] = "TEXTURE_MAX_LEVEL";
    GLEnum[GLEnum["TEXTURE_COMPARE_MODE"] = 34892] = "TEXTURE_COMPARE_MODE";
    GLEnum[GLEnum["TEXTURE_COMPARE_FUNC"] = 34893] = "TEXTURE_COMPARE_FUNC";
    GLEnum[GLEnum["SRGB"] = 35904] = "SRGB";
    GLEnum[GLEnum["SRGB8"] = 35905] = "SRGB8";
    GLEnum[GLEnum["SRGB8_ALPHA8"] = 35907] = "SRGB8_ALPHA8";
    GLEnum[GLEnum["COMPARE_REF_TO_TEXTURE"] = 34894] = "COMPARE_REF_TO_TEXTURE";
    GLEnum[GLEnum["RGBA32F"] = 34836] = "RGBA32F";
    GLEnum[GLEnum["RGB32F"] = 34837] = "RGB32F";
    GLEnum[GLEnum["RGBA16F"] = 34842] = "RGBA16F";
    GLEnum[GLEnum["RGB16F"] = 34843] = "RGB16F";
    GLEnum[GLEnum["TEXTURE_2D_ARRAY"] = 35866] = "TEXTURE_2D_ARRAY";
    GLEnum[GLEnum["TEXTURE_BINDING_2D_ARRAY"] = 35869] = "TEXTURE_BINDING_2D_ARRAY";
    GLEnum[GLEnum["R11F_G11F_B10F"] = 35898] = "R11F_G11F_B10F";
    GLEnum[GLEnum["RGB9_E5"] = 35901] = "RGB9_E5";
    GLEnum[GLEnum["RGBA32UI"] = 36208] = "RGBA32UI";
    GLEnum[GLEnum["RGB32UI"] = 36209] = "RGB32UI";
    GLEnum[GLEnum["RGBA16UI"] = 36214] = "RGBA16UI";
    GLEnum[GLEnum["RGB16UI"] = 36215] = "RGB16UI";
    GLEnum[GLEnum["RGBA8UI"] = 36220] = "RGBA8UI";
    GLEnum[GLEnum["RGB8UI"] = 36221] = "RGB8UI";
    GLEnum[GLEnum["RGBA32I"] = 36226] = "RGBA32I";
    GLEnum[GLEnum["RGB32I"] = 36227] = "RGB32I";
    GLEnum[GLEnum["RGBA16I"] = 36232] = "RGBA16I";
    GLEnum[GLEnum["RGB16I"] = 36233] = "RGB16I";
    GLEnum[GLEnum["RGBA8I"] = 36238] = "RGBA8I";
    GLEnum[GLEnum["RGB8I"] = 36239] = "RGB8I";
    GLEnum[GLEnum["RED_INTEGER"] = 36244] = "RED_INTEGER";
    GLEnum[GLEnum["RGB_INTEGER"] = 36248] = "RGB_INTEGER";
    GLEnum[GLEnum["RGBA_INTEGER"] = 36249] = "RGBA_INTEGER";
    GLEnum[GLEnum["R8"] = 33321] = "R8";
    GLEnum[GLEnum["RG8"] = 33323] = "RG8";
    GLEnum[GLEnum["R16F"] = 33325] = "R16F";
    GLEnum[GLEnum["R32F"] = 33326] = "R32F";
    GLEnum[GLEnum["RG16F"] = 33327] = "RG16F";
    GLEnum[GLEnum["RG32F"] = 33328] = "RG32F";
    GLEnum[GLEnum["R8I"] = 33329] = "R8I";
    GLEnum[GLEnum["R8UI"] = 33330] = "R8UI";
    GLEnum[GLEnum["R16I"] = 33331] = "R16I";
    GLEnum[GLEnum["R16UI"] = 33332] = "R16UI";
    GLEnum[GLEnum["R32I"] = 33333] = "R32I";
    GLEnum[GLEnum["R32UI"] = 33334] = "R32UI";
    GLEnum[GLEnum["RG8I"] = 33335] = "RG8I";
    GLEnum[GLEnum["RG8UI"] = 33336] = "RG8UI";
    GLEnum[GLEnum["RG16I"] = 33337] = "RG16I";
    GLEnum[GLEnum["RG16UI"] = 33338] = "RG16UI";
    GLEnum[GLEnum["RG32I"] = 33339] = "RG32I";
    GLEnum[GLEnum["RG32UI"] = 33340] = "RG32UI";
    GLEnum[GLEnum["R8_SNORM"] = 36756] = "R8_SNORM";
    GLEnum[GLEnum["RG8_SNORM"] = 36757] = "RG8_SNORM";
    GLEnum[GLEnum["RGB8_SNORM"] = 36758] = "RGB8_SNORM";
    GLEnum[GLEnum["RGBA8_SNORM"] = 36759] = "RGBA8_SNORM";
    GLEnum[GLEnum["RGB10_A2UI"] = 36975] = "RGB10_A2UI";
    /* covered by extension
    COMPRESSED_R11_EAC  = 0x9270,
    COMPRESSED_SIGNED_R11_EAC = 0x9271,
    COMPRESSED_RG11_EAC = 0x9272,
    COMPRESSED_SIGNED_RG11_EAC  = 0x9273,
    COMPRESSED_RGB8_ETC2  = 0x9274,
    COMPRESSED_SRGB8_ETC2 = 0x9275,
    COMPRESSED_RGB8_PUNCHTHROUGH_ALPHA1_ETC2  = 0x9276,
    COMPRESSED_SRGB8_PUNCHTHROUGH_ALPHA1_ETC  = 0x9277,
    COMPRESSED_RGBA8_ETC2_EAC = 0x9278,
    COMPRESSED_SRGB8_ALPHA8_ETC2_EAC  = 0x9279,
    */
    GLEnum[GLEnum["TEXTURE_IMMUTABLE_FORMAT"] = 37167] = "TEXTURE_IMMUTABLE_FORMAT";
    GLEnum[GLEnum["TEXTURE_IMMUTABLE_LEVELS"] = 33503] = "TEXTURE_IMMUTABLE_LEVELS";
    // Pixel types
    GLEnum[GLEnum["UNSIGNED_INT_2_10_10_10_REV"] = 33640] = "UNSIGNED_INT_2_10_10_10_REV";
    GLEnum[GLEnum["UNSIGNED_INT_10F_11F_11F_REV"] = 35899] = "UNSIGNED_INT_10F_11F_11F_REV";
    GLEnum[GLEnum["UNSIGNED_INT_5_9_9_9_REV"] = 35902] = "UNSIGNED_INT_5_9_9_9_REV";
    GLEnum[GLEnum["FLOAT_32_UNSIGNED_INT_24_8_REV"] = 36269] = "FLOAT_32_UNSIGNED_INT_24_8_REV";
    GLEnum[GLEnum["UNSIGNED_INT_24_8"] = 34042] = "UNSIGNED_INT_24_8";
    GLEnum[GLEnum["HALF_FLOAT"] = 5131] = "HALF_FLOAT";
    GLEnum[GLEnum["RG"] = 33319] = "RG";
    GLEnum[GLEnum["RG_INTEGER"] = 33320] = "RG_INTEGER";
    GLEnum[GLEnum["INT_2_10_10_10_REV"] = 36255] = "INT_2_10_10_10_REV";
    // Queries
    GLEnum[GLEnum["CURRENT_QUERY"] = 34917] = "CURRENT_QUERY";
    /** Returns a GLuint containing the query result. */
    GLEnum[GLEnum["QUERY_RESULT"] = 34918] = "QUERY_RESULT";
    /** Whether query result is available. */
    GLEnum[GLEnum["QUERY_RESULT_AVAILABLE"] = 34919] = "QUERY_RESULT_AVAILABLE";
    /** Occlusion query (if drawing passed depth test)  */
    GLEnum[GLEnum["ANY_SAMPLES_PASSED"] = 35887] = "ANY_SAMPLES_PASSED";
    /** Occlusion query less accurate/faster version */
    GLEnum[GLEnum["ANY_SAMPLES_PASSED_CONSERVATIVE"] = 36202] = "ANY_SAMPLES_PASSED_CONSERVATIVE";
    // Draw buffers
    GLEnum[GLEnum["MAX_DRAW_BUFFERS"] = 34852] = "MAX_DRAW_BUFFERS";
    GLEnum[GLEnum["DRAW_BUFFER0"] = 34853] = "DRAW_BUFFER0";
    GLEnum[GLEnum["DRAW_BUFFER1"] = 34854] = "DRAW_BUFFER1";
    GLEnum[GLEnum["DRAW_BUFFER2"] = 34855] = "DRAW_BUFFER2";
    GLEnum[GLEnum["DRAW_BUFFER3"] = 34856] = "DRAW_BUFFER3";
    GLEnum[GLEnum["DRAW_BUFFER4"] = 34857] = "DRAW_BUFFER4";
    GLEnum[GLEnum["DRAW_BUFFER5"] = 34858] = "DRAW_BUFFER5";
    GLEnum[GLEnum["DRAW_BUFFER6"] = 34859] = "DRAW_BUFFER6";
    GLEnum[GLEnum["DRAW_BUFFER7"] = 34860] = "DRAW_BUFFER7";
    GLEnum[GLEnum["DRAW_BUFFER8"] = 34861] = "DRAW_BUFFER8";
    GLEnum[GLEnum["DRAW_BUFFER9"] = 34862] = "DRAW_BUFFER9";
    GLEnum[GLEnum["DRAW_BUFFER10"] = 34863] = "DRAW_BUFFER10";
    GLEnum[GLEnum["DRAW_BUFFER11"] = 34864] = "DRAW_BUFFER11";
    GLEnum[GLEnum["DRAW_BUFFER12"] = 34865] = "DRAW_BUFFER12";
    GLEnum[GLEnum["DRAW_BUFFER13"] = 34866] = "DRAW_BUFFER13";
    GLEnum[GLEnum["DRAW_BUFFER14"] = 34867] = "DRAW_BUFFER14";
    GLEnum[GLEnum["DRAW_BUFFER15"] = 34868] = "DRAW_BUFFER15";
    GLEnum[GLEnum["MAX_COLOR_ATTACHMENTS"] = 36063] = "MAX_COLOR_ATTACHMENTS";
    GLEnum[GLEnum["COLOR_ATTACHMENT1"] = 36065] = "COLOR_ATTACHMENT1";
    GLEnum[GLEnum["COLOR_ATTACHMENT2"] = 36066] = "COLOR_ATTACHMENT2";
    GLEnum[GLEnum["COLOR_ATTACHMENT3"] = 36067] = "COLOR_ATTACHMENT3";
    GLEnum[GLEnum["COLOR_ATTACHMENT4"] = 36068] = "COLOR_ATTACHMENT4";
    GLEnum[GLEnum["COLOR_ATTACHMENT5"] = 36069] = "COLOR_ATTACHMENT5";
    GLEnum[GLEnum["COLOR_ATTACHMENT6"] = 36070] = "COLOR_ATTACHMENT6";
    GLEnum[GLEnum["COLOR_ATTACHMENT7"] = 36071] = "COLOR_ATTACHMENT7";
    GLEnum[GLEnum["COLOR_ATTACHMENT8"] = 36072] = "COLOR_ATTACHMENT8";
    GLEnum[GLEnum["COLOR_ATTACHMENT9"] = 36073] = "COLOR_ATTACHMENT9";
    GLEnum[GLEnum["COLOR_ATTACHMENT10"] = 36074] = "COLOR_ATTACHMENT10";
    GLEnum[GLEnum["COLOR_ATTACHMENT11"] = 36075] = "COLOR_ATTACHMENT11";
    GLEnum[GLEnum["COLOR_ATTACHMENT12"] = 36076] = "COLOR_ATTACHMENT12";
    GLEnum[GLEnum["COLOR_ATTACHMENT13"] = 36077] = "COLOR_ATTACHMENT13";
    GLEnum[GLEnum["COLOR_ATTACHMENT14"] = 36078] = "COLOR_ATTACHMENT14";
    GLEnum[GLEnum["COLOR_ATTACHMENT15"] = 36079] = "COLOR_ATTACHMENT15";
    // Samplers
    GLEnum[GLEnum["SAMPLER_3D"] = 35679] = "SAMPLER_3D";
    GLEnum[GLEnum["SAMPLER_2D_SHADOW"] = 35682] = "SAMPLER_2D_SHADOW";
    GLEnum[GLEnum["SAMPLER_2D_ARRAY"] = 36289] = "SAMPLER_2D_ARRAY";
    GLEnum[GLEnum["SAMPLER_2D_ARRAY_SHADOW"] = 36292] = "SAMPLER_2D_ARRAY_SHADOW";
    GLEnum[GLEnum["SAMPLER_CUBE_SHADOW"] = 36293] = "SAMPLER_CUBE_SHADOW";
    GLEnum[GLEnum["INT_SAMPLER_2D"] = 36298] = "INT_SAMPLER_2D";
    GLEnum[GLEnum["INT_SAMPLER_3D"] = 36299] = "INT_SAMPLER_3D";
    GLEnum[GLEnum["INT_SAMPLER_CUBE"] = 36300] = "INT_SAMPLER_CUBE";
    GLEnum[GLEnum["INT_SAMPLER_2D_ARRAY"] = 36303] = "INT_SAMPLER_2D_ARRAY";
    GLEnum[GLEnum["UNSIGNED_INT_SAMPLER_2D"] = 36306] = "UNSIGNED_INT_SAMPLER_2D";
    GLEnum[GLEnum["UNSIGNED_INT_SAMPLER_3D"] = 36307] = "UNSIGNED_INT_SAMPLER_3D";
    GLEnum[GLEnum["UNSIGNED_INT_SAMPLER_CUBE"] = 36308] = "UNSIGNED_INT_SAMPLER_CUBE";
    GLEnum[GLEnum["UNSIGNED_INT_SAMPLER_2D_ARRAY"] = 36311] = "UNSIGNED_INT_SAMPLER_2D_ARRAY";
    GLEnum[GLEnum["MAX_SAMPLES"] = 36183] = "MAX_SAMPLES";
    GLEnum[GLEnum["SAMPLER_BINDING"] = 35097] = "SAMPLER_BINDING";
    // Buffers
    GLEnum[GLEnum["PIXEL_PACK_BUFFER"] = 35051] = "PIXEL_PACK_BUFFER";
    GLEnum[GLEnum["PIXEL_UNPACK_BUFFER"] = 35052] = "PIXEL_UNPACK_BUFFER";
    GLEnum[GLEnum["PIXEL_PACK_BUFFER_BINDING"] = 35053] = "PIXEL_PACK_BUFFER_BINDING";
    GLEnum[GLEnum["PIXEL_UNPACK_BUFFER_BINDING"] = 35055] = "PIXEL_UNPACK_BUFFER_BINDING";
    GLEnum[GLEnum["COPY_READ_BUFFER"] = 36662] = "COPY_READ_BUFFER";
    GLEnum[GLEnum["COPY_WRITE_BUFFER"] = 36663] = "COPY_WRITE_BUFFER";
    GLEnum[GLEnum["COPY_READ_BUFFER_BINDING"] = 36662] = "COPY_READ_BUFFER_BINDING";
    GLEnum[GLEnum["COPY_WRITE_BUFFER_BINDING"] = 36663] = "COPY_WRITE_BUFFER_BINDING";
    // Data types
    GLEnum[GLEnum["FLOAT_MAT2x3"] = 35685] = "FLOAT_MAT2x3";
    GLEnum[GLEnum["FLOAT_MAT2x4"] = 35686] = "FLOAT_MAT2x4";
    GLEnum[GLEnum["FLOAT_MAT3x2"] = 35687] = "FLOAT_MAT3x2";
    GLEnum[GLEnum["FLOAT_MAT3x4"] = 35688] = "FLOAT_MAT3x4";
    GLEnum[GLEnum["FLOAT_MAT4x2"] = 35689] = "FLOAT_MAT4x2";
    GLEnum[GLEnum["FLOAT_MAT4x3"] = 35690] = "FLOAT_MAT4x3";
    GLEnum[GLEnum["UNSIGNED_INT_VEC2"] = 36294] = "UNSIGNED_INT_VEC2";
    GLEnum[GLEnum["UNSIGNED_INT_VEC3"] = 36295] = "UNSIGNED_INT_VEC3";
    GLEnum[GLEnum["UNSIGNED_INT_VEC4"] = 36296] = "UNSIGNED_INT_VEC4";
    GLEnum[GLEnum["UNSIGNED_NORMALIZED"] = 35863] = "UNSIGNED_NORMALIZED";
    GLEnum[GLEnum["SIGNED_NORMALIZED"] = 36764] = "SIGNED_NORMALIZED";
    // Vertex attributes
    GLEnum[GLEnum["VERTEX_ATTRIB_ARRAY_INTEGER"] = 35069] = "VERTEX_ATTRIB_ARRAY_INTEGER";
    GLEnum[GLEnum["VERTEX_ATTRIB_ARRAY_DIVISOR"] = 35070] = "VERTEX_ATTRIB_ARRAY_DIVISOR";
    // Transform feedback
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_BUFFER_MODE"] = 35967] = "TRANSFORM_FEEDBACK_BUFFER_MODE";
    GLEnum[GLEnum["MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS"] = 35968] = "MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_VARYINGS"] = 35971] = "TRANSFORM_FEEDBACK_VARYINGS";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_BUFFER_START"] = 35972] = "TRANSFORM_FEEDBACK_BUFFER_START";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_BUFFER_SIZE"] = 35973] = "TRANSFORM_FEEDBACK_BUFFER_SIZE";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN"] = 35976] = "TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN";
    GLEnum[GLEnum["MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS"] = 35978] = "MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS";
    GLEnum[GLEnum["MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS"] = 35979] = "MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS";
    GLEnum[GLEnum["INTERLEAVED_ATTRIBS"] = 35980] = "INTERLEAVED_ATTRIBS";
    GLEnum[GLEnum["SEPARATE_ATTRIBS"] = 35981] = "SEPARATE_ATTRIBS";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_BUFFER"] = 35982] = "TRANSFORM_FEEDBACK_BUFFER";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_BUFFER_BINDING"] = 35983] = "TRANSFORM_FEEDBACK_BUFFER_BINDING";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK"] = 36386] = "TRANSFORM_FEEDBACK";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_PAUSED"] = 36387] = "TRANSFORM_FEEDBACK_PAUSED";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_ACTIVE"] = 36388] = "TRANSFORM_FEEDBACK_ACTIVE";
    GLEnum[GLEnum["TRANSFORM_FEEDBACK_BINDING"] = 36389] = "TRANSFORM_FEEDBACK_BINDING";
    // Framebuffers and renderbuffers
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING"] = 33296] = "FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE"] = 33297] = "FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_RED_SIZE"] = 33298] = "FRAMEBUFFER_ATTACHMENT_RED_SIZE";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_GREEN_SIZE"] = 33299] = "FRAMEBUFFER_ATTACHMENT_GREEN_SIZE";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_BLUE_SIZE"] = 33300] = "FRAMEBUFFER_ATTACHMENT_BLUE_SIZE";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_ALPHA_SIZE"] = 33301] = "FRAMEBUFFER_ATTACHMENT_ALPHA_SIZE";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_DEPTH_SIZE"] = 33302] = "FRAMEBUFFER_ATTACHMENT_DEPTH_SIZE";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE"] = 33303] = "FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE";
    GLEnum[GLEnum["FRAMEBUFFER_DEFAULT"] = 33304] = "FRAMEBUFFER_DEFAULT";
    // DEPTH_STENCIL_ATTACHMENT  = 0x821A,
    // DEPTH_STENCIL = 0x84F9,
    GLEnum[GLEnum["DEPTH24_STENCIL8"] = 35056] = "DEPTH24_STENCIL8";
    GLEnum[GLEnum["DRAW_FRAMEBUFFER_BINDING"] = 36006] = "DRAW_FRAMEBUFFER_BINDING";
    GLEnum[GLEnum["READ_FRAMEBUFFER_BINDING"] = 36010] = "READ_FRAMEBUFFER_BINDING";
    GLEnum[GLEnum["RENDERBUFFER_SAMPLES"] = 36011] = "RENDERBUFFER_SAMPLES";
    GLEnum[GLEnum["FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER"] = 36052] = "FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER";
    GLEnum[GLEnum["FRAMEBUFFER_INCOMPLETE_MULTISAMPLE"] = 36182] = "FRAMEBUFFER_INCOMPLETE_MULTISAMPLE";
    // Uniforms
    GLEnum[GLEnum["UNIFORM_BUFFER"] = 35345] = "UNIFORM_BUFFER";
    GLEnum[GLEnum["UNIFORM_BUFFER_BINDING"] = 35368] = "UNIFORM_BUFFER_BINDING";
    GLEnum[GLEnum["UNIFORM_BUFFER_START"] = 35369] = "UNIFORM_BUFFER_START";
    GLEnum[GLEnum["UNIFORM_BUFFER_SIZE"] = 35370] = "UNIFORM_BUFFER_SIZE";
    GLEnum[GLEnum["MAX_VERTEX_UNIFORM_BLOCKS"] = 35371] = "MAX_VERTEX_UNIFORM_BLOCKS";
    GLEnum[GLEnum["MAX_FRAGMENT_UNIFORM_BLOCKS"] = 35373] = "MAX_FRAGMENT_UNIFORM_BLOCKS";
    GLEnum[GLEnum["MAX_COMBINED_UNIFORM_BLOCKS"] = 35374] = "MAX_COMBINED_UNIFORM_BLOCKS";
    GLEnum[GLEnum["MAX_UNIFORM_BUFFER_BINDINGS"] = 35375] = "MAX_UNIFORM_BUFFER_BINDINGS";
    GLEnum[GLEnum["MAX_UNIFORM_BLOCK_SIZE"] = 35376] = "MAX_UNIFORM_BLOCK_SIZE";
    GLEnum[GLEnum["MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS"] = 35377] = "MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS";
    GLEnum[GLEnum["MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS"] = 35379] = "MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS";
    GLEnum[GLEnum["UNIFORM_BUFFER_OFFSET_ALIGNMENT"] = 35380] = "UNIFORM_BUFFER_OFFSET_ALIGNMENT";
    GLEnum[GLEnum["ACTIVE_UNIFORM_BLOCKS"] = 35382] = "ACTIVE_UNIFORM_BLOCKS";
    GLEnum[GLEnum["UNIFORM_TYPE"] = 35383] = "UNIFORM_TYPE";
    GLEnum[GLEnum["UNIFORM_SIZE"] = 35384] = "UNIFORM_SIZE";
    GLEnum[GLEnum["UNIFORM_BLOCK_INDEX"] = 35386] = "UNIFORM_BLOCK_INDEX";
    GLEnum[GLEnum["UNIFORM_OFFSET"] = 35387] = "UNIFORM_OFFSET";
    GLEnum[GLEnum["UNIFORM_ARRAY_STRIDE"] = 35388] = "UNIFORM_ARRAY_STRIDE";
    GLEnum[GLEnum["UNIFORM_MATRIX_STRIDE"] = 35389] = "UNIFORM_MATRIX_STRIDE";
    GLEnum[GLEnum["UNIFORM_IS_ROW_MAJOR"] = 35390] = "UNIFORM_IS_ROW_MAJOR";
    GLEnum[GLEnum["UNIFORM_BLOCK_BINDING"] = 35391] = "UNIFORM_BLOCK_BINDING";
    GLEnum[GLEnum["UNIFORM_BLOCK_DATA_SIZE"] = 35392] = "UNIFORM_BLOCK_DATA_SIZE";
    GLEnum[GLEnum["UNIFORM_BLOCK_ACTIVE_UNIFORMS"] = 35394] = "UNIFORM_BLOCK_ACTIVE_UNIFORMS";
    GLEnum[GLEnum["UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES"] = 35395] = "UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES";
    GLEnum[GLEnum["UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER"] = 35396] = "UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER";
    GLEnum[GLEnum["UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER"] = 35398] = "UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER";
    // Sync objects
    GLEnum[GLEnum["OBJECT_TYPE"] = 37138] = "OBJECT_TYPE";
    GLEnum[GLEnum["SYNC_CONDITION"] = 37139] = "SYNC_CONDITION";
    GLEnum[GLEnum["SYNC_STATUS"] = 37140] = "SYNC_STATUS";
    GLEnum[GLEnum["SYNC_FLAGS"] = 37141] = "SYNC_FLAGS";
    GLEnum[GLEnum["SYNC_FENCE"] = 37142] = "SYNC_FENCE";
    GLEnum[GLEnum["SYNC_GPU_COMMANDS_COMPLETE"] = 37143] = "SYNC_GPU_COMMANDS_COMPLETE";
    GLEnum[GLEnum["UNSIGNALED"] = 37144] = "UNSIGNALED";
    GLEnum[GLEnum["SIGNALED"] = 37145] = "SIGNALED";
    GLEnum[GLEnum["ALREADY_SIGNALED"] = 37146] = "ALREADY_SIGNALED";
    GLEnum[GLEnum["TIMEOUT_EXPIRED"] = 37147] = "TIMEOUT_EXPIRED";
    GLEnum[GLEnum["CONDITION_SATISFIED"] = 37148] = "CONDITION_SATISFIED";
    GLEnum[GLEnum["WAIT_FAILED"] = 37149] = "WAIT_FAILED";
    GLEnum[GLEnum["SYNC_FLUSH_COMMANDS_BIT"] = 1] = "SYNC_FLUSH_COMMANDS_BIT";
    // Miscellaneous constants
    GLEnum[GLEnum["COLOR"] = 6144] = "COLOR";
    GLEnum[GLEnum["DEPTH"] = 6145] = "DEPTH";
    GLEnum[GLEnum["STENCIL"] = 6146] = "STENCIL";
    GLEnum[GLEnum["MIN"] = 32775] = "MIN";
    GLEnum[GLEnum["MAX"] = 32776] = "MAX";
    GLEnum[GLEnum["DEPTH_COMPONENT24"] = 33190] = "DEPTH_COMPONENT24";
    GLEnum[GLEnum["STREAM_READ"] = 35041] = "STREAM_READ";
    GLEnum[GLEnum["STREAM_COPY"] = 35042] = "STREAM_COPY";
    GLEnum[GLEnum["STATIC_READ"] = 35045] = "STATIC_READ";
    GLEnum[GLEnum["STATIC_COPY"] = 35046] = "STATIC_COPY";
    GLEnum[GLEnum["DYNAMIC_READ"] = 35049] = "DYNAMIC_READ";
    GLEnum[GLEnum["DYNAMIC_COPY"] = 35050] = "DYNAMIC_COPY";
    GLEnum[GLEnum["DEPTH_COMPONENT32F"] = 36012] = "DEPTH_COMPONENT32F";
    GLEnum[GLEnum["DEPTH32F_STENCIL8"] = 36013] = "DEPTH32F_STENCIL8";
    GLEnum[GLEnum["INVALID_INDEX"] = 4294967295] = "INVALID_INDEX";
    GLEnum[GLEnum["TIMEOUT_IGNORED"] = -1] = "TIMEOUT_IGNORED";
    GLEnum[GLEnum["MAX_CLIENT_WAIT_TIMEOUT_WEBGL"] = 37447] = "MAX_CLIENT_WAIT_TIMEOUT_WEBGL";
    // Constants defined in WebGL extensions
    // WEBGL_debug_renderer_info
    /** Passed to getParameter to get the vendor string of the graphics driver. */
    GLEnum[GLEnum["UNMASKED_VENDOR_WEBGL"] = 37445] = "UNMASKED_VENDOR_WEBGL";
    /** Passed to getParameter to get the renderer string of the graphics driver. */
    GLEnum[GLEnum["UNMASKED_RENDERER_WEBGL"] = 37446] = "UNMASKED_RENDERER_WEBGL";
    // EXT_texture_filter_anisotropic
    /** Returns the maximum available anisotropy. */
    GLEnum[GLEnum["MAX_TEXTURE_MAX_ANISOTROPY_EXT"] = 34047] = "MAX_TEXTURE_MAX_ANISOTROPY_EXT";
    /** Passed to texParameter to set the desired maximum anisotropy for a texture. */
    GLEnum[GLEnum["TEXTURE_MAX_ANISOTROPY_EXT"] = 34046] = "TEXTURE_MAX_ANISOTROPY_EXT";
    // EXT_texture_norm16 - https://khronos.org/registry/webgl/extensions/EXT_texture_norm16/
    GLEnum[GLEnum["R16_EXT"] = 33322] = "R16_EXT";
    GLEnum[GLEnum["RG16_EXT"] = 33324] = "RG16_EXT";
    GLEnum[GLEnum["RGB16_EXT"] = 32852] = "RGB16_EXT";
    GLEnum[GLEnum["RGBA16_EXT"] = 32859] = "RGBA16_EXT";
    GLEnum[GLEnum["R16_SNORM_EXT"] = 36760] = "R16_SNORM_EXT";
    GLEnum[GLEnum["RG16_SNORM_EXT"] = 36761] = "RG16_SNORM_EXT";
    GLEnum[GLEnum["RGB16_SNORM_EXT"] = 36762] = "RGB16_SNORM_EXT";
    GLEnum[GLEnum["RGBA16_SNORM_EXT"] = 36763] = "RGBA16_SNORM_EXT";
    // WEBGL_compressed_texture_s3tc (BC1, BC2, BC3)
    /** A DXT1-compressed image in an RGB image format. */
    GLEnum[GLEnum["COMPRESSED_RGB_S3TC_DXT1_EXT"] = 33776] = "COMPRESSED_RGB_S3TC_DXT1_EXT";
    /** A DXT1-compressed image in an RGB image format with a simple on/off alpha value. */
    GLEnum[GLEnum["COMPRESSED_RGBA_S3TC_DXT1_EXT"] = 33777] = "COMPRESSED_RGBA_S3TC_DXT1_EXT";
    /** A DXT3-compressed image in an RGBA image format. Compared to a 32-bit RGBA texture, it offers 4:1 compression. */
    GLEnum[GLEnum["COMPRESSED_RGBA_S3TC_DXT3_EXT"] = 33778] = "COMPRESSED_RGBA_S3TC_DXT3_EXT";
    /** A DXT5-compressed image in an RGBA image format. It also provides a 4:1 compression, but differs to the DXT3 compression in how the alpha compression is done. */
    GLEnum[GLEnum["COMPRESSED_RGBA_S3TC_DXT5_EXT"] = 33779] = "COMPRESSED_RGBA_S3TC_DXT5_EXT";
    // WEBGL_compressed_texture_s3tc_srgb (BC1, BC2, BC3 -  SRGB)
    GLEnum[GLEnum["COMPRESSED_SRGB_S3TC_DXT1_EXT"] = 35916] = "COMPRESSED_SRGB_S3TC_DXT1_EXT";
    GLEnum[GLEnum["COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT"] = 35917] = "COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT";
    GLEnum[GLEnum["COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT"] = 35918] = "COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT";
    GLEnum[GLEnum["COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT"] = 35919] = "COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT";
    // WEBGL_compressed_texture_rgtc (BC4, BC5)
    GLEnum[GLEnum["COMPRESSED_RED_RGTC1_EXT"] = 36283] = "COMPRESSED_RED_RGTC1_EXT";
    GLEnum[GLEnum["COMPRESSED_SIGNED_RED_RGTC1_EXT"] = 36284] = "COMPRESSED_SIGNED_RED_RGTC1_EXT";
    GLEnum[GLEnum["COMPRESSED_RED_GREEN_RGTC2_EXT"] = 36285] = "COMPRESSED_RED_GREEN_RGTC2_EXT";
    GLEnum[GLEnum["COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT"] = 36286] = "COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT";
    // WEBGL_compressed_texture_bptc (BC6, BC7)
    GLEnum[GLEnum["COMPRESSED_RGBA_BPTC_UNORM_EXT"] = 36492] = "COMPRESSED_RGBA_BPTC_UNORM_EXT";
    GLEnum[GLEnum["COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT"] = 36493] = "COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT";
    GLEnum[GLEnum["COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT"] = 36494] = "COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT";
    GLEnum[GLEnum["COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT"] = 36495] = "COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT";
    // WEBGL_compressed_texture_es3
    /** One-channel (red) unsigned format compression. */
    GLEnum[GLEnum["COMPRESSED_R11_EAC"] = 37488] = "COMPRESSED_R11_EAC";
    /** One-channel (red) signed format compression. */
    GLEnum[GLEnum["COMPRESSED_SIGNED_R11_EAC"] = 37489] = "COMPRESSED_SIGNED_R11_EAC";
    /** Two-channel (red and green) unsigned format compression. */
    GLEnum[GLEnum["COMPRESSED_RG11_EAC"] = 37490] = "COMPRESSED_RG11_EAC";
    /** Two-channel (red and green) signed format compression. */
    GLEnum[GLEnum["COMPRESSED_SIGNED_RG11_EAC"] = 37491] = "COMPRESSED_SIGNED_RG11_EAC";
    /** Compresses RGB8 data with no alpha channel. */
    GLEnum[GLEnum["COMPRESSED_RGB8_ETC2"] = 37492] = "COMPRESSED_RGB8_ETC2";
    /** Compresses RGBA8 data. The RGB part is encoded the same as RGB_ETC2, but the alpha part is encoded separately. */
    GLEnum[GLEnum["COMPRESSED_RGBA8_ETC2_EAC"] = 37493] = "COMPRESSED_RGBA8_ETC2_EAC";
    /** Compresses sRGB8 data with no alpha channel. */
    GLEnum[GLEnum["COMPRESSED_SRGB8_ETC2"] = 37494] = "COMPRESSED_SRGB8_ETC2";
    /** Compresses sRGBA8 data. The sRGB part is encoded the same as SRGB_ETC2, but the alpha part is encoded separately. */
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ETC2_EAC"] = 37495] = "COMPRESSED_SRGB8_ALPHA8_ETC2_EAC";
    /** Similar to RGB8_ETC, but with ability to punch through the alpha channel, which means to make it completely opaque or transparent. */
    GLEnum[GLEnum["COMPRESSED_RGB8_PUNCHTHROUGH_ALPHA1_ETC2"] = 37496] = "COMPRESSED_RGB8_PUNCHTHROUGH_ALPHA1_ETC2";
    /** Similar to SRGB8_ETC, but with ability to punch through the alpha channel, which means to make it completely opaque or transparent. */
    GLEnum[GLEnum["COMPRESSED_SRGB8_PUNCHTHROUGH_ALPHA1_ETC2"] = 37497] = "COMPRESSED_SRGB8_PUNCHTHROUGH_ALPHA1_ETC2";
    // WEBGL_compressed_texture_pvrtc
    /** RGB compression in 4-bit mode. One block for each 4×4 pixels. */
    GLEnum[GLEnum["COMPRESSED_RGB_PVRTC_4BPPV1_IMG"] = 35840] = "COMPRESSED_RGB_PVRTC_4BPPV1_IMG";
    /** RGBA compression in 4-bit mode. One block for each 4×4 pixels. */
    GLEnum[GLEnum["COMPRESSED_RGBA_PVRTC_4BPPV1_IMG"] = 35842] = "COMPRESSED_RGBA_PVRTC_4BPPV1_IMG";
    /** RGB compression in 2-bit mode. One block for each 8×4 pixels. */
    GLEnum[GLEnum["COMPRESSED_RGB_PVRTC_2BPPV1_IMG"] = 35841] = "COMPRESSED_RGB_PVRTC_2BPPV1_IMG";
    /** RGBA compression in 2-bit mode. One block for each 8×4 pixels. */
    GLEnum[GLEnum["COMPRESSED_RGBA_PVRTC_2BPPV1_IMG"] = 35843] = "COMPRESSED_RGBA_PVRTC_2BPPV1_IMG";
    // WEBGL_compressed_texture_etc1
    /** Compresses 24-bit RGB data with no alpha channel. */
    GLEnum[GLEnum["COMPRESSED_RGB_ETC1_WEBGL"] = 36196] = "COMPRESSED_RGB_ETC1_WEBGL";
    // WEBGL_compressed_texture_atc
    GLEnum[GLEnum["COMPRESSED_RGB_ATC_WEBGL"] = 35986] = "COMPRESSED_RGB_ATC_WEBGL";
    GLEnum[GLEnum["COMPRESSED_RGBA_ATC_EXPLICIT_ALPHA_WEBGL"] = 35986] = "COMPRESSED_RGBA_ATC_EXPLICIT_ALPHA_WEBGL";
    GLEnum[GLEnum["COMPRESSED_RGBA_ATC_INTERPOLATED_ALPHA_WEBGL"] = 34798] = "COMPRESSED_RGBA_ATC_INTERPOLATED_ALPHA_WEBGL";
    // WEBGL_compressed_texture_astc
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_4x4_KHR"] = 37808] = "COMPRESSED_RGBA_ASTC_4x4_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_5x4_KHR"] = 37809] = "COMPRESSED_RGBA_ASTC_5x4_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_5x5_KHR"] = 37810] = "COMPRESSED_RGBA_ASTC_5x5_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_6x5_KHR"] = 37811] = "COMPRESSED_RGBA_ASTC_6x5_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_6x6_KHR"] = 37812] = "COMPRESSED_RGBA_ASTC_6x6_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_8x5_KHR"] = 37813] = "COMPRESSED_RGBA_ASTC_8x5_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_8x6_KHR"] = 37814] = "COMPRESSED_RGBA_ASTC_8x6_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_8x8_KHR"] = 37815] = "COMPRESSED_RGBA_ASTC_8x8_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_10x5_KHR"] = 37816] = "COMPRESSED_RGBA_ASTC_10x5_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_10x6_KHR"] = 37817] = "COMPRESSED_RGBA_ASTC_10x6_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_10x8_KHR"] = 37818] = "COMPRESSED_RGBA_ASTC_10x8_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_10x10_KHR"] = 37819] = "COMPRESSED_RGBA_ASTC_10x10_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_12x10_KHR"] = 37820] = "COMPRESSED_RGBA_ASTC_12x10_KHR";
    GLEnum[GLEnum["COMPRESSED_RGBA_ASTC_12x12_KHR"] = 37821] = "COMPRESSED_RGBA_ASTC_12x12_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR"] = 37840] = "COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR"] = 37841] = "COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR"] = 37842] = "COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR"] = 37843] = "COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR"] = 37844] = "COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR"] = 37845] = "COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR"] = 37846] = "COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR"] = 37847] = "COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR"] = 37848] = "COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR"] = 37849] = "COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR"] = 37850] = "COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR"] = 37851] = "COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR"] = 37852] = "COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR";
    GLEnum[GLEnum["COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR"] = 37853] = "COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR";
    // EXT_disjoint_timer_query
    /** The number of bits used to hold the query result for the given target. */
    GLEnum[GLEnum["QUERY_COUNTER_BITS_EXT"] = 34916] = "QUERY_COUNTER_BITS_EXT";
    /** The currently active query. */
    GLEnum[GLEnum["CURRENT_QUERY_EXT"] = 34917] = "CURRENT_QUERY_EXT";
    /** The query result. */
    GLEnum[GLEnum["QUERY_RESULT_EXT"] = 34918] = "QUERY_RESULT_EXT";
    /** A Boolean indicating whether or not a query result is available. */
    GLEnum[GLEnum["QUERY_RESULT_AVAILABLE_EXT"] = 34919] = "QUERY_RESULT_AVAILABLE_EXT";
    /** Elapsed time (in nanoseconds). */
    GLEnum[GLEnum["TIME_ELAPSED_EXT"] = 35007] = "TIME_ELAPSED_EXT";
    /** The current time. */
    GLEnum[GLEnum["TIMESTAMP_EXT"] = 36392] = "TIMESTAMP_EXT";
    /** A Boolean indicating whether or not the GPU performed any disjoint operation (lost context) */
    GLEnum[GLEnum["GPU_DISJOINT_EXT"] = 36795] = "GPU_DISJOINT_EXT";
    // KHR_parallel_shader_compile https://registry.khronos.org/webgl/extensions/KHR_parallel_shader_compile
    /** a non-blocking poll operation, so that compile/link status availability can be queried without potentially incurring stalls */
    GLEnum[GLEnum["COMPLETION_STATUS_KHR"] = 37297] = "COMPLETION_STATUS_KHR";
    // EXT_depth_clamp https://registry.khronos.org/webgl/extensions/EXT_depth_clamp/
    /** Disables depth clipping */
    GLEnum[GLEnum["DEPTH_CLAMP_EXT"] = 34383] = "DEPTH_CLAMP_EXT";
    // WEBGL_provoking_vertex https://registry.khronos.org/webgl/extensions/WEBGL_provoking_vertex/
    /** Values of first vertex in primitive are used for flat shading */
    GLEnum[GLEnum["FIRST_VERTEX_CONVENTION_WEBGL"] = 36429] = "FIRST_VERTEX_CONVENTION_WEBGL";
    /** Values of first vertex in primitive are used for flat shading */
    GLEnum[GLEnum["LAST_VERTEX_CONVENTION_WEBGL"] = 36430] = "LAST_VERTEX_CONVENTION_WEBGL";
    /** Controls which vertex in primitive is used for flat shading */
    GLEnum[GLEnum["PROVOKING_VERTEX_WEBL"] = 36431] = "PROVOKING_VERTEX_WEBL";
    // WEBGL_polygon_mode https://registry.khronos.org/webgl/extensions/WEBGL_polygon_mode/
    GLEnum[GLEnum["POLYGON_MODE_WEBGL"] = 2880] = "POLYGON_MODE_WEBGL";
    GLEnum[GLEnum["POLYGON_OFFSET_LINE_WEBGL"] = 10754] = "POLYGON_OFFSET_LINE_WEBGL";
    GLEnum[GLEnum["LINE_WEBGL"] = 6913] = "LINE_WEBGL";
    GLEnum[GLEnum["FILL_WEBGL"] = 6914] = "FILL_WEBGL";
    // WEBGL_clip_cull_distance https://registry.khronos.org/webgl/extensions/WEBGL_clip_cull_distance/
    /** Max clip distances */
    GLEnum[GLEnum["MAX_CLIP_DISTANCES_WEBGL"] = 3378] = "MAX_CLIP_DISTANCES_WEBGL";
    /** Max cull distances */
    GLEnum[GLEnum["MAX_CULL_DISTANCES_WEBGL"] = 33529] = "MAX_CULL_DISTANCES_WEBGL";
    /** Max clip and cull distances */
    GLEnum[GLEnum["MAX_COMBINED_CLIP_AND_CULL_DISTANCES_WEBGL"] = 33530] = "MAX_COMBINED_CLIP_AND_CULL_DISTANCES_WEBGL";
    /** Enable gl_ClipDistance[0] and gl_CullDistance[0] */
    GLEnum[GLEnum["CLIP_DISTANCE0_WEBGL"] = 12288] = "CLIP_DISTANCE0_WEBGL";
    /** Enable gl_ClipDistance[1] and gl_CullDistance[1] */
    GLEnum[GLEnum["CLIP_DISTANCE1_WEBGL"] = 12289] = "CLIP_DISTANCE1_WEBGL";
    /** Enable gl_ClipDistance[2] and gl_CullDistance[2] */
    GLEnum[GLEnum["CLIP_DISTANCE2_WEBGL"] = 12290] = "CLIP_DISTANCE2_WEBGL";
    /** Enable gl_ClipDistance[3] and gl_CullDistance[3] */
    GLEnum[GLEnum["CLIP_DISTANCE3_WEBGL"] = 12291] = "CLIP_DISTANCE3_WEBGL";
    /** Enable gl_ClipDistance[4] and gl_CullDistance[4] */
    GLEnum[GLEnum["CLIP_DISTANCE4_WEBGL"] = 12292] = "CLIP_DISTANCE4_WEBGL";
    /** Enable gl_ClipDistance[5] and gl_CullDistance[5] */
    GLEnum[GLEnum["CLIP_DISTANCE5_WEBGL"] = 12293] = "CLIP_DISTANCE5_WEBGL";
    /** Enable gl_ClipDistance[6] and gl_CullDistance[6] */
    GLEnum[GLEnum["CLIP_DISTANCE6_WEBGL"] = 12294] = "CLIP_DISTANCE6_WEBGL";
    /** Enable gl_ClipDistance[7] and gl_CullDistance[7] */
    GLEnum[GLEnum["CLIP_DISTANCE7_WEBGL"] = 12295] = "CLIP_DISTANCE7_WEBGL";
    /** EXT_polygon_offset_clamp https://registry.khronos.org/webgl/extensions/EXT_polygon_offset_clamp/ */
    GLEnum[GLEnum["POLYGON_OFFSET_CLAMP_EXT"] = 36379] = "POLYGON_OFFSET_CLAMP_EXT";
    /** EXT_clip_control https://registry.khronos.org/webgl/extensions/EXT_clip_control/ */
    GLEnum[GLEnum["LOWER_LEFT_EXT"] = 36001] = "LOWER_LEFT_EXT";
    GLEnum[GLEnum["UPPER_LEFT_EXT"] = 36002] = "UPPER_LEFT_EXT";
    GLEnum[GLEnum["NEGATIVE_ONE_TO_ONE_EXT"] = 37726] = "NEGATIVE_ONE_TO_ONE_EXT";
    GLEnum[GLEnum["ZERO_TO_ONE_EXT"] = 37727] = "ZERO_TO_ONE_EXT";
    GLEnum[GLEnum["CLIP_ORIGIN_EXT"] = 37724] = "CLIP_ORIGIN_EXT";
    GLEnum[GLEnum["CLIP_DEPTH_MODE_EXT"] = 37725] = "CLIP_DEPTH_MODE_EXT";
    /** WEBGL_blend_func_extended https://registry.khronos.org/webgl/extensions/WEBGL_blend_func_extended/ */
    GLEnum[GLEnum["SRC1_COLOR_WEBGL"] = 35065] = "SRC1_COLOR_WEBGL";
    GLEnum[GLEnum["SRC1_ALPHA_WEBGL"] = 34185] = "SRC1_ALPHA_WEBGL";
    GLEnum[GLEnum["ONE_MINUS_SRC1_COLOR_WEBGL"] = 35066] = "ONE_MINUS_SRC1_COLOR_WEBGL";
    GLEnum[GLEnum["ONE_MINUS_SRC1_ALPHA_WEBGL"] = 35067] = "ONE_MINUS_SRC1_ALPHA_WEBGL";
    GLEnum[GLEnum["MAX_DUAL_SOURCE_DRAW_BUFFERS_WEBGL"] = 35068] = "MAX_DUAL_SOURCE_DRAW_BUFFERS_WEBGL";
    /** EXT_texture_mirror_clamp_to_edge https://registry.khronos.org/webgl/extensions/EXT_texture_mirror_clamp_to_edge/ */
    GLEnum[GLEnum["MIRROR_CLAMP_TO_EDGE_EXT"] = 34627] = "MIRROR_CLAMP_TO_EDGE_EXT";
})(GLEnum || (GLEnum = {}));
export { GLEnum as GL };
//# sourceMappingURL=lumagl.js.map