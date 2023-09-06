void main() {
v_UV = UV - 0.5;
gl_Position = ModelViewProjectionMatrix * vec4(P * u_Transform.zw * 0.5 * u_Aspect + u_Transform.xy, 0.0, 1.0);
}