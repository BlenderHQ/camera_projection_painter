#pragma BHQGLSL_REQUIRE(space)
#ifndef USE_GPU_SHADER_CREATE_INFO
in mat4 v_Data[];
layout(binding = 0, std140) uniform u_Params { CameraCommonParams _u_Params; };
uniform mat4 ModelViewProjectionMatrix;
uniform vec4 u_ViewportMetrics;
out vec4 g_Segment;
out flat int g_Flags;
#endif
void segment_primitive(in vec4 p0, in vec2 sp0, in vec4 p1, in vec2 sp1) {
g_Segment = vec4(sp0, sp1);
gl_Position = p0;
EmitVertex();
gl_Position = p1;
EmitVertex();
EndPrimitive();
}
void main() {
int camera_index = int(v_Data[0][3][2]);
bool is_active_camera = ((camera_index == _u_Params.index_active) ? true : false);
g_Flags = 0;
if (is_active_camera) {
g_Flags |= CAMERA_WIRES_FLAG_ACTIVE;
}
if (!is_active_camera && _u_Params.index_hover == camera_index) {
g_Flags |= CAMERA_WIRES_FLAG_HOVER;
}
vec3 origin;
mat3 rotation;
vec2 aspect;
float lens;
if (is_active_camera) {
unpack_camera_data(origin, rotation, lens, aspect, _u_Params.data);
} else {
unpack_camera_data(origin, rotation, lens, aspect, v_Data[0]);
if (_u_Params.highlight_orientation) {
if (v_Data[0][3][1] < 1.0) {
g_Flags |= CAMERA_WIRES_FLAG_PORTRAIT;
} else if (v_Data[0][3][1] > 1.0) {
g_Flags |= CAMERA_WIRES_FLAG_LANDSCAPE;
}
}
}
vec2 half_res = u_ViewportMetrics.zw * 0.5;
mat4 packed_coo;
vec2 screen_coo[4];
eval_frame_clip_screen_space(
packed_coo, screen_coo, origin, rotation, half_res, lens, aspect, _u_Params.scale, ModelViewProjectionMatrix);
vec4 tri_packed_coo[3];
vec2 tri_screen_coo[3];
eval_frame_tri_clip_screen_space(tri_packed_coo,
tri_screen_coo,
origin,
rotation,
half_res,
lens,
aspect,
_u_Params.scale,
ModelViewProjectionMatrix);
vec4 center;
vec2 center_screen;
eval_vertex_clip_space(center, origin, ModelViewProjectionMatrix);
eval_vertex_screen_space(center_screen, center, half_res);
segment_primitive(center, center_screen, packed_coo[0], screen_coo[0]);
segment_primitive(center, center_screen, packed_coo[1], screen_coo[1]);
segment_primitive(center, center_screen, packed_coo[2], screen_coo[2]);
segment_primitive(center, center_screen, packed_coo[3], screen_coo[3]);
segment_primitive(packed_coo[0], screen_coo[0], packed_coo[1], screen_coo[1]);
segment_primitive(packed_coo[1], screen_coo[1], packed_coo[3], screen_coo[3]);
segment_primitive(packed_coo[3], screen_coo[3], packed_coo[2], screen_coo[2]);
segment_primitive(packed_coo[2], screen_coo[2], packed_coo[0], screen_coo[0]);
segment_primitive(tri_packed_coo[0], tri_screen_coo[0], tri_packed_coo[1], tri_screen_coo[1]);
segment_primitive(tri_packed_coo[1], tri_screen_coo[1], tri_packed_coo[2], tri_screen_coo[2]);
segment_primitive(tri_packed_coo[0], tri_screen_coo[0], tri_packed_coo[2], tri_screen_coo[2]);
}