#pragma BHQGLSL_REQUIRE(lens_distortion)
void main() {
vec2 distortedUV = v_UV;
uv_distort(distortedUV);
f_Color = texture(u_Image, distortedUV);
vec4 p0 = vec4(smoothstep(vec2(0.0), u_ViewportMetrics.xy, distortedUV),
smoothstep(vec2(0.0), u_ViewportMetrics.xy, 1.0 - distortedUV));
float maskValue = p0.x * p0.y * p0.z * p0.w;
f_Color.a *= u_Opacity * maskValue;
}