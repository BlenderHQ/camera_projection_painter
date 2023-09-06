#pragma BHQGLSL_REQUIRE(constants, colorspace, dithering)
#ifndef USE_GPU_SHADER_CREATE_INFO
in vec4 g_Segment0;
in vec4 g_Segment1;
in vec2 g_AtlasUV;
in flat int g_IsTriangle;
layout(binding = 0, std140) uniform u_Dithering { DitheringParams _u_Dithering; };
layout(binding = 1, std140) uniform u_Params { CameraCommonParams _u_Params; };
uniform sampler2D u_Atlas;
uniform sampler2D u_Image;
out vec4 f_Color;
#endif
void main() {
if (g_IsTriangle == 1) {
f_Color = vec4(_u_Params.color_active.rgb, 1.0);
} else {
f_Color = texture(u_Atlas, g_AtlasUV);
if (_u_Dithering.use) {
f_Color = mix(f_Color, bayer_dither8x8(f_Color), _u_Dithering.mix_factor);
}
vec2 fcoo = gl_FragCoord.xy;
vec2 p0 = g_Segment0.xy;
vec2 p1 = g_Segment0.zw;
vec2 p2 = g_Segment1.xy;
vec2 p3 = g_Segment1.zw;
vec2 s01 = p1 - p0;
vec2 s21 = p2 - p1;
vec2 s32 = p3 - p2;
vec2 s30 = p3 - p0;
vec2 sm0 = fcoo - p0;
vec2 sm1 = fcoo - p1;
vec2 sm2 = fcoo - p2;
f_Color.a *= _u_Params.transparency *
smoothstep(0.0, _u_Params.line_thickness, length(sm0 - s01 * dot(s01, sm0) / dot(s01, s01))) *
smoothstep(0.0, _u_Params.line_thickness, length(sm1 - s21 * dot(s21, sm1) / dot(s21, s21))) *
smoothstep(0.0, _u_Params.line_thickness, length(sm2 - s32 * dot(s32, sm2) / dot(s32, s32))) *
smoothstep(0.0, _u_Params.line_thickness, length(sm0 - s30 * dot(s30, sm0) / dot(s30, s30)));
}
if (f_Color.a < BHQGLSL_EXP) {
discard;
}
f_Color.a = clamp(f_Color.a, 0.0, BHQGLSL_ONEMINEXP);
f_Color = srgb_to_linear(f_Color);
}