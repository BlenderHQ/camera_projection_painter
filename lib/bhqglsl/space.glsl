#pragma BHQGLSL_REQUIRE(constants)
const lowp vec2 N_RECT_COO[4] = vec2[4](vec2(-BHQGLSL_CAMERA_FRAME_HALF_SIZE, -BHQGLSL_CAMERA_FRAME_HALF_SIZE),
vec2(-BHQGLSL_CAMERA_FRAME_HALF_SIZE, BHQGLSL_CAMERA_FRAME_HALF_SIZE),
vec2(BHQGLSL_CAMERA_FRAME_HALF_SIZE, -BHQGLSL_CAMERA_FRAME_HALF_SIZE),
vec2(BHQGLSL_CAMERA_FRAME_HALF_SIZE, BHQGLSL_CAMERA_FRAME_HALF_SIZE));
void unpack_camera_data(out vec3 r_origin, out mat3 r_rotation, out float r_lens, out vec2 r_aspect, in mat4 data) {
r_origin = vec3(data[0].w, data[1].w, data[2].w);
r_rotation = mat3(data);
r_lens = data[3][0];
float asp = data[3][1];
if (asp == 1.0) {
r_aspect = vec2(1.0, 1.0);
}
else if (asp > 1.0) {
r_aspect = vec2(1.0, asp - 1.0);
}
else {
r_aspect = vec2(asp, 1.0);
}
}
void eval_vertex_clip_space(out vec4 r_pos, in vec3 pos, in mat4 MVP) { r_pos = MVP * vec4(pos, 1.0); }
void eval_vertex_screen_space(out vec2 r_coo, in vec4 pos, in vec2 half_res) {
r_coo = (1.0 + (pos.xy / pos.w)) * half_res;
}
void eval_frame_clip_screen_space(out mat4 r_packed_coo,
out vec2[4] r_ndc_coo,
in vec3 origin,
in mat3 rotation,
in vec2 half_res,
in float lens,
in vec2 aspect,
in float scale,
in mat4 MVP) {
for (int i = 0; i < 4; ++i) {
eval_vertex_clip_space(r_packed_coo[i], origin + (rotation * vec3(N_RECT_COO[i] * aspect, -lens)) * scale, MVP);
eval_vertex_screen_space(r_ndc_coo[i], r_packed_coo[i], half_res);
}
}
void eval_frame_tri_clip_screen_space(out vec4[3] r_packed_coo,
out vec2[3] r_ndc_coo,
in vec3 origin,
in mat3 rotation,
in vec2 half_res,
in float lens,
in vec2 aspect,
in float scale,
in mat4 MVP) {
float y_coordinate = (BHQGLSL_CAMERA_FRAME_HALF_SIZE * aspect.y) + BHQGLSL_CAMERA_UP_TRI_OFFSET;
eval_vertex_clip_space(
r_packed_coo[0], origin + (rotation * vec3(-BHQGLSL_CAMERA_UP_TRI_SIZE, y_coordinate, -lens) * scale), MVP);
eval_vertex_screen_space(r_ndc_coo[0], r_packed_coo[0], half_res);
eval_vertex_clip_space(
r_packed_coo[1], origin + (rotation * vec3(0.0, y_coordinate + BHQGLSL_CAMERA_UP_TRI_SIZE, -lens)) * scale, MVP);
eval_vertex_screen_space(r_ndc_coo[1], r_packed_coo[1], half_res);
eval_vertex_clip_space(
r_packed_coo[2], origin + (rotation * vec3(BHQGLSL_CAMERA_UP_TRI_SIZE, y_coordinate, -lens)) * scale, MVP);
eval_vertex_screen_space(r_ndc_coo[2], r_packed_coo[2], half_res);
}
void draw_frame_tri(in vec3 origin, in mat3 rotation, in float lens, in vec2 aspect, in float scale, in mat4 MVP) {
float y_coordinate = (0.5 * aspect.y) + BHQGLSL_CAMERA_UP_TRI_OFFSET;
eval_vertex_clip_space(
gl_Position, origin + (rotation * vec3(-BHQGLSL_CAMERA_UP_TRI_SIZE, y_coordinate, -lens) * scale), MVP);
EmitVertex();
eval_vertex_clip_space(
gl_Position, origin + (rotation * vec3(0.0, y_coordinate + BHQGLSL_CAMERA_UP_TRI_SIZE, -lens) * scale), MVP);
EmitVertex();
eval_vertex_clip_space(
gl_Position, origin + (rotation * vec3(BHQGLSL_CAMERA_UP_TRI_SIZE, y_coordinate, -lens) * scale), MVP);
EmitVertex();
EndPrimitive();
}