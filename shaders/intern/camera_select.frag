#pragma BHQGLSL_REQUIRE(mask_fragment_stage)
#ifndef USE_GPU_SHADER_CREATE_INFO
in flat int g_ID;
uniform vec2 u_DepthMapMetrics;
uniform sampler2D u_DepthMap;
out int f_Color;
#endif
void main() {
if (frag_depth_greater_biased(u_DepthMap, u_DepthMapMetrics)) {
discard;
}
f_Color = g_ID;
}