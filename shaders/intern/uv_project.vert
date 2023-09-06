#ifndef USE_GPU_SHADER_CREATE_INFO
in vec3 P;
#endif
void main() { gl_Position = vec4(P, 1.0); }