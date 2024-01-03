void main() {
v_pos = UV;
gl_Position = vec4(P, 1.0, 1.0);
#if SMAA_STAGE == 0
SMAAEdgeDetectionVS(v_pos, v_offset);
#elif SMAA_STAGE == 1
SMAABlendingWeightCalculationVS(v_pos, v_pixcoord, v_offset);
#elif SMAA_STAGE == 2
SMAANeighborhoodBlendingVS(v_pos, v_offset[0]);
#endif
}