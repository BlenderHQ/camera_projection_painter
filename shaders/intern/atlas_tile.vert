#pragma BHQGLSL_REQUIRE(tiles, mask_vertex_stage)
void main() {
vert_stage_prepare_rounded_rectangle(v_CenterHalfSize, u_Params.transform);
vec2 P_norm = P - 0.5;
gl_Position = ModelViewProjectionMatrix * vec4(P * u_Params.transform.zw + u_Params.transform.xy, 1.0, 1.0);
int index = find_value_index(u_Params.tile_index, u_TileMapping);
if (index != -1) {
eval_tile_uv(v_AtlasUV, index, P, u_Params.aspect);
} else {
v_AtlasUV = vec2(0.0);
}
}