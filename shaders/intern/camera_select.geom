#pragma BHQGLSL_REQUIRE(space, mask_vertex_stage)
#ifndef USE_GPU_SHADER_CREATE_INFO
in mat4 v_Data[];
uniform mat4 ModelViewProjectionMatrix;
uniform bool u_ShowActiveCamera;
layout(binding = 0, std140) uniform u_Params { CameraCommonParams _u_Params; };
out flat int g_ID;
#endif
void main() {
int camera_index = int(v_Data[0][3][2]);
if (u_ShowActiveCamera || camera_index != _u_Params.index_active) {
g_ID = camera_index - CAMERA_SELECT_OFFSET;
vec3 origin;
mat3 rotation;
vec2 aspect;
float lens;
unpack_camera_data(origin, rotation, lens, aspect, v_Data[0]);
if (bool(_u_Params.cage_flags & CAGE_USE) && bool(_u_Params.cage_flags & CAGE_USE_CAMERAS) &&
!inside_box(origin, _u_Params.cage_matrix)) {
return;
}
vec4 center;
eval_vertex_clip_space(center, origin, ModelViewProjectionMatrix);
mat4 packed_coo;
for (int i = 0; i < 4; ++i) {
eval_vertex_clip_space(packed_coo[i],
origin + (rotation * vec3(N_RECT_COO[i] * aspect, -lens) * _u_Params.scale),
ModelViewProjectionMatrix);
gl_Position = packed_coo[i];
EmitVertex();
}
EndPrimitive();
gl_Position = center;
EmitVertex();
gl_Position = packed_coo[0];
EmitVertex();
gl_Position = packed_coo[3];
EmitVertex();
EndPrimitive();
gl_Position = center;
EmitVertex();
gl_Position = packed_coo[1];
EmitVertex();
gl_Position = packed_coo[2];
EmitVertex();
EndPrimitive();
draw_frame_tri(origin, rotation, lens, aspect, _u_Params.scale, ModelViewProjectionMatrix);
}
}