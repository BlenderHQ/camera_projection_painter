#pragma BHQGLSL_REQUIRE(constants, colorspace)
#ifndef USE_GPU_SHADER_CREATE_INFO
in vec4 g_Segment;
in flat int g_Flags;
layout(binding = 0, std140) uniform u_Params { CameraCommonParams _u_Params; };
out vec4 f_Color;
#endif
void main() {
vec2 p0 = g_Segment.xy;
vec2 p1 = g_Segment.zw;
vec2 s01 = p1 - p0;
vec2 sm0 = gl_FragCoord.xy - p1;
vec3 rgb_color;
if (bool(g_Flags & CAMERA_WIRES_FLAG_ACTIVE) || bool(g_Flags & CAMERA_WIRES_FLAG_HOVER)) {
rgb_color = _u_Params.color_active.rgb;
} else if (_u_Params.highlight_orientation) {
if (bool(g_Flags & CAMERA_WIRES_FLAG_PORTRAIT)) {
rgb_color = _u_Params.color_portrait.rgb;
} else if (bool(g_Flags & CAMERA_WIRES_FLAG_LANDSCAPE)) {
rgb_color = _u_Params.color_landscape.rgb;
}
} else {
rgb_color = _u_Params.color.rgb;
}
f_Color.rgb = rgb_color;
f_Color.a = _u_Params.transparency *
smoothstep(_u_Params.line_thickness, 0.0, length(sm0 - s01 * dot(s01, sm0) / dot(s01, s01)));
if (f_Color.a < BHQGLSL_EXP) {
discard;
}
f_Color.a = clamp(f_Color.a, 0.0, BHQGLSL_ONEMINEXP);
f_Color = srgb_to_linear(f_Color);
}