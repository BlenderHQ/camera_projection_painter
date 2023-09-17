#pragma BHQGLSL_REQUIRE(mask_fragment_stage, colorspace)
void main() {
if (frag_depth_greater_biased(u_DepthTexture, u_ViewportMetrics.zw)) {
discard;
}
float brush_mask = 0.0;
float dist = distance(u_BrushPos, gl_FragCoord.xy);
bool is_brush_inner = (dist > u_MeshProjectParams.brush_radius) ? false : true;
if (u_MeshProjectParams.highlight_border_type == BORDERTYPE_NONE && !is_brush_inner) {
discard;
}
brush_mask = (is_brush_inner ? texture(u_BrushMask, (dist / u_MeshProjectParams.brush_radius)).r : 0.0);
f_Color = texture(u_Image, v_ProjectedDistortedUV.xy);
f_Color.a *= brush_mask;
const bool border_facing = (bool(u_MeshProjectParams.highlight_border_facing & FACING_FRONT &
u_MeshProjectParams.highlight_border_facing & FACING_BACK)
? true
: gl_FrontFacing ? bool(u_MeshProjectParams.highlight_border_facing & FACING_FRONT)
: bool(u_MeshProjectParams.highlight_border_facing & FACING_BACK));
if (border_facing && u_MeshProjectParams.highlight_border_type != BORDERTYPE_NONE &&
!(mask_rectangle(v_ProjectedUV.xy, vec2(-0.5), vec2(0.5)) && v_ProjectedUV.z > 0.0)) {
float pattern_mask = 1.0;
if (u_MeshProjectParams.highlight_border_type == BORDERTYPE_CHECKER) {
checker_pattern(pattern_mask, 0.15);
} else if (u_MeshProjectParams.highlight_border_type == BORDERTYPE_LINES) {
lines_pattern(pattern_mask, 0.15);
}
vec4 border_gradient = mix(u_MeshProjectParams.highlight_border_color0,
u_MeshProjectParams.highlight_border_color1,
gl_FragCoord.x * u_ViewportMetrics.x);
border_gradient.a *= pattern_mask * (1.0 - brush_mask);
f_Color = premultiplied_alpha_blend(f_Color, border_gradient);
}
}