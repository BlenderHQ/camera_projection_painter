#ifndef USE_GPU_SHADER_CREATE_INFO
in vec4 g_ProjectedDistortedUV;
out vec4 f_Color;
#endif
void main() { f_Color = g_ProjectedDistortedUV; }