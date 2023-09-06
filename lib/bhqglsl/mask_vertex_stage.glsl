void vert_stage_prepare_rounded_rectangle(out vec4 center_half_size, in vec4 transform) {
vec2 half_size = transform.zw * 0.5;
center_half_size = vec4(transform.xy + half_size, half_size);
}