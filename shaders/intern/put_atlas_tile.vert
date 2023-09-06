const float PRV_HALF_TILE_SIDE = 2.0 / PRV_ATLAS_SIDE_TILES;
void main() {
v_UV = P;
gl_Position = vec4(P * PRV_HALF_TILE_SIDE - 1.0 +
vec2(PRV_HALF_TILE_SIDE * (u_Index % PRV_ATLAS_SIDE_TILES),
PRV_HALF_TILE_SIDE * (u_Index / PRV_ATLAS_SIDE_TILES)),
0.0,
1.0);
}