#pragma BHQGLSL_REQUIRE(mask_fragment_stage, colorspace, dithering)
void main() {
f_Color = srgb_to_linear(texture(u_Atlas, v_AtlasUV));
if (_u_Dithering.use) {
f_Color = mix(f_Color, bayer_dither8x8(f_Color), u_Dithering.mix_factor);
}
rounded_rectangle_outlined(f_Color,
srgb_to_linear(u_Params.outline_color),
v_CenterHalfSize,
u_Params.roundness,
u_Params.outline_thickness);
}