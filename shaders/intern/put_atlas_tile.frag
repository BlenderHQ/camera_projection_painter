#pragma BHQGLSL_REQUIRE(fxaa_lib)
void main() {
if (u_UseFXAA) {
f_Color = FxaaPixelShader(v_UV, u_Preview, vec2(1.0 / 128.0), 1.0, 0.063, 0.0312);
} else {
f_Color = texture(u_Preview, v_UV);
}
}