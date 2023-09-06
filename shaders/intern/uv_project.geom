#pragma BHQGLSL_REQUIRE(lens_distortion)
#ifndef USE_GPU_SHADER_CREATE_INFO
layout(binding = 1, std140) uniform u_UVProjectParams { UVProjectParams _u_UVProjectParams; };
out vec4 g_ProjectedDistortedUV;
#endif
void main() {
uv_project(g_ProjectedDistortedUV.xy, gl_in[0].gl_Position.xyz, _u_UVProjectParams.camera_matrix);
uv_distort(g_ProjectedDistortedUV.xy);
uv_project(g_ProjectedDistortedUV.zw, gl_in[1].gl_Position.xyz, _u_UVProjectParams.camera_matrix);
uv_distort(g_ProjectedDistortedUV.zw);
vec2 pos = (0.5 + vec2(gl_PrimitiveIDIn % _u_UVProjectParams.uv_texture_resolution,
gl_PrimitiveIDIn / _u_UVProjectParams.uv_texture_resolution)) /
_u_UVProjectParams.uv_texture_resolution;
gl_Position = vec4(2.0 * pos - 1.0, 0.0, 1.0);
EmitVertex();
EndPrimitive();
}