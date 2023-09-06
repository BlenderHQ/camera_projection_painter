#if defined(SMAA_PRESET_LOW)
#  define SMAA_THRESHOLD 0.15
#  define SMAA_MAX_SEARCH_STEPS 4
#  define SMAA_DISABLE_DIAG_DETECTION
#  define SMAA_DISABLE_CORNER_DETECTION
#elif defined(SMAA_PRESET_MEDIUM)
#  define SMAA_THRESHOLD 0.1
#  define SMAA_MAX_SEARCH_STEPS 8
#  define SMAA_DISABLE_DIAG_DETECTION
#  define SMAA_DISABLE_CORNER_DETECTION
#elif defined(SMAA_PRESET_HIGH)
#  define SMAA_THRESHOLD 0.1
#  define SMAA_MAX_SEARCH_STEPS 16
#  define SMAA_MAX_SEARCH_STEPS_DIAG 8
#  define SMAA_CORNER_ROUNDING 25
#elif defined(SMAA_PRESET_ULTRA)
#  define SMAA_THRESHOLD 0.05
#  define SMAA_MAX_SEARCH_STEPS 32
#  define SMAA_MAX_SEARCH_STEPS_DIAG 16
#  define SMAA_CORNER_ROUNDING 25
#endif
#ifndef SMAA_THRESHOLD
#  define SMAA_THRESHOLD 0.1
#endif
#ifndef SMAA_DEPTH_THRESHOLD
#  define SMAA_DEPTH_THRESHOLD (0.1 * SMAA_THRESHOLD)
#endif
#ifndef SMAA_MAX_SEARCH_STEPS
#  define SMAA_MAX_SEARCH_STEPS 16
#endif
#ifndef SMAA_MAX_SEARCH_STEPS_DIAG
#  define SMAA_MAX_SEARCH_STEPS_DIAG 8
#endif
#ifndef SMAA_CORNER_ROUNDING
#  define SMAA_CORNER_ROUNDING 25
#endif
#ifndef SMAA_LOCAL_CONTRAST_ADAPTATION_FACTOR
#  define SMAA_LOCAL_CONTRAST_ADAPTATION_FACTOR 2.0
#endif
#ifndef SMAA_PREDICATION
#  define SMAA_PREDICATION 0
#endif
#ifndef SMAA_PREDICATION_THRESHOLD
#  define SMAA_PREDICATION_THRESHOLD 0.01
#endif
#ifndef SMAA_PREDICATION_SCALE
#  define SMAA_PREDICATION_SCALE 2.0
#endif
#ifndef SMAA_PREDICATION_STRENGTH
#  define SMAA_PREDICATION_STRENGTH 0.4
#endif
#ifndef SMAA_REPROJECTION
#  define SMAA_REPROJECTION 0
#endif
#ifndef SMAA_REPROJECTION_WEIGHT_SCALE
#  define SMAA_REPROJECTION_WEIGHT_SCALE 30.0
#endif
#ifndef SMAA_INCLUDE_VS
#  define SMAA_INCLUDE_VS 1
#endif
#ifndef SMAA_INCLUDE_PS
#  define SMAA_INCLUDE_PS 1
#endif
#ifndef SMAA_AREATEX_SELECT
#  if defined(SMAA_HLSL_3)
#    define SMAA_AREATEX_SELECT(sample) sample.ra
#  else
#    define SMAA_AREATEX_SELECT(sample) sample.rg
#  endif
#endif
#ifndef SMAA_SEARCHTEX_SELECT
#  define SMAA_SEARCHTEX_SELECT(sample) sample.r
#endif
#ifndef SMAA_DECODE_VELOCITY
#  define SMAA_DECODE_VELOCITY(sample) sample.rg
#endif
#define SMAA_AREATEX_MAX_DISTANCE 16
#define SMAA_AREATEX_MAX_DISTANCE_DIAG 20
#define SMAA_AREATEX_PIXEL_SIZE (1.0 / float2(160.0, 560.0))
#define SMAA_AREATEX_SUBTEX_SIZE (1.0 / 7.0)
#define SMAA_SEARCHTEX_SIZE float2(66.0, 33.0)
#define SMAA_SEARCHTEX_PACKED_SIZE float2(64.0, 16.0)
#define SMAA_CORNER_ROUNDING_NORM (float(SMAA_CORNER_ROUNDING) / 100.0)
#if defined(SMAA_HLSL_3)
#  define SMAATexture2D(tex) sampler2D tex
#  define SMAATexturePass2D(tex) tex
#  define SMAASampleLevelZero(tex, coord) tex2Dlod(tex, float4(coord, 0.0, 0.0))
#  define SMAASampleLevelZeroPoint(tex, coord) tex2Dlod(tex, float4(coord, 0.0, 0.0))
#  define SMAASampleLevelZeroOffset(tex, coord, offset) tex2Dlod(tex, float4(coord + offset * SMAA_RT_METRICS.xy, 0.0, 0.0))
#  define SMAASample(tex, coord) tex2D(tex, coord)
#  define SMAASamplePoint(tex, coord) tex2D(tex, coord)
#  define SMAASampleOffset(tex, coord, offset) tex2D(tex, coord + offset * SMAA_RT_METRICS.xy)
#  define SMAA_FLATTEN [flatten]
#  define SMAA_BRANCH [branch]
#endif
#if defined(SMAA_HLSL_4) || defined(SMAA_HLSL_4_1)
SamplerState LinearSampler
{
Filter = MIN_MAG_LINEAR_MIP_POINT;
AddressU = Clamp;
AddressV = Clamp;
};
SamplerState PointSampler
{
Filter = MIN_MAG_MIP_POINT;
AddressU = Clamp;
AddressV = Clamp;
};
#  define SMAATexture2D(tex) Texture2D tex
#  define SMAATexturePass2D(tex) tex
#  define SMAASampleLevelZero(tex, coord) tex.SampleLevel(LinearSampler, coord, 0)
#  define SMAASampleLevelZeroPoint(tex, coord) tex.SampleLevel(PointSampler, coord, 0)
#  define SMAASampleLevelZeroOffset(tex, coord, offset) tex.SampleLevel(LinearSampler, coord, 0, offset)
#  define SMAASample(tex, coord) tex.Sample(LinearSampler, coord)
#  define SMAASamplePoint(tex, coord) tex.Sample(PointSampler, coord)
#  define SMAASampleOffset(tex, coord, offset) tex.Sample(LinearSampler, coord, offset)
#  define SMAA_FLATTEN [flatten]
#  define SMAA_BRANCH [branch]
#  define SMAATexture2DMS2(tex) Texture2DMS<float4, 2> tex
#  define SMAALoad(tex, pos, sample) tex.Load(pos, sample)
#  if defined(SMAA_HLSL_4_1)
#    define SMAAGather(tex, coord) tex.Gather(LinearSampler, coord, 0)
#  endif
#endif
#if defined(SMAA_GLSL_3) || defined(SMAA_GLSL_4) || defined(GPU_METAL)
#  define SMAATexture2D(tex) sampler2D tex
#  define SMAATexturePass2D(tex) tex
#  define SMAASampleLevelZero(tex, coord) textureLod(tex, coord, 0.0)
#  define SMAASampleLevelZeroPoint(tex, coord) textureLod(tex, coord, 0.0)
#  define SMAASampleLevelZeroOffset(tex, coord, offset) textureLodOffset(tex, coord, 0.0, offset)
#  define SMAASample(tex, coord) texture(tex, coord)
#  define SMAASamplePoint(tex, coord) texture(tex, coord)
#  define SMAASampleOffset(tex, coord, offset) texture(tex, coord, offset)
#  define SMAA_FLATTEN
#  define SMAA_BRANCH
#  define lerp(a, b, t) mix(a, b, t)
#  define saturate(a) clamp(a, 0.0, 1.0)
#  if defined(SMAA_GLSL_4)
#    define mad(a, b, c) fma(a, b, c)
#    define SMAAGather(tex, coord) textureGather(tex, coord)
#  else
#    define mad(a, b, c) (a * b + c)
#  endif
#  define float2 vec2
#  define float3 vec3
#  define float4 vec4
#  define int2 ivec2
#  define int3 ivec3
#  define int4 ivec4
#  define bool2 bvec2
#  define bool3 bvec3
#  define bool4 bvec4
#endif
#if !defined(SMAA_HLSL_3) && !defined(SMAA_HLSL_4) && !defined(SMAA_HLSL_4_1) && !defined(SMAA_GLSL_3) && !defined(SMAA_GLSL_4) && !defined(SMAA_CUSTOM_SL)
#  error you must define the shading language: SMAA_HLSL_*, SMAA_GLSL_* or SMAA_CUSTOM_SL
#endif
float3 SMAAGatherNeighbours(float2 texcoord, float4 offset[3], SMAATexture2D(tex))
{
#ifdef SMAAGather
return SMAAGather(tex, texcoord + SMAA_RT_METRICS.xy * float2(-0.5, -0.5)).grb;
#else
float P = SMAASamplePoint(tex, texcoord).r;
float Pleft = SMAASamplePoint(tex, offset[0].xy).r;
float Ptop = SMAASamplePoint(tex, offset[0].zw).r;
return float3(P, Pleft, Ptop);
#endif
}
float2 SMAACalculatePredicatedThreshold(float2 texcoord,
float4 offset[3],
SMAATexture2D(predicationTex))
{
float3 neighbours = SMAAGatherNeighbours(texcoord, offset, SMAATexturePass2D(predicationTex));
float2 delta = abs(neighbours.xx - neighbours.yz);
float2 edges = step(SMAA_PREDICATION_THRESHOLD, delta);
return SMAA_PREDICATION_SCALE * SMAA_THRESHOLD * (1.0 - SMAA_PREDICATION_STRENGTH * edges);
}
void SMAAMovc(bool2 cond, inout float2 variable, float2 value)
{
variable = select(variable, value, cond);
}
void SMAAMovc(bool4 cond, inout float4 variable, float4 value)
{
variable = select(variable, value, cond);
}
#if SMAA_INCLUDE_VS
void SMAAEdgeDetectionVS(float2 texcoord, out float4 offset[3])
{
offset[0] = mad(SMAA_RT_METRICS.xyxy, float4(-1.0, 0.0, 0.0, -1.0), texcoord.xyxy);
offset[1] = mad(SMAA_RT_METRICS.xyxy, float4(1.0, 0.0, 0.0, 1.0), texcoord.xyxy);
offset[2] = mad(SMAA_RT_METRICS.xyxy, float4(-2.0, 0.0, 0.0, -2.0), texcoord.xyxy);
}
void SMAABlendingWeightCalculationVS(float2 texcoord, out float2 pixcoord, out float4 offset[3])
{
pixcoord = texcoord * SMAA_RT_METRICS.zw;
offset[0] = mad(SMAA_RT_METRICS.xyxy, float4(-0.25, -0.125, 1.25, -0.125), texcoord.xyxy);
offset[1] = mad(SMAA_RT_METRICS.xyxy, float4(-0.125, -0.25, -0.125, 1.25), texcoord.xyxy);
offset[2] = mad(SMAA_RT_METRICS.xxyy,
float4(-2.0, 2.0, -2.0, 2.0) * float(SMAA_MAX_SEARCH_STEPS),
float4(offset[0].xz, offset[1].yw));
}
void SMAANeighborhoodBlendingVS(float2 texcoord, out float4 offset)
{
offset = mad(SMAA_RT_METRICS.xyxy, float4(1.0, 0.0, 0.0, 1.0), texcoord.xyxy);
}
#endif
#if SMAA_INCLUDE_PS
#  ifndef SMAA_LUMA_WEIGHT
#    define SMAA_LUMA_WEIGHT float4(0.2126, 0.7152, 0.0722, 0.0)
#  endif
float2 SMAALumaEdgeDetectionPS(float2 texcoord,
float4 offset[3],
SMAATexture2D(colorTex)
#  if SMAA_PREDICATION
,
SMAATexture2D(predicationTex)
#  endif
)
{
#  if SMAA_PREDICATION
float2 threshold = SMAACalculatePredicatedThreshold(
texcoord, offset, SMAATexturePass2D(predicationTex));
#  else
float2 threshold = float2(SMAA_THRESHOLD, SMAA_THRESHOLD);
#  endif
float4 weights = SMAA_LUMA_WEIGHT;
float L = dot(SMAASamplePoint(colorTex, texcoord).rgba, weights);
float Lleft = dot(SMAASamplePoint(colorTex, offset[0].xy).rgba, weights);
float Ltop = dot(SMAASamplePoint(colorTex, offset[0].zw).rgba, weights);
float4 delta;
delta.xy = abs(L - float2(Lleft, Ltop));
float2 edges = step(threshold, delta.xy);
#  ifndef SMAA_NO_DISCARD
#    ifdef GPU_FRAGMENT_SHADER
if (dot(edges, float2(1.0, 1.0)) == 0.0)
discard;
#    endif
#  endif
float Lright = dot(SMAASamplePoint(colorTex, offset[1].xy).rgba, weights);
float Lbottom = dot(SMAASamplePoint(colorTex, offset[1].zw).rgba, weights);
delta.zw = abs(L - float2(Lright, Lbottom));
float2 maxDelta = max(delta.xy, delta.zw);
float Lleftleft = dot(SMAASamplePoint(colorTex, offset[2].xy).rgba, weights);
float Ltoptop = dot(SMAASamplePoint(colorTex, offset[2].zw).rgba, weights);
delta.zw = abs(float2(Lleft, Ltop) - float2(Lleftleft, Ltoptop));
maxDelta = max(maxDelta.xy, delta.zw);
float finalDelta = max(maxDelta.x, maxDelta.y);
#  if !defined(SHADER_API_OPENGL)
edges.xy *= step(finalDelta, SMAA_LOCAL_CONTRAST_ADAPTATION_FACTOR * delta.xy);
#  endif
return edges;
}
float2 SMAAColorEdgeDetectionPS(float2 texcoord,
float4 offset[3],
SMAATexture2D(colorTex)
#  if SMAA_PREDICATION
,
SMAATexture2D(predicationTex)
#  endif
)
{
#  if SMAA_PREDICATION
float2 threshold = SMAACalculatePredicatedThreshold(texcoord, offset, predicationTex);
#  else
float2 threshold = float2(SMAA_THRESHOLD, SMAA_THRESHOLD);
#  endif
float4 delta;
float3 C = SMAASamplePoint(colorTex, texcoord).rgb;
float3 Cleft = SMAASamplePoint(colorTex, offset[0].xy).rgb;
float3 t = abs(C - Cleft);
delta.x = max(max(t.r, t.g), t.b);
float3 Ctop = SMAASamplePoint(colorTex, offset[0].zw).rgb;
t = abs(C - Ctop);
delta.y = max(max(t.r, t.g), t.b);
float2 edges = step(threshold, delta.xy);
#  ifndef SMAA_NO_DISCARD
#    ifdef GPU_FRAGMENT_SHADER
if (dot(edges, float2(1.0, 1.0)) == 0.0)
discard;
#    endif
#  endif
float3 Cright = SMAASamplePoint(colorTex, offset[1].xy).rgb;
t = abs(C - Cright);
delta.z = max(max(t.r, t.g), t.b);
float3 Cbottom = SMAASamplePoint(colorTex, offset[1].zw).rgb;
t = abs(C - Cbottom);
delta.w = max(max(t.r, t.g), t.b);
float2 maxDelta = max(delta.xy, delta.zw);
float3 Cleftleft = SMAASamplePoint(colorTex, offset[2].xy).rgb;
t = abs(C - Cleftleft);
delta.z = max(max(t.r, t.g), t.b);
float3 Ctoptop = SMAASamplePoint(colorTex, offset[2].zw).rgb;
t = abs(C - Ctoptop);
delta.w = max(max(t.r, t.g), t.b);
maxDelta = max(maxDelta.xy, delta.zw);
float finalDelta = max(maxDelta.x, maxDelta.y);
#  if !defined(SHADER_API_OPENGL)
edges.xy *= step(finalDelta, SMAA_LOCAL_CONTRAST_ADAPTATION_FACTOR * delta.xy);
#  endif
return edges;
}
float2 SMAADepthEdgeDetectionPS(float2 texcoord, float4 offset[3], SMAATexture2D(depthTex))
{
float3 neighbours = SMAAGatherNeighbours(texcoord, offset, SMAATexturePass2D(depthTex));
float2 delta = abs(neighbours.xx - float2(neighbours.y, neighbours.z));
float2 edges = step(SMAA_DEPTH_THRESHOLD, delta);
#  ifdef GPU_FRAGMENT_SHADER
if (dot(edges, float2(1.0, 1.0)) == 0.0)
discard;
#  endif
return edges;
}
#  if !defined(SMAA_DISABLE_DIAG_DETECTION)
float2 SMAADecodeDiagBilinearAccess(float2 e)
{
e.r = e.r * abs(5.0 * e.r - 5.0 * 0.75);
return round(e);
}
float4 SMAADecodeDiagBilinearAccess(float4 e)
{
e.rb = e.rb * abs(5.0 * e.rb - 5.0 * 0.75);
return round(e);
}
float2 SMAASearchDiag1(SMAATexture2D(edgesTex), float2 texcoord, float2 dir, out float2 e)
{
float4 coord = float4(texcoord, -1.0, 1.0);
float3 t = float3(SMAA_RT_METRICS.xy, 1.0);
while (coord.z < float(SMAA_MAX_SEARCH_STEPS_DIAG - 1) && coord.w > 0.9) {
coord.xyz = mad(t, float3(dir, 1.0), coord.xyz);
e = SMAASampleLevelZero(edgesTex, coord.xy).rg;
coord.w = dot(e, float2(0.5, 0.5));
}
return coord.zw;
}
float2 SMAASearchDiag2(SMAATexture2D(edgesTex), float2 texcoord, float2 dir, out float2 e)
{
float4 coord = float4(texcoord, -1.0, 1.0);
coord.x += 0.25 * SMAA_RT_METRICS.x;
float3 t = float3(SMAA_RT_METRICS.xy, 1.0);
while (coord.z < float(SMAA_MAX_SEARCH_STEPS_DIAG - 1) && coord.w > 0.9) {
coord.xyz = mad(t, float3(dir, 1.0), coord.xyz);
e = SMAASampleLevelZero(edgesTex, coord.xy).rg;
e = SMAADecodeDiagBilinearAccess(e);
coord.w = dot(e, float2(0.5, 0.5));
}
return coord.zw;
}
float2 SMAAAreaDiag(SMAATexture2D(areaTex), float2 dist, float2 e, float offset)
{
float2 texcoord = mad(
float2(SMAA_AREATEX_MAX_DISTANCE_DIAG, SMAA_AREATEX_MAX_DISTANCE_DIAG), e, dist);
texcoord = mad(SMAA_AREATEX_PIXEL_SIZE, texcoord, 0.5 * SMAA_AREATEX_PIXEL_SIZE);
texcoord.x += 0.5;
texcoord.y += SMAA_AREATEX_SUBTEX_SIZE * offset;
return SMAA_AREATEX_SELECT(SMAASampleLevelZero(areaTex, texcoord));
}
float2 SMAACalculateDiagWeights(SMAATexture2D(edgesTex),
SMAATexture2D(areaTex),
float2 texcoord,
float2 e,
float4 subsampleIndices)
{
float2 weights = float2(0.0, 0.0);
float4 d;
float2 end;
if (e.r > 0.0) {
d.xz = SMAASearchDiag1(SMAATexturePass2D(edgesTex), texcoord, float2(-1.0, 1.0), end);
d.x += float(end.y > 0.9);
}
else
d.xz = float2(0.0, 0.0);
d.yw = SMAASearchDiag1(SMAATexturePass2D(edgesTex), texcoord, float2(1.0, -1.0), end);
SMAA_BRANCH
if (d.x + d.y > 2.0) {
float4 coords = mad(
float4(-d.x + 0.25, d.x, d.y, -d.y - 0.25), SMAA_RT_METRICS.xyxy, texcoord.xyxy);
float4 c;
c.xy = SMAASampleLevelZeroOffset(edgesTex, coords.xy, int2(-1, 0)).rg;
c.zw = SMAASampleLevelZeroOffset(edgesTex, coords.zw, int2(1, 0)).rg;
c.yxwz = SMAADecodeDiagBilinearAccess(c.xyzw);
float2 cc = mad(float2(2.0, 2.0), c.xz, c.yw);
SMAAMovc(bool2(step(0.9, d.zw)), cc, float2(0.0, 0.0));
weights += SMAAAreaDiag(SMAATexturePass2D(areaTex), d.xy, cc, subsampleIndices.z);
}
d.xz = SMAASearchDiag2(SMAATexturePass2D(edgesTex), texcoord, float2(-1.0, -1.0), end);
if (SMAASampleLevelZeroOffset(edgesTex, texcoord, int2(1, 0)).r > 0.0) {
d.yw = SMAASearchDiag2(SMAATexturePass2D(edgesTex), texcoord, float2(1.0, 1.0), end);
d.y += float(end.y > 0.9);
}
else
d.yw = float2(0.0, 0.0);
SMAA_BRANCH
if (d.x + d.y > 2.0) {
float4 coords = mad(float4(-d.x, -d.x, d.y, d.y), SMAA_RT_METRICS.xyxy, texcoord.xyxy);
float4 c;
c.x = SMAASampleLevelZeroOffset(edgesTex, coords.xy, int2(-1, 0)).g;
c.y = SMAASampleLevelZeroOffset(edgesTex, coords.xy, int2(0, -1)).r;
c.zw = SMAASampleLevelZeroOffset(edgesTex, coords.zw, int2(1, 0)).gr;
float2 cc = mad(float2(2.0, 2.0), c.xz, c.yw);
SMAAMovc(bool2(step(0.9, d.zw)), cc, float2(0.0, 0.0));
weights += SMAAAreaDiag(SMAATexturePass2D(areaTex), d.xy, cc, subsampleIndices.w).gr;
}
return weights;
}
#  endif
float SMAASearchLength(SMAATexture2D(searchTex), float2 e, float offset)
{
float2 scale = SMAA_SEARCHTEX_SIZE * float2(0.5, -1.0);
float2 bias = SMAA_SEARCHTEX_SIZE * float2(offset, 1.0);
scale += float2(-1.0, 1.0);
bias += float2(0.5, -0.5);
scale *= 1.0 / SMAA_SEARCHTEX_PACKED_SIZE;
bias *= 1.0 / SMAA_SEARCHTEX_PACKED_SIZE;
return SMAA_SEARCHTEX_SELECT(SMAASampleLevelZero(searchTex, mad(scale, e, bias)));
}
float SMAASearchXLeft(SMAATexture2D(edgesTex),
SMAATexture2D(searchTex),
float2 texcoord,
float end)
{
float2 e = float2(0.0, 1.0);
while (texcoord.x > end && e.g > 0.8281 &&
e.r == 0.0) {
e = SMAASampleLevelZero(edgesTex, texcoord).rg;
texcoord = mad(-float2(2.0, 0.0), SMAA_RT_METRICS.xy, texcoord);
}
float offset = mad(
-(255.0 / 127.0), SMAASearchLength(SMAATexturePass2D(searchTex), e, 0.0), 3.25);
return mad(SMAA_RT_METRICS.x, offset, texcoord.x);
}
float SMAASearchXRight(SMAATexture2D(edgesTex),
SMAATexture2D(searchTex),
float2 texcoord,
float end)
{
float2 e = float2(0.0, 1.0);
while (texcoord.x < end && e.g > 0.8281 &&
e.r == 0.0) {
e = SMAASampleLevelZero(edgesTex, texcoord).rg;
texcoord = mad(float2(2.0, 0.0), SMAA_RT_METRICS.xy, texcoord);
}
float offset = mad(
-(255.0 / 127.0), SMAASearchLength(SMAATexturePass2D(searchTex), e, 0.5), 3.25);
return mad(-SMAA_RT_METRICS.x, offset, texcoord.x);
}
float SMAASearchYUp(SMAATexture2D(edgesTex), SMAATexture2D(searchTex), float2 texcoord, float end)
{
float2 e = float2(1.0, 0.0);
while (texcoord.y > end && e.r > 0.8281 &&
e.g == 0.0) {
e = SMAASampleLevelZero(edgesTex, texcoord).rg;
texcoord = mad(-float2(0.0, 2.0), SMAA_RT_METRICS.xy, texcoord);
}
float offset = mad(
-(255.0 / 127.0), SMAASearchLength(SMAATexturePass2D(searchTex), e.gr, 0.0), 3.25);
return mad(SMAA_RT_METRICS.y, offset, texcoord.y);
}
float SMAASearchYDown(SMAATexture2D(edgesTex),
SMAATexture2D(searchTex),
float2 texcoord,
float end)
{
float2 e = float2(1.0, 0.0);
while (texcoord.y < end && e.r > 0.8281 &&
e.g == 0.0) {
e = SMAASampleLevelZero(edgesTex, texcoord).rg;
texcoord = mad(float2(0.0, 2.0), SMAA_RT_METRICS.xy, texcoord);
}
float offset = mad(
-(255.0 / 127.0), SMAASearchLength(SMAATexturePass2D(searchTex), e.gr, 0.5), 3.25);
return mad(-SMAA_RT_METRICS.y, offset, texcoord.y);
}
float2 SMAAArea(SMAATexture2D(areaTex), float2 dist, float e1, float e2, float offset)
{
float2 texcoord = mad(float2(SMAA_AREATEX_MAX_DISTANCE, SMAA_AREATEX_MAX_DISTANCE),
round(4.0 * float2(e1, e2)),
dist);
texcoord = mad(SMAA_AREATEX_PIXEL_SIZE, texcoord, 0.5 * SMAA_AREATEX_PIXEL_SIZE);
texcoord.y = mad(SMAA_AREATEX_SUBTEX_SIZE, offset, texcoord.y);
return SMAA_AREATEX_SELECT(SMAASampleLevelZero(areaTex, texcoord));
}
void SMAADetectHorizontalCornerPattern(SMAATexture2D(edgesTex),
inout float2 weights,
float4 texcoord,
float2 d)
{
#  if !defined(SMAA_DISABLE_CORNER_DETECTION)
float2 leftRight = step(d.xy, d.yx);
float2 rounding = (1.0 - SMAA_CORNER_ROUNDING_NORM) * leftRight;
rounding /= leftRight.x + leftRight.y;
float2 factor = float2(1.0, 1.0);
factor.x -= rounding.x * SMAASampleLevelZeroOffset(edgesTex, texcoord.xy, int2(0, 1)).r;
factor.x -= rounding.y * SMAASampleLevelZeroOffset(edgesTex, texcoord.zw, int2(1, 1)).r;
factor.y -= rounding.x * SMAASampleLevelZeroOffset(edgesTex, texcoord.xy, int2(0, -2)).r;
factor.y -= rounding.y * SMAASampleLevelZeroOffset(edgesTex, texcoord.zw, int2(1, -2)).r;
weights *= saturate(factor);
#  endif
}
void SMAADetectVerticalCornerPattern(SMAATexture2D(edgesTex),
inout float2 weights,
float4 texcoord,
float2 d)
{
#  if !defined(SMAA_DISABLE_CORNER_DETECTION)
float2 leftRight = step(d.xy, d.yx);
float2 rounding = (1.0 - SMAA_CORNER_ROUNDING_NORM) * leftRight;
rounding /= leftRight.x + leftRight.y;
float2 factor = float2(1.0, 1.0);
factor.x -= rounding.x * SMAASampleLevelZeroOffset(edgesTex, texcoord.xy, int2(1, 0)).g;
factor.x -= rounding.y * SMAASampleLevelZeroOffset(edgesTex, texcoord.zw, int2(1, 1)).g;
factor.y -= rounding.x * SMAASampleLevelZeroOffset(edgesTex, texcoord.xy, int2(-2, 0)).g;
factor.y -= rounding.y * SMAASampleLevelZeroOffset(edgesTex, texcoord.zw, int2(-2, 1)).g;
weights *= saturate(factor);
#  endif
}
float4 SMAABlendingWeightCalculationPS(float2 texcoord,
float2 pixcoord,
float4 offset[3],
SMAATexture2D(edgesTex),
SMAATexture2D(areaTex),
SMAATexture2D(searchTex),
float4 subsampleIndices)
{
float4 weights = float4(0.0, 0.0, 0.0, 0.0);
float2 e = SMAASample(edgesTex, texcoord).rg;
SMAA_BRANCH
if (e.g > 0.0) {
#  if !defined(SMAA_DISABLE_DIAG_DETECTION)
weights.rg = SMAACalculateDiagWeights(
SMAATexturePass2D(edgesTex), SMAATexturePass2D(areaTex), texcoord, e, subsampleIndices);
SMAA_BRANCH
if (weights.r == -weights.g) {
#  endif
float2 d;
float3 coords;
coords.x = SMAASearchXLeft(
SMAATexturePass2D(edgesTex), SMAATexturePass2D(searchTex), offset[0].xy, offset[2].x);
coords.y =
offset[1].y;
d.x = coords.x;
float e1 = SMAASampleLevelZero(edgesTex, coords.xy).r;
coords.z = SMAASearchXRight(
SMAATexturePass2D(edgesTex), SMAATexturePass2D(searchTex), offset[0].zw, offset[2].y);
d.y = coords.z;
d = abs(round(mad(SMAA_RT_METRICS.zz, d, -pixcoord.xx)));
float2 sqrt_d = sqrt(d);
float e2 = SMAASampleLevelZeroOffset(edgesTex, coords.zy, int2(1, 0)).r;
weights.rg = SMAAArea(SMAATexturePass2D(areaTex), sqrt_d, e1, e2, subsampleIndices.y);
coords.y = texcoord.y;
#  ifdef GPU_METAL
vec2 _weights = weights.rg;
SMAADetectHorizontalCornerPattern(SMAATexturePass2D(edgesTex), _weights, coords.xyzy, d);
weights.rg = _weights;
#  else
SMAADetectHorizontalCornerPattern(SMAATexturePass2D(edgesTex), weights.rg, coords.xyzy, d);
#  endif
#  if !defined(SMAA_DISABLE_DIAG_DETECTION)
}
else
e.r = 0.0;
#  endif
}
SMAA_BRANCH
if (e.r > 0.0) {
float2 d;
float3 coords;
coords.y = SMAASearchYUp(
SMAATexturePass2D(edgesTex), SMAATexturePass2D(searchTex), offset[1].xy, offset[2].z);
coords.x = offset[0].x;
d.x = coords.y;
float e1 = SMAASampleLevelZero(edgesTex, coords.xy).g;
coords.z = SMAASearchYDown(
SMAATexturePass2D(edgesTex), SMAATexturePass2D(searchTex), offset[1].zw, offset[2].w);
d.y = coords.z;
d = abs(round(mad(SMAA_RT_METRICS.ww, d, -pixcoord.yy)));
float2 sqrt_d = sqrt(d);
float e2 = SMAASampleLevelZeroOffset(edgesTex, coords.xz, int2(0, 1)).g;
weights.ba = SMAAArea(SMAATexturePass2D(areaTex), sqrt_d, e1, e2, subsampleIndices.x);
coords.x = texcoord.x;
#  ifdef GPU_METAL
vec2 _weights = weights.ba;
SMAADetectVerticalCornerPattern(SMAATexturePass2D(edgesTex), _weights, coords.xyxz, d);
weights.ba = _weights;
#  else
SMAADetectVerticalCornerPattern(SMAATexturePass2D(edgesTex), weights.ba, coords.xyxz, d);
#  endif
}
return weights;
}
float4 SMAANeighborhoodBlendingPS(float2 texcoord,
float4 offset,
SMAATexture2D(colorTex),
SMAATexture2D(blendTex)
#  if SMAA_REPROJECTION
,
SMAATexture2D(velocityTex)
#  endif
)
{
float4 a;
a.x = SMAASample(blendTex, offset.xy).a;
a.y = SMAASample(blendTex, offset.zw).g;
a.wz = SMAASample(blendTex, texcoord).xz;
SMAA_BRANCH
if (dot(a, float4(1.0, 1.0, 1.0, 1.0)) < 1e-5) {
float4 color = SMAASampleLevelZero(colorTex, texcoord);
#  if SMAA_REPROJECTION
float2 velocity = SMAA_DECODE_VELOCITY(SMAASampleLevelZero(velocityTex, texcoord));
color.a = sqrt(5.0 * length(velocity));
#  endif
return color;
}
else {
bool h = max(a.x, a.z) > max(a.y, a.w);
float4 blendingOffset = float4(0.0, a.y, 0.0, a.w);
float2 blendingWeight = a.yw;
SMAAMovc(bool4(h, h, h, h), blendingOffset, float4(a.x, 0.0, a.z, 0.0));
SMAAMovc(bool2(h, h), blendingWeight, a.xz);
blendingWeight /= dot(blendingWeight, float2(1.0, 1.0));
float4 blendingCoord = mad(
blendingOffset, float4(SMAA_RT_METRICS.xy, -SMAA_RT_METRICS.xy), texcoord.xyxy);
float4 color = blendingWeight.x * SMAASampleLevelZero(colorTex, blendingCoord.xy);
color += blendingWeight.y * SMAASampleLevelZero(colorTex, blendingCoord.zw);
#  if SMAA_REPROJECTION
float2 velocity = blendingWeight.x *
SMAA_DECODE_VELOCITY(SMAASampleLevelZero(velocityTex, blendingCoord.xy));
velocity += blendingWeight.y *
SMAA_DECODE_VELOCITY(SMAASampleLevelZero(velocityTex, blendingCoord.zw));
color.a = sqrt(5.0 * length(velocity));
#  endif
return color;
}
}
float4 SMAAResolvePS(float2 texcoord,
SMAATexture2D(currentColorTex),
SMAATexture2D(previousColorTex)
#  if SMAA_REPROJECTION
,
SMAATexture2D(velocityTex)
#  endif
)
{
#  if SMAA_REPROJECTION
float2 velocity = -SMAA_DECODE_VELOCITY(SMAASamplePoint(velocityTex, texcoord).rg);
float4 current = SMAASamplePoint(currentColorTex, texcoord);
float4 previous = SMAASamplePoint(previousColorTex, texcoord + velocity);
float delta = abs(current.a * current.a - previous.a * previous.a) / 5.0;
float weight = 0.5 * saturate(1.0 - sqrt(delta) * SMAA_REPROJECTION_WEIGHT_SCALE);
return lerp(current, previous, weight);
#  else
float4 current = SMAASamplePoint(currentColorTex, texcoord);
float4 previous = SMAASamplePoint(previousColorTex, texcoord);
return lerp(current, previous, 0.5);
#  endif
}
#  ifdef SMAALoad
void SMAASeparatePS(float4 position,
float2 texcoord,
out float4 target0,
out float4 target1,
SMAATexture2DMS2(colorTexMS))
{
int2 pos = int2(position.xy);
target0 = SMAALoad(colorTexMS, pos, 0);
target1 = SMAALoad(colorTexMS, pos, 1);
}
#  endif
#endif