#pragma BHQGLSL_REQUIRE(constants, mask_fragment_stage, colorspace)
void main() {
f_Color = v_Color;
rounded_rectangle_outlined(
f_Color, u_Params.outline_color, v_CenterHalfSize, u_Params.roundness, u_Params.outline_thickness);
f_Color = srgb_to_linear(f_Color);
}