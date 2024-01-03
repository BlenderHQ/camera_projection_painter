#pragma BHQGLSL_REQUIRE(space, tiles, sampler_map, mask_vertex_stage)
#ifndef USE_GPU_SHADER_CREATE_INFO
in mat4 v_Data[];
uniform mat4 ModelViewProjectionMatrix;
uniform vec4 u_ViewportMetrics;
uniform bool u_ShowActiveCamera;
layout(binding = 0, std140) uniform u_Params { CameraCommonParams _u_Params; };
uniform sampler2D u_TileMapping;
out vec4 g_Segment0;
out vec4 g_Segment1;
out vec2 g_AtlasUV;
out flat int g_IsTriangle;
#endif
void main() {
int camera_index = int(v_Data[0][3][2]);
bool is_active_camera = ((camera_index == _u_Params.index_active) ? true : false);
int preview_tile_index;
vec3 origin;
mat3 rotation;
vec2 aspect;
float lens;
if (is_active_camera) {
unpack_camera_data(origin, rotation, lens, aspect, _u_Params.data);
preview_tile_index = int(_u_Params.data[3][3]);
} else {
unpack_camera_data(origin, rotation, lens, aspect, v_Data[0]);
preview_tile_index = int(v_Data[0][3][3]);
}
if (bool(_u_Params.cage_flags & CAGE_USE) && bool(_u_Params.cage_flags & CAGE_USE_CAMERAS) &&
!inside_box(origin, _u_Params.cage_matrix)) {
return;
}
if (is_active_camera) {
g_IsTriangle = 1;
draw_frame_tri(origin, rotation, lens, aspect, _u_Params.scale, ModelViewProjectionMatrix);
}
if ((u_ShowActiveCamera || !is_active_camera) && preview_tile_index != -1) {
vec2 half_res = u_ViewportMetrics.zw * 0.5;
mat4 packed_coo;
vec2 screen_coo[4];
eval_frame_clip_screen_space(
packed_coo, screen_coo, origin, rotation, half_res, lens, aspect, _u_Params.scale, ModelViewProjectionMatrix);
g_IsTriangle = 0;
g_Segment0 = vec4(screen_coo[0], screen_coo[1]);
g_Segment1 = vec4(screen_coo[3], screen_coo[2]);
int index = find_value_index(preview_tile_index, u_TileMapping);
if (index == -1) {
return;
}
for (int i = 0; i < 4; ++i) {
gl_Position = packed_coo[i];
eval_tile_uv(g_AtlasUV, index, N_RECT_COO[i] + 0.5, aspect);
EmitVertex();
}
}
EndPrimitive();
}