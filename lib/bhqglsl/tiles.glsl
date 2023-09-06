#pragma BHQGLSL_REQUIRE(constants)
int find_value_index(in const int value, in sampler2D index_mapping) {
int index = -1;
vec2 size = textureSize(index_mapping, 0);
vec2 st = 1.0 / size;
for (float V = st.y * 0.5; V < 1.0; V += st.y) {
for (float U = st.x * 0.5; U < 1.0; U += st.x) {
index += 1;
if (int(texture(index_mapping, vec2(U, V)).r) == value) {
return index;
}
}
}
return -1;
}
void eval_tile_uv(out vec2 r_UV, in const int index, in const vec2 pos, in const vec2 aspect) {
const vec2 offset = vec2((index % PRV_ATLAS_SIDE_TILES), (index / PRV_ATLAS_SIDE_TILES));
r_UV = (((pos - 0.5) * aspect + 0.5) + offset) / PRV_ATLAS_SIDE_TILES;
}