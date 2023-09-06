#pragma BHQGLSL_REQUIRE(mask_vertex_stage)
void main() {
vert_stage_prepare_rounded_rectangle(v_CenterHalfSize, u_Params.transform);
v_Color = u_Params.color;
if (u_Params.show_shaded) {
if (gl_VertexID == 1 || gl_VertexID == 2) {
v_Color.rgb += u_Params.shade_top_bottom.x;
} else {
v_Color.rgb += u_Params.shade_top_bottom.y;
}
}
v_Color = clamp(v_Color, 0.0, 1.0);
gl_Position = ModelViewProjectionMatrix * vec4(P * u_Params.transform.zw + u_Params.transform.xy, 0.0, 1.0);
}