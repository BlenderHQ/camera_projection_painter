in mat4 data;
out mat4 v_Data;
void main() {
v_Data = data;
gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
}