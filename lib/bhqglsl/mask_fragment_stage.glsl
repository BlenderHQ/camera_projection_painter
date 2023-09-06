#pragma BHQGLSL_REQUIRE(constants)
bool mask_rectangle(vec2 coo, vec2 bottom_left, vec2 top_right) {
vec2 st = step(bottom_left, coo) - step(top_right, coo);
return (st.x * st.y == 0.0) ? false : true;
}
float mask_rounded_rectangle(vec2 center, vec2 size, float radius) {
return smoothstep(-1.0, 1.0, length(max(abs(center) - size + radius, 0.0)) - radius);
}
void rounded_rectangle_outlined(inout vec4 color_inner,
in vec4 color_outline,
in vec4 center_half_size,
in float roundness,
float outline_thickness) {
float radius = BHQGLSL_OUTLINE_RADIUS_MIN + BHQGLSL_OUTLINE_RADIUS_MAX * roundness;
vec2 pos = center_half_size.xy - gl_FragCoord.xy;
float mask_inner = 1.0 - mask_rounded_rectangle(pos, center_half_size.zw, radius);
float mask_outline =
1.0 - mask_rounded_rectangle(pos, center_half_size.zw - vec2(outline_thickness), radius - outline_thickness);
color_inner = mix(color_outline, color_inner, mask_outline);
color_inner.a *= mask_inner;
}
bool frag_depth_greater_biased(in sampler2D depth_map, in vec2 view_resolution) {
return (gl_FragCoord.z > texture(depth_map, vec2(gl_FragCoord.xy / view_resolution)).r + 1e-6);
}
void rotate_2d(inout vec2 st, float angle) {
float cosang = cos(angle), sinang = sin(angle);
st = (mat2(cosang, -sinang, sinang, cosang) * st - 0.5) + 0.5;
}
void lines_pattern(out float pattern, in float scale) {
vec2 coo = gl_FragCoord.xy;
rotate_2d(coo, BHQGLSL_PI * -0.25);
pattern = clamp(mod(floor(scale * coo.x),  2.0), 0.0, 1.0);
}
void checker_pattern(out float pattern, in float scale) {
pattern = clamp(
mod(floor(scale * gl_FragCoord.x) + floor(scale * gl_FragCoord.y),  2.0), 0.0, 1.0);
}