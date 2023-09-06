vec4 srgb_to_linear(vec4 color) {
vec3 c = max(color.rgb, vec3(0.0));
vec3 c1 = c * (1.0 / 12.92);
vec3 c2 = pow((c + 0.055) * (1.0 / 1.055), vec3(2.4));
color.rgb = mix(c1, c2, step(vec3(0.04045), c));
return color;
}
vec4 premultiplied_alpha_blend(vec4 src, vec4 dst) {
float final_alpha = src.a + dst.a * (1.0 - src.a);
return vec4((src.rgb * src.a + dst.rgb * dst.a * (1.0 - src.a)) / final_alpha, final_alpha);
}