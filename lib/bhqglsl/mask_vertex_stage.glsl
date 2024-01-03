void vert_stage_prepare_rounded_rectangle(out vec4 center_half_size, in vec4 transform) {
vec2 half_size = transform.zw * 0.5;
center_half_size = vec4(transform.xy + half_size, half_size);
}
bool inside_box(vec3 coo, mat4 M) {
vec4 local_coo = inverse(M) * vec4(coo, 1.0);
return all(lessThanEqual(vec3(-0.5), local_coo.xyz)) && all(lessThanEqual(local_coo.xyz, vec3(0.5)));
}