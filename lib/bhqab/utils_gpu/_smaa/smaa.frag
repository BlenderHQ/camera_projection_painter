void main() {
#if SMAA_STAGE == 0
vec4 offset[3];
out_edges = SMAAColorEdgeDetectionPS(v_pos, v_offset, colorTex);
#elif SMAA_STAGE == 1
out_weights = SMAABlendingWeightCalculationPS(v_pos, v_pixcoord, v_offset, edgesTex, areaTex, searchTex, vec4(0.0));
#elif SMAA_STAGE == 2
out_color = SMAANeighborhoodBlendingPS(v_pos, v_offset[0], colorTex, blendTex);
#endif
}