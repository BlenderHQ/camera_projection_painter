#ifndef DISTORTIONMODEL_NONE
#error "DISTORTIONMODEL_NONE" must be defined before linking
#endif
#ifndef DISTORTIONMODEL_DIVISION
#error "DISTORTIONMODEL_DIVISION" must be defined before linking
#endif
#ifndef DISTORTIONMODEL_POLYNOMIAL
#error "DISTORTIONMODEL_POLYNOMIAL" must be defined before linking
#endif
#ifndef DISTORTIONMODEL_BROWN
#error "DISTORTIONMODEL_BROWN" must be defined before linking
#endif
#ifndef USE_GPU_SHADER_CREATE_INFO
layout(binding = 0, std140) uniform u_Intrinsics { IntrinsicsPixelCoo _u_Intrinsics; };
#endif
vec2 uv_project_texture_coo(in const int index, in const int res) {
return (vec2(index % res, index / res) + 0.5) / res;
}
void uv_project(out vec2 r_uv, in const vec3 pos, in const mat4 mat) {
vec4 coo = mat * vec4(pos, 1.0);
r_uv = (coo.xy / coo.w) * 0.5;
}
void uv_project_keep_depth(out vec3 r_uv, in const vec3 pos, in const mat4 mat) {
vec4 coo = mat * vec4(pos, 1.0);
r_uv.xy = (coo.xy / coo.w) * 0.5;
r_uv.z = coo.z;
}
void uv_distort(inout vec2 uv) {
float cx, cy, x2, y2, xy2, r2, r4, r6, r_coeff, dcx = 0.0, dcy = 0.0, tx, ty;
cx = uv.x * _u_Intrinsics.res.x / _u_Intrinsics.lens;
cy = -uv.y * _u_Intrinsics.res.y / _u_Intrinsics.lens;
switch (_u_Intrinsics.distortion_model) {
case DISTORTIONMODEL_NONE:
dcx = cx;
dcy = cy;
break;
case DISTORTIONMODEL_POLYNOMIAL:
x2 = cx * cx;
y2 = cy * cy;
r2 = x2 + y2;
r4 = r2 * r2;
r6 = r4 * r2;
xy2 = 2.0 * cx * cy;
r_coeff = 1.0 + (_u_Intrinsics.k1 * r2) + (_u_Intrinsics.k2 * r4) + (_u_Intrinsics.k3 * r6);
dcx = cx * r_coeff + _u_Intrinsics.p1 * xy2 + _u_Intrinsics.p2 * (r2 + 2.0 * x2);
dcy = cy * r_coeff + _u_Intrinsics.p2 * xy2 + _u_Intrinsics.p1 * (r2 + 2.0 * y2);
break;
case DISTORTIONMODEL_DIVISION:
x2 = cx * cx;
y2 = cy * cy;
r2 = x2 + y2;
#if 0
r_coeff = 1.0 + k1 * r2;
dcx = cx / r_coeff;
dcy = cy / r_coeff;
#endif
r4 = r2 * r2;
r_coeff = 1.0 + _u_Intrinsics.k1 * r2 + _u_Intrinsics.k2 * r4;
dcx = cx / r_coeff;
dcy = cy / r_coeff;
break;
case DISTORTIONMODEL_BROWN:
x2 = cx * cx;
y2 = cy * cy;
xy2 = 2.0 * cx * cy;
r2 = x2 + y2;
r_coeff =
1.0f + (((_u_Intrinsics.k4 * r2 + _u_Intrinsics.k3) * r2 + _u_Intrinsics.k2) * r2 + _u_Intrinsics.k1) * r2;
tx = _u_Intrinsics.p1 * (r2 + 2.0 * x2) + _u_Intrinsics.p2 * xy2;
ty = _u_Intrinsics.p2 * (r2 + 2.0 * y2) + _u_Intrinsics.p1 * xy2;
dcx = (cx * r_coeff + tx);
dcy = (cy * r_coeff + ty);
break;
}
uv = ((vec2(_u_Intrinsics.lens * dcx + _u_Intrinsics.skew * dcy,
1.0 - _u_Intrinsics.lens * _u_Intrinsics.aspect * dcy) +
_u_Intrinsics.principal) /
_u_Intrinsics.res);
}