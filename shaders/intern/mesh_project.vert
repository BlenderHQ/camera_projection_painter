#pragma BHQGLSL_REQUIRE(constants, lens_distortion)
void main() {
if (u_MeshProjectParams.use_uniforms) {
if (u_MeshProjectParams.highlight_border_type == BORDERTYPE_NONE) {
uv_project(v_ProjectedDistortedUV, P, u_UVProjectParams.camera_matrix);
} else {
uv_project_keep_depth(v_ProjectedUV, P, u_UVProjectParams.camera_matrix);
v_ProjectedDistortedUV = v_ProjectedUV.xy;
}
uv_distort(v_ProjectedDistortedUV);
} else {
if (u_MeshProjectParams.highlight_border_type != BORDERTYPE_NONE) {
uv_project_keep_depth(v_ProjectedUV, P, u_UVProjectParams.camera_matrix);
}
vec2 tex_coo = uv_project_texture_coo(int(ID / 2), u_UVProjectParams.uv_texture_resolution);
if (ID % 2 == 0) {
v_ProjectedDistortedUV = texture(u_UVProjectTexture, tex_coo).xy;
} else {
v_ProjectedDistortedUV = texture(u_UVProjectTexture, tex_coo).zw;
}
}
gl_Position = ModelViewProjectionMatrix * u_MeshProjectParams.model_matrix * vec4(P, 1.0);
gl_Position.w += BHQGLSL_EXP;
}