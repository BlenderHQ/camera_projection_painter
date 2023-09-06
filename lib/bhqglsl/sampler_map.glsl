bool contains_value(in const int value, in sampler1D array) {
const int num = textureSize(array, 0);
const float st = 1.0 / float(num);
for (float U = st * 0.5; U < 1.0; U += st) {
if (int(texture(array, U).r) == value) {
return true;
}
}
return false;
}