#pragma BHQGLSL_REQUIRE(space)
#ifndef USE_GPU_SHADER_CREATE_INFO
in mat4 v_Data[];
uniform mat4 ModelViewProjectionMatrix;
uniform float u_Scale;
out flat int g_ID;
#endif
void main() {
int camera_index = int(v_Data[0][3][2]);
g_ID = camera_index - CAMERA_SELECT_OFFSET;
vec3 origin;
mat3 rotation;
vec2 aspect;
float lens;
unpack_camera_data(origin, rotation, lens, aspect, v_Data[0]);
mat4 packed_coo;
for (int i = 0; i < 4; ++i) {
eval_vertex_clip_space(packed_coo[i],
origin + (rotation * vec3(N_RECT_COO[i] * aspect, -lens) * u_Scale),
ModelViewProjectionMatrix);
gl_Position = packed_coo[i];
EmitVertex();
}
EndPrimitive();
}