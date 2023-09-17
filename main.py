from __future__ import annotations
_m='INVOKE_DEFAULT'
_l='RUNNING_MODAL'
_k='end, {elapsed:.6f} sec'
_j='{qualname} end, {elapsed:.6f} sec'
_i='{qualname} begin'
_h='u_UVProjectParams'
_g='RGBA32F'
_f='u_ShowActiveCamera'
_e='u_TileMapping'
_d='u_Atlas'
_c='u_Dithering'
_b='u_Image'
_a='POINTS'
_Z='OBJECT'
_Y='name_full'
_X='CPP_OT_view_camera'
_W='CPP_OT_select'
_V='CPP_OT_draw'
_U='CPP_OT_main'
_T='FINISHED'
_S='LESS_EQUAL'
_R='u_Intrinsics'
_Q='camera_wires'
_P='INTERNAL'
_O='u_ViewportMetrics'
_N='ALPHA'
_M='DEPTH_COMPONENT32F'
_L='FLOAT'
_K='VIEW_3D'
_J='u_Params'
_I='CAMERA'
_H='NONE'
_G='C'
_F='WINDOW'
_E=1.
_D=True
_C=False
_B=.0
_A=None
import os,math,time
from.import log
from.import get_addon_pref
from.lib import bhqab
from.lib import bhqglsl
from.import constants
from.import shaders
from.import reports
import bpy
from bpy.types import bpy_prop_collection,Brush,Context,Event,ID,Mesh,MeshUVLoopLayer,Operator,Region,SpaceImageEditor,SpaceView3D,Timer,View3DOverlay,Window,WorkSpaceTool
import bl_math
from bpy_extras import view3d_utils
from bpy.app.translations import pgettext
from mathutils import Matrix,Vector,Color
import gpu
from gpu.types import GPUBatch,GPUIndexBuf,GPUOffScreen,GPUShader,GPUShader,GPUTexture,GPUVertBuf,GPUVertFormat
from gpu_extras.batch import batch_for_shader
import blf
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import Literal;import numpy as np;from.props import Object,Image,WindowManager,Camera;from.props.camera import CameraProps;from.props.image import ImageProps;from.props.scene import SceneProps
__all__='CameraPainterMain','WindowInstances','CheckPoint','Workflow','EventMouse','GPUDrawCameras','GPUDrawMesh','GPUDraw','load_post_launch_main',_U,_V,_W,_X
class CameraPainterMain:
	@classmethod
	def initialize(cls,context:Context)->bool:return _D
	@classmethod
	def restore(cls,context:Context)->bool:return _D
class WindowInstances(CameraPainterMain):
	instances:set[CPP_OT_main]=set();window_timers:dict[Window,Timer]=dict()
	@classmethod
	def _validate_running_instances(cls)->_A:
		invalid_operator_instances=set()
		for operator_instance in cls.instances:
			try:getattr(operator_instance,'bl_idname')
			except ReferenceError:invalid_operator_instances.add(operator_instance)
		if invalid_operator_instances:cls.instances.difference_update(invalid_operator_instances)
	@classmethod
	def invoke_register_operator_instance_in_window(cls,context:Context,*,operator:CPP_OT_main)->_A:wm=context.window_manager;wm.modal_handler_add(operator);operator.window=context.window;cls.instances.add(operator)
	@classmethod
	def modal_ensure_operator_invoked_in_all_windows(cls,context:Context,*,idname:str)->_A:
		cls._validate_running_instances();wm:WindowManager=context.window_manager
		for window in wm.windows:
			is_operator_invoked_in_window=_C
			for operator_instance in cls.instances:
				if operator_instance.window==window:is_operator_invoked_in_window=_D
			if not is_operator_invoked_in_window:
				with context.temp_override(window=window):eval(f"bpy.ops.{idname}")('INVOKE_SCREEN')
	@classmethod
	def modal_verify_window_timer(cls,context:Context,*,time_step:float):
		wm=context.window_manager
		for window in wm.windows:
			existing_timer:Timer|_A=cls.window_timers.get(window,_A)
			if existing_timer:
				current_time_step_rounded=round(existing_timer.time_step,constants.IEEE754.FLT_DIG);required_time_step_rounded=round(time_step,constants.IEEE754.FLT_DIG)
				if current_time_step_rounded!=required_time_step_rounded:wm.event_timer_remove(existing_timer);existing_timer=_A
			if not existing_timer:cls.window_timers[window]=wm.event_timer_add(time_step=time_step,window=window)
	@classmethod
	def cancel_operator_instance(cls,context:Context,*,operator:CPP_OT_main):
		cls._validate_running_instances();is_any_other_instance_in_window=_C
		for operator_instance in cls.instances:
			if operator_instance==operator:continue
			if operator_instance.window==operator.window:is_any_other_instance_in_window=_D
		if not is_any_other_instance_in_window and context.window in cls.window_timers:wm=context.window_manager;timer=cls.window_timers[context.window];wm.event_timer_remove(timer=timer);del cls.window_timers[context.window]
		if operator in cls.instances:cls.instances.remove(operator)
	@classmethod
	def cancel_all(cls):
		for operator in tuple(cls.instances):operator.cancel(bpy.context)
	@staticmethod
	def tag_redraw_all_regions():bhqab.utils_wm.tag_redraw_all_regions(area_type=_K,region_type=_F)
class CheckPoint(CameraPainterMain):
	objects:tuple[Object]=tuple();images:tuple[Image]=tuple();prev_camera_has_changes:bool=_C;camera:_A|Object=_A;cam:_A|Camera=_A;image:_A|Image=_A;width:float=_B;height:float=_B;lens:float=_B;sensor_fit:Literal['AUTO','HORIZONTAL','VERTICAL'];sensor:float=_B;clip_start:float=_B;clip_end:float=_B;principal_x:float=_B;principal_y:float=_B;skew:float=_B;aspect:float=_B;distortion_model:str='';k1:float=_B;k2:float=_B;k3:float=_B;k4:float=_B;p1:float=_B;p2:float=_B;object_matrix_world:Matrix=Matrix.Identity(4);camera_matrix_world:Matrix=Matrix.Identity(4);object_arr_has_changes:bool=_C;image_arr_has_changes:bool=_C;select_id:int=constants.CAMERA.SELECT.OFFSET
	class pref:
		class view:use_mesh_preview:bool=_C;ui_line_width:str=''
		dithering_mix_factor:float=_B;refine_previews:str='';cameras_transparency:float=_B
	class scene_props:
		highlight_orientation:bool=_C;highlight_border:bool=_C;highlight_border_type:int=constants.BorderType.FILL;highlight_border_color0:Vector=Vector((_B,_B,_B,_B));highlight_border_color1:Vector=Vector((_B,_B,_B,_B));highlight_border_facing:set[str]=set()
		class image_paint:brush_size:float=_B
	@classmethod
	def restore(cls,_context:Context)->bool:cls.objects=tuple();cls.images=tuple();cls.prev_camera_has_changes=_C;cls.camera=_A;cls.cam=_A;cls.image=_A;cls.width=_B;cls.height=_B;cls.lens=_B;cls.sensor_fit='AUTO';cls.sensor=_B;cls.clip_start=_B;cls.clip_end=_B;cls.principal_x=_B;cls.principal_y=_B;cls.skew=_B;cls.aspect=_B;cls.distortion_model='';cls.k1=_B;cls.k2=_B;cls.k3=_B;cls.k4=_B;cls.p1=_B;cls.p2=_B;cls.object_matrix_world.identity();cls.camera_matrix_world.identity();cls.object_arr_has_changes=_C;cls.image_arr_has_changes=_C;cls.select_id=constants.CAMERA.SELECT.OFFSET;cls.pref.view.use_mesh_preview=_C;cls.pref.view.ui_line_width='';cls.pref.dithering_mix_factor=_B;cls.pref.refine_previews='';cls.pref.cameras_transparency=_B;cls.scene_props.highlight_orientation=_C;cls.scene_props.highlight_border=_C;cls.scene_props.highlight_border_type=constants.BorderType.FILL;cls.scene_props.highlight_border_color0=Vector((_B,_B,_B,_B));cls.scene_props.highlight_border_color1=Vector((_B,_B,_B,_B));cls.scene_props.highlight_border_facing.clear();cls.scene_props.image_paint.brush_size=_B;return _D
class Workflow(CameraPainterMain):
	__slots__=()
	@classmethod
	def initialize(cls,context:Context)->bool:return cls.Cameras.process_cameras_visibility(context,hide=_D)
	@classmethod
	def restore(cls,context:Context)->bool:return cls.Mesh.restore(context)and cls.Cameras.process_cameras_visibility(context,hide=_C)and cls.ImagePaint.restore(context)
	@staticmethod
	def check_object_arr_has_changed(context:Context)->bool:
		scene=context.scene
		if not CheckPoint.objects:CheckPoint.objects=tuple(scene.objects);return _C
		if len(scene.objects)!=len(CheckPoint.objects):CheckPoint.objects=tuple(scene.objects);return _D
		if CheckPoint.object_arr_has_changes:CheckPoint.object_arr_has_changes=_C;return _D
		return _C
	@staticmethod
	def check_image_arr_has_changed()->bool:
		if not CheckPoint.images:CheckPoint.images=tuple(bpy.data.images);return _C
		if len(bpy.data.images)!=len(CheckPoint.images):CheckPoint.images=tuple(bpy.data.images);return _D
		if CheckPoint.image_arr_has_changes:CheckPoint.image_arr_has_changes=_C;return _D
		return _C
	@staticmethod
	def object_poll(ob:_A|Object)->bool:
		if ob and'MESH'==ob.type:
			me:Mesh=ob.data
			if me.polygons:
				uv_layer=me.uv_layers.active
				if uv_layer:return _D
		return _C
	@staticmethod
	def camera_poll(ob:_A|Object)->bool:return ob and _I==ob.type and'PERSP'==ob.data.type
	@staticmethod
	def validate_id(*,item:bpy.types.ID)->bool:
		try:getattr(item,_Y)
		except ReferenceError:return _C
		return _D
	@staticmethod
	def get_id_index(*,coll:bpy_prop_collection,id:ID)->int:
		if id is _A:return-1
		name_full=''
		try:name_full=getattr(id,_Y)
		except ReferenceError:return-1
		if name_full:return coll.find(name_full)
	class Cameras:
		@staticmethod
		def process_cameras_visibility(context:Context,*,hide:bool)->bool:
			scene=context.scene
			for ob in scene.objects:
				if Workflow.camera_poll(ob):ob.hide_set(hide)
			return _D
		@classmethod
		def modal_validate_scene_camera_has_been_set(cls,context:Context)->bool:
			if not Workflow.camera:
				scene=context.scene
				for ob in scene.objects:
					if Workflow.camera_poll(ob):scene.camera=ob;return _D
				return _C
			return _D
	class Mesh:
		@classmethod
		def modal_validate_uv_layers(cls)->bool:
			mesh:Mesh=Workflow.mesh
			if mesh:
				if constants.TEMPORARY_DATA_NAME not in mesh.uv_layers:mesh.uv_layers.new(name=constants.TEMPORARY_DATA_NAME,do_init=_C)
				uv_layer=mesh.uv_layers[constants.TEMPORARY_DATA_NAME]
				if mesh.uv_layer_clone!=uv_layer:mesh.uv_layer_clone=uv_layer
				check_tmp_not_active=_D
				if mesh.uv_layers.active==uv_layer:
					check_tmp_not_active=_C
					for layer in mesh.uv_layers:
						if layer!=uv_layer:mesh.uv_layers.active=layer;check_tmp_not_active=_D;break
				return check_tmp_not_active
			return _C
		@classmethod
		def restore(cls,context:Context)->bool:
			mesh=Workflow.mesh
			if mesh:
				uv_layers=mesh.uv_layers
				if constants.TEMPORARY_DATA_NAME in uv_layers:uv_layers.remove(uv_layers[constants.TEMPORARY_DATA_NAME])
			return _D
	class ImagePaint:
		is_paint:bool=_C
		@classmethod
		def restore(cls,_context:Context)->bool:cls.is_paint=_C;return _D
		@staticmethod
		def __intern_get_clone_brush_tool(context:Context)->_A|WorkSpaceTool:
			tool:WorkSpaceTool=context.workspace.tools.from_space_view3d_mode(context.mode,create=_C)
			if tool and tool.idname=='builtin_brush.Clone':return tool
		@classmethod
		def tool_poll(cls,context:Context)->bool:ts=context.scene.tool_settings;return cls.__intern_get_clone_brush_tool(context)is not _A and ts.image_paint.mode=='IMAGE'and ts.image_paint.detect_data()
		@classmethod
		@property
		def size(cls)->float:
			ts=bpy.context.tool_settings;ups=ts.unified_paint_settings
			if ups.use_unified_size:return ups.size
			else:
				brush=ts.image_paint.brush
				if brush:return brush.size
			return _B
	@classmethod
	@property
	def object(cls)->_A|Object:
		context=bpy.context;ob:_A|Object=_A
		if'PAINT_TEXTURE'==context.mode:ob=context.image_paint_object
		elif _Z==context.mode:ob=context.active_object
		if ob and'MESH'==ob.type:return ob
	@classmethod
	@property
	def mesh(cls)->_A|Mesh:
		ob=cls.object
		if ob:return ob.data
	@classmethod
	@property
	def active_uv_layer(cls)->_A|MeshUVLoopLayer:
		ob=cls.object
		if ob:me:Mesh=ob.data;return me.uv_layers.active
	@classmethod
	@property
	def clone_uv_layer(cls)->_A|MeshUVLoopLayer:
		ob=cls.object
		if not ob:return
		me:Mesh=ob.data;return me.uv_layer_clone
	@classmethod
	@property
	def camera(cls)->_A|Object:
		context=bpy.context;scene=context.scene
		if context.mode==_Z:
			camera=context.active_object
			if Workflow.camera_poll(camera):return camera
		camera=scene.camera
		if Workflow.camera_poll(camera):return camera
	@classmethod
	@property
	def cam(cls)->_A|Camera:
		camera=cls.camera
		if camera:return camera.data
	@classmethod
	@property
	def image(cls)->_A|Image:
		camera=cls.camera
		if camera:cam:Camera=camera.data;cam_props:CameraProps=cam.cpp;return cam_props.image
	@classmethod
	@property
	def canvas(cls)->_A|Image:context=bpy.context;scene=context.scene;return scene.tool_settings.image_paint.canvas
	@classmethod
	@property
	def brush(cls)->_A|Brush:context=bpy.context;return context.scene.tool_settings.image_paint.brush
class EventMouse(CameraPainterMain):
	window:_A|Window=_A;region:_A|Region=_A;is_in_region_view_3d:bool=_C;position:Vector=Vector((_B,_B))
	@classmethod
	def restore(cls,_context:Context)->bool:cls.window=_A;cls.region=_A;cls.is_in_region_view_3d=_C;cls.position=Vector((_B,_B));return _D
	@classmethod
	def update_from(cls,context:Context,event:Event)->_A:
		active_window=context.window;cls.window=active_window;cls.is_in_region_view_3d=_C
		for area in active_window.screen.areas:
			if _K==area.type:
				for region in area.regions:
					if _F==region.type:
						xmin=region.x;ymin=region.y;xmax=xmin+region.width;ymax=ymin+region.height
						if xmin<event.mouse_x<xmax and ymin<event.mouse_y<ymax:cls.region=region;cls.is_in_region_view_3d=_D;cls.position.x=event.mouse_x;cls.position.y=event.mouse_y;break
	@classmethod
	def position_region(cls,context:Context)->Vector:
		if cls.region:return cls.position-Vector((cls.region.x,cls.region.y))
		return cls.position
class GPUDrawCameras(CameraPainterMain):
	batch_wires_data:_A|np.ndarray=_A;batch_wires:_A|GPUBatch=_A;select_framework:_A|bhqab.utils_gpu.FrameBufferFramework=_A;select_id:int=constants.CAMERA.SELECT.OFFSET;tt_info:str='';tt_info_text_pos:_A|Vector=_A;need_update_camera_info:bool=_C;prv_pixels:_A|np.ndarray=_A;prv_atlas_offscreen:_A|GPUOffScreen=_A;prv_image_indices:_A|np.ndarray=_A;prv_image_indices_texture:_A|GPUTexture=_A;prv_images:list[Image]=list();prv_i:int=0;prv_process_queue:list[Object]=list();prv_render_queue:list[Object]=list();prv_rendered:_A|Object=_A;LINE_THICKNESS_PX:float=_E;tooltip_ubo:_A|bhqglsl.ubo.UBO[shaders.TooltipParams]=_A;prv_ubo:_A|bhqglsl.ubo.UBO[shaders.PreviewParams]=_A;dithering_ubo:_A|bhqglsl.ubo.UBO[shaders.DitheringParams]=_A;common_ubo:_A|bhqglsl.ubo.UBO[shaders.CameraCommonParams]=_A
	@classmethod
	def initialize(cls,context:Context)->bool:cls.modal_update_ubo_data(context);return cls.generate_batches(context,force=_D)and cls.update_select_framework(context)
	@classmethod
	def restore(cls,_context:Context)->bool:cls.batch_wires_data=_A;cls.batch_wires=_A;cls.select_framework=_A;cls.select_id=constants.CAMERA.SELECT.OFFSET;cls.tt_info='';cls.tt_info_text_pos=_A;cls.need_update_camera_info=_C;cls.clear_preview_data();cls.tooltip_ubo=_A;cls.prv_ubo=_A;cls.dithering_ubo=_A;cls.common_ubo=_A;return _D
	@classmethod
	def clear_preview_data(cls):bhqab.utils_ui.progress.complete(identifier='prv');cls.prv_pixels=_A;cls.prv_atlas_offscreen=_A;cls.prv_image_indices=_A;cls.prv_image_indices_texture=_A;cls.prv_images.clear();cls.prv_i=0;cls.prv_process_queue.clear();cls.prv_render_queue.clear();cls.prv_rendered=_A
	@classmethod
	def handlers_SpaceView3D(cls)->set[object]:return{SpaceView3D.draw_handler_add(cls.cb_SpaceView3D_POST_PIXEL,tuple(),_F,'POST_PIXEL'),SpaceView3D.draw_handler_add(cls.cb_SpaceView3D_Selection,tuple(),_F,'PRE_VIEW')}
	@staticmethod
	def shorten_path(fp:str,max_length:int)->str:
		A='...'
		if len(fp)<max_length:return fp
		ret=A;parts=fp.split(os.sep);add_last_path=_C
		while len(ret)<max_length:
			if len(parts)==0:return ret
			if add_last_path:ret=ret.replace(A,f"...{os.sep}{parts[-1]}");del parts[-1];add_last_path=_C
			else:ret=ret.replace(A,f"{parts[0]}{os.sep}...");del parts[0];add_last_path=_D
		return ret
	@staticmethod
	def pack_camera_data_as_m4_flatten(*,camera:Object,camera_index:int)->_A|tuple[float]:
		cam:Camera=camera.data;cam_props:CameraProps=cam.cpp;image:_A|Image=cam.cpp.image;preview_tile_index=constants.IEEE754.INT_MAX;aspect=_E
		if image:image_props:ImageProps=image.cpp;aspect=image_props.aspect;preview_tile_index=Workflow.get_id_index(coll=bpy.data.images,id=image)
		lens=cam.lens/cam_props.sensor;m4_rot_loc=camera.matrix_world.to_quaternion().to_matrix().transposed().to_4x4();m4_rot_loc.translation=camera.matrix_world.translation;return*m4_rot_loc.row[0],*m4_rot_loc.row[1],*m4_rot_loc.row[2],lens,aspect,camera_index,preview_tile_index
	@classmethod
	def generate_batches(cls,context:Context,force:bool=_C)->bool:
		import numpy as np
		if force or cls.batch_wires_data is _A:cls.batch_wires_data=np.array(tuple(cls.pack_camera_data_as_m4_flatten(camera=ob,camera_index=i)for(i,ob)in enumerate(context.scene.objects)if Workflow.camera_poll(ob)),dtype=np.float32,order=_G);cls.batch_wires=batch_for_shader(shaders.get(_Q),type=_a,content=dict(data=cls.batch_wires_data))
		return _D
	@classmethod
	def update_batches_for_camera(cls,context:Context,*,camera:Object):
		import numpy as np;ob_index=Workflow.get_id_index(coll=context.scene.objects,id=camera)
		if ob_index!=-1:
			indices=np.where(cls.batch_wires_data[:,14]==ob_index)
			if indices:
				index=indices[0];updated_data=cls.pack_camera_data_as_m4_flatten(camera=camera,camera_index=ob_index);existing_data=cls.batch_wires_data[index]
				if np.array_equal(updated_data,existing_data):return
				cls.batch_wires_data[index]=updated_data
		cls.batch_wires=batch_for_shader(shaders.get(_Q),type=_a,content=dict(data=cls.batch_wires_data))
	@classmethod
	def prv_add_to_process_queue(cls,*,camera:_A|Object,prior:bool=_C):
		image=_A
		if Workflow.camera_poll(camera):cam_props:CameraProps=camera.data.cpp;image=cam_props.image
		if image is not _A:
			if prior:
				if image not in cls.prv_images:
					if camera in cls.prv_render_queue:cls.prv_render_queue.remove(camera);cls.prv_render_queue.append(camera)
					else:
						if camera in cls.prv_process_queue:cls.prv_process_queue.remove(camera)
						cls.prv_process_queue.append(camera)
			elif not(image in cls.prv_images or camera in cls.prv_process_queue or camera in cls.prv_render_queue or camera==cls.prv_rendered):cls.prv_process_queue.append(camera)
	@classmethod
	def prv_image_indices_texture_update(cls):cls.prv_image_indices_texture=GPUTexture(size=(constants.UI.PRV.SIDE,constants.UI.PRV.SIDE),format='R32F',data=gpu.types.Buffer(_L,constants.UI.PRV.NUM_TILES,cls.prv_image_indices))
	@classmethod
	def prv_image_indices_validate(cls,context:Context):
		addon_pref=get_addon_pref(context)
		if not addon_pref.use_previews:return
		invalid_indices=list()
		for(i,image)in enumerate(cls.prv_images):
			if not Workflow.validate_id(item=image):invalid_indices.append(i)
		for i in reversed(invalid_indices):cls.prv_image_indices[i]=-_E;cls.prv_images.pop(i)
		cls.prv_image_indices_texture_update()
	@classmethod
	def modal_process_previews_render_queue(cls,context:Context):
		addon_pref=get_addon_pref(context)
		if not addon_pref.use_previews:cls.clear_preview_data();return
		if cls.prv_render_queue:progress=bhqab.utils_ui.progress.get(identifier='prv');progress.label='Preview Render';num_images_total=len(bpy.data.images);progress.num_steps=num_images_total;progress.step=num_images_total-len(cls.prv_render_queue)
		import numpy as np
		if not cls.prv_atlas_offscreen:cls.prv_atlas_offscreen=GPUOffScreen(width=constants.UI.PRV.RESOLUTION,height=constants.UI.PRV.RESOLUTION,format=constants.UI.PRV.COLOR_FORMAT)
		if cls.prv_image_indices is _A:cls.prv_image_indices=np.full(constants.UI.PRV.NUM_TILES,-_E,dtype=np.float32,order=_G)
		def _get_pixels_float(image:Image)->_A|GPUTexture:
			prv=image.preview
			if prv:
				prv_width,prv_height=prv.image_size
				if prv_width and prv_height:
					if prv_width==128 and prv_height==128:prv_shape=65536
					else:prv_shape=prv_width*prv_height*4
					if cls.prv_pixels is _A:cls.prv_pixels=np.empty(shape=prv_shape,dtype=np.float32,order=_G)
					elif prv_shape!=cls.prv_pixels.shape:cls.prv_pixels.resize(prv_shape)
					prv.image_pixels_float.foreach_get(cls.prv_pixels)
					if np.any(cls.prv_pixels):return GPUTexture(size=(prv_width,prv_height),format=constants.UI.PRV.COLOR_FORMAT,data=gpu.types.Buffer(_L,prv_shape,cls.prv_pixels))
		textures=list();queue_num=len(cls.prv_process_queue)
		if queue_num>constants.UI.PRV.NUM_TILES:cls.prv_process_queue=cls.prv_process_queue[:constants.UI.PRV.NUM_TILES]
		textures:list[tuple[GPUTexture,Image,int]]=list();camera_hover=_A
		if cls.select_id!=constants.CAMERA.SELECT.OFFSET:camera_hover=context.scene.objects[cls.select_id]
		while cls.prv_process_queue:
			camera=cls.prv_process_queue.pop(-1);cam_props:CameraProps=camera.data.cpp;image=cam_props.image;image_index=Workflow.get_id_index(coll=bpy.data.images,id=image)
			if image_index!=-1:
				tex=_get_pixels_float(image)
				if tex:
					if camera==camera_hover:cls.need_update_camera_info=_D
					else:cls.need_update_camera_info=_C
					image.gl_free();image.buffers_free();textures.append((tex,image,image_index))
				else:cls.prv_render_queue.append(camera)
		if textures:
			shader=shaders.get('put_atlas_tile')
			with cls.prv_atlas_offscreen.bind():
				with gpu.matrix.push_pop():
					for(tex,image,image_index)in textures:
						if cls.prv_i==constants.UI.PRV.NUM_TILES:cls.prv_i=0
						if len(cls.prv_images)<constants.UI.PRV.NUM_TILES:cls.prv_images.append(image)
						else:cls.prv_images[cls.prv_i]=image
						cls.prv_image_indices[cls.prv_i]=image_index;shader.uniform_sampler('u_Preview',tex);shader.uniform_int('u_Index',cls.prv_i);shader.uniform_bool('u_UseFXAA',addon_pref.use_smooth_previews);bhqab.utils_gpu.BatchPreset.unit_rectangle_tris_P.draw(shader);image.buffers_free();image.gl_free();cls.prv_i+=1
			cls.prv_image_indices_texture_update()
		if bpy.app.is_job_running('RENDER_PREVIEW'):return
		elif cls.prv_rendered:cls.update_batches_for_camera(context,camera=cls.prv_rendered);cls.prv_process_queue.insert(0,cls.prv_rendered);cls.prv_rendered=_A
		elif cls.prv_render_queue:
			camera=cls.prv_render_queue.pop(-1);cam_props:CameraProps=camera.data.cpp;image=cam_props.image
			if Workflow.validate_id(item=image):image.asset_generate_preview();cls.prv_rendered=camera
	@classmethod
	@property
	def prv_is_rendering(cls)->bool:return bool(cls.prv_render_queue)
	@classmethod
	def update_select_framework(cls,context:Context)->bool:
		addon_pref=get_addon_pref(context)
		if not cls.select_framework:cls.select_framework=bhqab.utils_gpu.FrameBufferFramework(area_type=_K,region_type=_F)
		cls.select_framework.modal_eval(context,color_format='R32UI',depth_format=_M,percentage=addon_pref.select_framebuffer_scale);return _D
	@staticmethod
	def _intern_draw_tt_setup_blf(context:Context):pref=context.preferences;ui_scale=pref.view.ui_scale;text_size=pref.ui_styles[0].widget.points*ui_scale;blf.enable(0,blf.WORD_WRAP);blf.disable(0,blf.SHADOW|blf.MONOCHROME|blf.CLIPPING|blf.ROTATION);blf.word_wrap(0,-1);blf.size(0,text_size)
	@staticmethod
	def _intern_draw_tt_restore_blf():blf.disable(0,blf.WORD_WRAP)
	@classmethod
	def modal_update_ubo_data(cls,context:Context):
		if not cls.common_ubo:cls.common_ubo=bhqglsl.ubo.UBO(ubo_type=shaders.CameraCommonParams)
		scene=context.scene;scene_props:SceneProps=scene.cpp;pref=context.preferences;addon_pref=get_addon_pref(context);pref_theme_view_3d=pref.themes[0].view_3d;camera=Workflow.camera;camera_index=-1
		if camera:camera_index=Workflow.get_id_index(coll=scene.objects,id=camera)
		params=cls.common_ubo.data
		if camera_index!=constants.CAMERA.SELECT.OFFSET:flat_data=cls.pack_camera_data_as_m4_flatten(camera=camera,camera_index=camera_index);params.data=flat_data[0:4],flat_data[4:8],flat_data[8:12],flat_data[12:16]
		params.scale=scene_props.cameras_viewport_size;params.line_thickness=cls.LINE_THICKNESS_PX;params.index_hover=cls.select_id;params.index_active=camera_index;params.color[0:3]=pref_theme_view_3d.camera[:];params.color_active=pref_theme_view_3d.object_active[:]
		if scene_props.highlight_orientation:params.color_landscape[0:3]=scene_props.highlight_orientation_landscape_color[:];params.color_portrait[0:3]=scene_props.highlight_orientation_portrait_color[:]
		params.highlight_orientation=scene_props.highlight_orientation;params.transparency=addon_pref.cameras_transparency;cls.common_ubo.update()
		if not cls.dithering_ubo:cls.dithering_ubo=bhqglsl.ubo.UBO(ubo_type=shaders.DitheringParams)
		params=cls.dithering_ubo.data;params.use=bool(addon_pref.dithering_mix_factor)
		if addon_pref.dithering_mix_factor:params.mix_factor=addon_pref.dithering_mix_factor
		cls.dithering_ubo.update()
		if cls.select_id==constants.CAMERA.SELECT.OFFSET:cls.tt_info='';cls.tt_info_text_pos=Vector((0,0))
		else:
			msgctxt='ToolTip';ui_scale=context.preferences.view.ui_scale;theme=pref.themes[0];wcol=theme.user_interface.wcol_tooltip;scene=context.scene
			if cls.need_update_camera_info:
				camera=scene.objects[cls.select_id];cam:Camera=camera.data;cam_props:CameraProps=cam.cpp;image:Image=cam_props.image;image_fmt='';image_name=''
				if image:
					image_props:ImageProps=image.cpp;image_props.update_size_info(force=_C,free=not addon_pref.use_previews);image_fp_fmt=''
					if image.source not in{'GENERATED','VIEWER'}and image.filepath:image_fp_fmt=cls.shorten_path(image.filepath,max_length=constants.UI.TOOLTIP.FILEPATH_MAX_LENGTH)+'\n'
					image_source_fmt=bpy.types.UILayout.enum_item_name(image,'source',image.source);image_alpha_mode_fmt=bpy.types.UILayout.enum_item_name(image,'alpha_mode',image.alpha_mode);image_name=image.name;colorspace=image.colorspace_settings.name;has_data_fmt=pgettext('Yes'if image.has_data else'No',msgctxt);image_fmt=f"{image_fp_fmt}{image_props.size[0]} x {image_props.size[1]}, {image_source_fmt}, {image_alpha_mode_fmt}, {colorspace}\n"+pgettext('Loaded into memory: %s',msgctxt)%has_data_fmt+'\n'
				id_indices_fmt=''
				if bhqab.utils_ui.developer_extras_poll(bpy.context):
					image_index=-1
					if image:image_index=Workflow.get_id_index(coll=bpy.data.images,id=image)
					id_indices_fmt=pgettext('Image Index: %d\nCamera Index: %d',msgctxt)%(image_index,cls.select_id)
				camera_data_names_fmt=pgettext('%s - object\n',msgctxt)%camera.name+pgettext('%s - camera\n',msgctxt)%cam.name+(pgettext('%s - image\n',msgctxt)%image_name if image_name else'');text=f"{image_fmt}{camera_data_names_fmt}{id_indices_fmt}";cls.tt_info=text
			if cls.need_update_camera_info or addon_pref.tooltip_position=='FOLLOW':
				border_px=constants.UI.TOOLTIP.BORDER_PX_UNIT_SCALE*ui_scale;border_px_2=border_px*2;offset_from_cursor=Workflow.ImagePaint.size;offset_from_border=constants.UI.TOOLTIP.OFFSET_FROM_BORDER;PRV_SIZE=constants.UI.TOOLTIP.PRV_SIZE_NORMAL
				match addon_pref.tooltip_preview_size:
					case'NORMAL':PRV_SIZE=constants.UI.TOOLTIP.PRV_SIZE_NORMAL
					case'LARGE':PRV_SIZE=constants.UI.TOOLTIP.PRV_SIZE_LARGE
				PRV_SIZE*=ui_scale;prv_dimensions=Vector((PRV_SIZE,PRV_SIZE));cls._intern_draw_tt_setup_blf(context);line_height=blf.dimensions(0,'M')[1]*1.45;info_width,info_height=blf.dimensions(0,cls.tt_info);info_height+=line_height;cls._intern_draw_tt_restore_blf();image_index=-1
				if addon_pref.use_previews and cls.select_id!=constants.CAMERA.SELECT.OFFSET:
					camera=scene.objects[cls.select_id];cam_props:CameraProps=camera.data.cpp;image=cam_props.image
					if image:
						image_index=Workflow.get_id_index(coll=bpy.data.images,id=image);image_props:ImageProps=image.cpp
						if image_props.valid:prv_dimensions*=image_props.aspect_ratio
				prv_dimensions.x,prv_dimensions.y=int(prv_dimensions.x),int(prv_dimensions.y);box_sx=info_width+border_px_2;box_sy=info_height+border_px
				if image_index!=-1:box_sx+=border_px+prv_dimensions.x;box_sy=max(info_height,prv_dimensions.y)+border_px_2
				match addon_pref.tooltip_position:
					case'REMAIN'|'FOLLOW':mouse_pos=EventMouse.position_region(context);box_x=mouse_pos.x-box_sx*.5;box_y=mouse_pos.y-offset_from_cursor-box_sy-line_height-border_px;box_xmin=offset_from_border;box_xmax=EventMouse.region.width-box_sx-offset_from_border;box_ymin=offset_from_border;box_x=max(box_xmin,min(box_x,box_xmax));box_y=max(box_ymin,box_y)
					case'FIXED':box_x=EventMouse.region.width/2-box_sx*.5;box_y=offset_from_border
				box_upper=box_y+box_sy-border_px;prv_x=box_x+border_px;prv_y=box_upper-prv_dimensions.y;text_x=box_x+border_px
				if image_index!=-1:text_x+=prv_dimensions.x+border_px
				text_y=box_upper-line_height;cls.tt_info_text_pos=Vector((text_x,text_y))
				if not cls.tooltip_ubo:cls.tooltip_ubo=bhqglsl.ubo.UBO(ubo_type=shaders.TooltipParams)
				params=cls.tooltip_ubo.data
				if len(wcol.outline)==3:color_wcol_outline=*wcol.outline,_E
				elif len(wcol.outline)==4:color_wcol_outline=wcol.outline[:]
				params.transform=box_x,box_y,box_sx,box_sy;params.color=wcol.inner[:];params.outline_color=color_wcol_outline;params.show_shaded=wcol.show_shaded;params.shade_top_bottom=wcol.shadetop/255.,wcol.shadedown/255.;params.outline_thickness=cls.LINE_THICKNESS_PX;params.roundness=wcol.roundness;cls.tooltip_ubo.update()
				if image_index!=-1:
					if not cls.prv_ubo:cls.prv_ubo=bhqglsl.ubo.UBO(ubo_type=shaders.PreviewParams)
					params=cls.prv_ubo.data;params.transform=prv_x,prv_y,prv_dimensions.x,prv_dimensions.y;params.tile_index=image_index;params.aspect=image_props.aspect_ratio[:];params.outline_color=color_wcol_outline;params.outline_thickness=cls.LINE_THICKNESS_PX;params.roundness=wcol.roundness;cls.prv_ubo.update()
			cls.need_update_camera_info=_C
	@classmethod
	def cb_SpaceView3D_POST_PIXEL(cls):
		context=bpy.context;scene=context.scene;scene_props:SceneProps=scene.cpp;overlay:View3DOverlay=context.space_data.overlay
		if not overlay.show_overlays:return
		pref=context.preferences;theme=pref.themes[0];wcol=theme.user_interface.wcol_tooltip
		if context.region_data.view_perspective==_I and scene_props.current_image_alpha:
			camera=Workflow.camera;cam=Workflow.cam
			if cam:
				cam_props:CameraProps=cam.cpp;image:_A|Image=cam_props.image
				if image:
					image_props:ImageProps=image.cpp
					if image_props.valid:
						aspect=image_props.aspect_ratio;view_frame=cam.view_frame();left_bottom_corner=view3d_utils.location_3d_to_region_2d(context.region,context.region_data,coord=camera.matrix_world@view_frame[2]);right_top_corner=view3d_utils.location_3d_to_region_2d(context.region,context.region_data,coord=camera.matrix_world@view_frame[0]);frame_dimensions:Vector=right_top_corner-left_bottom_corner;frame_center:Vector=left_bottom_corner+frame_dimensions*.5
						with gpu.matrix.push_pop():gpu.state.blend_set(_N);shader_image=shaders.get('distorted_image');shader_image.bind();shader_image.uniform_sampler(_b,GPUDraw.image_texture);shader_image.uniform_float('u_Opacity',scene_props.current_image_alpha);shader_image.uniform_float('u_Aspect',aspect);viewport_metrics=bhqab.utils_gpu.get_viewport_metrics();shader_image.uniform_float(_O,viewport_metrics);shader_image.uniform_float('u_Transform',(frame_center.x,frame_center.y,frame_dimensions.x,frame_dimensions.y));shader_image.uniform_block(_R,GPUDraw.intrinsics_ubo.ubo);bhqab.utils_gpu.BatchPreset.ndc_rectangle_tris_P_UV.draw(shader_image)
		if context.region==EventMouse.region and cls.tt_info:
			do_draw_preview=_C
			if cls.prv_atlas_offscreen and cls.prv_image_indices_texture and cls.select_id!=constants.CAMERA.SELECT.OFFSET:
				camera=scene.objects[cls.select_id];cam_props:CameraProps=camera.data.cpp;image=cam_props.image
				if image and image.preview and image.preview.image_size[0]:do_draw_preview=_D
			with gpu.matrix.push_pop():
				gpu.state.blend_set(_N);shader=shaders.get('ui_rectangle');shader.uniform_block(_J,cls.tooltip_ubo.ubo);bhqab.utils_gpu.BatchPreset.unit_rectangle_tris_P.draw(shader)
				if do_draw_preview:shader=shaders.get('atlas_tile');shader.uniform_block(_J,cls.prv_ubo.ubo);shader.uniform_block(_c,cls.dithering_ubo.ubo);shader.uniform_sampler(_d,cls.prv_atlas_offscreen.texture_color);shader.uniform_sampler(_e,cls.prv_image_indices_texture);bhqab.utils_gpu.BatchPreset.unit_rectangle_tris_P.draw(shader)
				cls._intern_draw_tt_setup_blf(context);blf.color(0,*wcol.text,_E);blf.position(0,cls.tt_info_text_pos.x,cls.tt_info_text_pos.y,0);blf.draw(0,cls.tt_info);cls._intern_draw_tt_restore_blf()
	@classmethod
	def cb_SpaceView3D_POST_VIEW(cls):
		context=bpy.context;overlay:View3DOverlay=context.space_data.overlay
		if not overlay.show_overlays:return
		viewport_metrics=bhqab.utils_gpu.get_viewport_metrics();do_draw_previews=_C
		if cls.prv_atlas_offscreen and cls.prv_image_indices_texture:do_draw_previews=_D
		with gpu.matrix.push_pop():
			gpu.state.line_width_set(cls.LINE_THICKNESS_PX+.5);gpu.state.blend_set(_N);gpu.state.depth_mask_set(_D);gpu.state.depth_test_set(_S);gpu.state.front_facing_set(_C);gpu.state.face_culling_set(_H)
			if do_draw_previews:show_active_camera=context.region_data.view_perspective!=_I;shader_camera_frames=shaders.get('camera_frames');shader_camera_frames.bind();shader_camera_frames.uniform_float(_O,viewport_metrics);shader_camera_frames.uniform_block(_c,cls.dithering_ubo.ubo);shader_camera_frames.uniform_block(_J,cls.common_ubo.ubo);shader_camera_frames.uniform_bool(_f,show_active_camera);shader_camera_frames.uniform_sampler(_d,cls.prv_atlas_offscreen.texture_color);shader_camera_frames.uniform_sampler(_e,cls.prv_image_indices_texture);cls.batch_wires.draw(shader_camera_frames)
			shader_camera_wires=shaders.get(_Q);shader_camera_wires.bind();shader_camera_wires.uniform_float(_O,viewport_metrics);shader_camera_wires.uniform_block(_J,cls.common_ubo.ubo);cls.batch_wires.draw(shader_camera_wires)
	@classmethod
	def cb_SpaceView3D_Selection(cls):
		B='u_DepthMap';A='UINT';import numpy as np;context=bpy.context;addon_pref=get_addon_pref(context)
		if not cls.select_framework:return
		if context.region!=EventMouse.region:return
		fb_select=cls.select_framework.get()
		if not fb_select:return
		region_mouse=EventMouse.position_region(context)
		if 0<=region_mouse.x<=context.region.width and 0<=region_mouse.y<=context.region.height:
			camera=Workflow.camera
			if GPUDrawMesh.draw_framework:depth_map=GPUDrawMesh.draw_framework.get(index=0).get_depth_texture()
			else:depth_map=bhqab.utils_gpu.get_depth_map(depth_format=_M)
			fb_scale=addon_pref.select_framebuffer_scale/1e2;selection_mouse_x=region_mouse.x*fb_scale;selection_mouse_y=region_mouse.y*fb_scale
			with fb_select.bind():
				fb_select.clear(color=(_B,_B,_B,_B),depth=_E)
				with gpu.matrix.push_pop():viewport_metrics=bhqab.utils_gpu.get_viewport_metrics();gpu.state.line_width_set(_E);gpu.state.point_size_set(_E);gpu.state.blend_set(_H);gpu.state.depth_mask_set(_D);gpu.state.depth_test_set('LESS');gpu.state.front_facing_set(_C);gpu.state.face_culling_set(_H);shader=shaders.get('camera_select');shader.bind();shader.uniform_float('u_DepthMapMetrics',viewport_metrics[2:4]);shader.uniform_sampler(B,depth_map);shader.uniform_bool(_f,context.region_data.view_perspective!=_I);shader.uniform_block(_J,cls.common_ubo.ubo);cls.batch_wires.draw(shader);buff=gpu.types.Buffer(A,1);fb_select.read_color(x=int(selection_mouse_x),y=int(selection_mouse_y),xsize=1,ysize=1,channels=1,slot=0,format=A,data=buff)
				cls.select_id=buff[0]+constants.CAMERA.SELECT.OFFSET
			if addon_pref.use_previews:
				with fb_select.bind():
					fb_select.clear(color=(_B,_B,_B,_B),depth=_E)
					with gpu.matrix.push_pop():
						gpu.state.line_width_set(_E);gpu.state.point_size_set(_E);gpu.state.blend_set(_H);gpu.state.depth_mask_set(_C);gpu.state.depth_test_set(_S);gpu.state.front_facing_set(_C);gpu.state.face_culling_set(_H);shader=shaders.get('camera_roi');shader.bind();scene_props:SceneProps=context.scene.cpp;shader.uniform_float('u_Scale',scene_props.cameras_viewport_size);shader.uniform_sampler(B,depth_map);cls.batch_wires.draw(shader);w,h=fb_select.viewport_get()[2:];buff=gpu.types.Buffer(A,w*h);fb_select.read_color(x=0,y=0,xsize=w,ysize=h,channels=1,slot=0,format=A,data=buff);arr=np.array(buff,dtype=np.int32,copy=_C,order=_G);arr=arr[arr!=0]+constants.CAMERA.SELECT.OFFSET
						if arr.size:
							counts=np.bincount(arr);max_count=np.max(counts);most_repetitive_items=np.argwhere(counts>=int(max_count/2)).flatten();queue_num=len(most_repetitive_items)
							if queue_num>constants.UI.PRV.NUM_TILES:most_repetitive_items=most_repetitive_items[queue_num-constants.UI.PRV.NUM_TILES:]
							for i in most_repetitive_items:
								camera=context.scene.objects[i]
								if Workflow.camera_poll(camera):cls.prv_add_to_process_queue(camera=camera,prior=_C)
class GPUDrawMesh(CameraPainterMain):
	__slots__=();draw_framework:_A|bhqab.utils_gpu.DrawFramework=_A;batch_tris:_A|GPUBatch=_A;batch_loop_pairs:_A|GPUBatch=_A;brush_curve_points_data:_A|tuple[tuple[Vector,str]]=_A;brush_curve_size:float=_B;brush_curve_texture:_A|GPUTexture=_A;uv_project_offscreen:_A|GPUOffScreen=_A;camera_matrix:Matrix=Matrix.Identity(4);need_uv_project:bool=_C;uv_project_ubo:_A|bhqglsl.ubo.UBO[shaders.UVProjectParams]=_A;mesh_project_ubo:_A|bhqglsl.ubo.UBO[shaders.MeshProjectParams]=_A
	@classmethod
	def initialize(cls,context:Context)->bool:return cls.generate_batches(context)and cls.__intern_update_uv_project_framebuffer()and cls.update_draw_framework(context)
	@classmethod
	def restore(cls,_context:Context)->bool:cls.draw_framework=_A;cls.batch_tris=_A;cls.batch_loop_pairs=_A;cls.brush_curve_points_data=_A;cls.brush_curve_size=_A;cls.brush_curve_texture=_A;cls.uv_project_offscreen=_A;cls.camera_matrix=Matrix.Identity(4);cls.need_uv_project=_C;cls.uv_project_ubo=_A;cls.mesh_project_ubo=_A;return _D
	@classmethod
	def generate_batches(cls,context:Context):
		B='TRIS';A='LINES';mesh=Workflow.mesh
		if not mesh:return _C
		addon_pref=get_addon_pref(context);do_batch_tris=addon_pref.use_mesh_preview
		if cls.batch_loop_pairs:
			if do_batch_tris:
				if cls.batch_tris:return _D
			else:
				if cls.batch_tris:cls.batch_tris=_A;print('Removed mesh batch triangles')
				return _D
		import numpy as np;mesh:Mesh=Workflow.mesh;num_verts=len(mesh.vertices);num_loops=len(mesh.loops);vert_format=GPUVertFormat();vert_format.attr_add(id='P',comp_type='F32',len=3,fetch_mode=_L)
		if do_batch_tris:vert_format.attr_add(id='ID',comp_type='I32',len=1,fetch_mode='INT')
		vbo=GPUVertBuf(len=num_loops,format=vert_format);vertex_positions=np.empty((num_verts,3),dtype=np.float32,order=_G);loop_vertex_indices=np.empty(num_loops,dtype=np.int32,order=_G);mesh.vertices.foreach_get('co',vertex_positions.ravel());mesh.loops.foreach_get('vertex_index',loop_vertex_indices.ravel());vbo.attr_fill(id='P',data=vertex_positions[loop_vertex_indices]);loop_indices=loop_vertex_indices;mesh.loops.foreach_get('index',loop_indices)
		if do_batch_tris:vbo.attr_fill(id='ID',data=loop_indices.ravel())
		if num_loops%2:loop_indices=np.concatenate((loop_indices,np.zeros(1,dtype=loop_indices.dtype)))
		lines_ibo=GPUIndexBuf(type=A,seq=loop_indices.reshape(((num_loops+1)//2,2)));cls.batch_loop_pairs=GPUBatch(type=A,buf=vbo,elem=lines_ibo)
		if do_batch_tris:mesh.calc_loop_triangles();num_loop_tri=len(mesh.loop_triangles);loop_tri_indices=loop_vertex_indices;loop_tri_indices.resize(num_loop_tri*3,refcheck=_C);mesh.loop_triangles.foreach_get('loops',loop_tri_indices);tris_ibo=GPUIndexBuf(type=B,seq=loop_tri_indices.reshape((num_loop_tri,3)));cls.batch_tris=GPUBatch(type=B,buf=vbo,elem=tris_ibo)
		return _D
	@classmethod
	def __intern_update_uv_project_framebuffer(cls)->bool:
		ob=Workflow.object
		if ob:mesh:Mesh=ob.data;num_loops=len(mesh.loops);side=math.ceil(math.sqrt(num_loops/2));cls.uv_project_offscreen=GPUOffScreen(width=side,height=side,format=_g);return _D
		return _C
	@classmethod
	def update_draw_framework(cls,context:Context)->bool:
		addon_pref=get_addon_pref(context)
		if addon_pref.use_mesh_preview:
			if not cls.draw_framework:cls.draw_framework=bhqab.utils_gpu.DrawFramework(num=1,area_type=_K,region_type=_F)
			if cls.draw_framework:cls.draw_framework.update_from_preferences(pref=addon_pref,attr_aa_method='aa_method',attr_smaa_preset='smaa_preset',attr_fxaa_preset='fxaa_preset',attr_fxaa_value='fxaa_value');cls.draw_framework.modal_eval(context,color_format=_g,depth_format=_M,percentage=100);return _D
			return _C
		return _D
	@classmethod
	def update_brush_curve_mapping_texture(cls,context:Context):
		brush=context.scene.tool_settings.image_paint.brush;size=Workflow.ImagePaint.size
		if brush and size:
			cm=brush.curve;cm.initialize();curve=cm.curves[0];curve_data=tuple((point.location.copy(),point.handle_type)for point in curve.points)
			if cls.brush_curve_size!=size or cls.brush_curve_points_data!=curve_data:cls.brush_curve_texture=GPUTexture(size=size,format='R32F',data=gpu.types.Buffer(_L,size,tuple(bl_math.clamp(cm.evaluate(curve,bl_math.lerp(cm.clip_min_x,cm.clip_max_x,i/size)),cm.clip_min_y,cm.clip_max_y)for i in range(size))));cls.brush_curve_points_data=curve_data;cls.brush_curve_size=size
		else:cls.brush_curve_texture=_A
	@classmethod
	def update_camera_matrix(cls,context:Context)->bool:
		camera=Workflow.camera;image=Workflow.image;ob=Workflow.object
		if camera and image and ob:
			image_props:ImageProps=image.cpp;dg=context.evaluated_depsgraph_get();image_width,image_height=image_props.size
			if image_width and image_height:model_view=camera.matrix_world.inverted();projection=camera.calc_matrix_camera(depsgraph=dg,x=image_width,y=image_height);cls.camera_matrix=projection@model_view@ob.matrix_world;return _D
		return _C
	@classmethod
	def cb_SpaceView3D_POST_VIEW(cls):
		context=bpy.context
		if not(cls.draw_framework and cls.batch_tris):return
		if context.region!=EventMouse.region:return
		fb_framework=cls.draw_framework.get(index=0)
		if not fb_framework:return
		fb=fb_framework.get()
		if not fb:return
		original_depth_texture=bhqab.utils_gpu.get_depth_map(depth_format=_M);viewport_metrics=bhqab.utils_gpu.get_viewport_metrics();ob=Workflow.object;camera=Workflow.camera
		if not(ob and camera):return
		mouse_pos=EventMouse.position_region(context);shader=shaders.get('mesh_project');shader.uniform_sampler('u_DepthTexture',original_depth_texture)
		if GPUDraw.image_texture:shader.uniform_sampler(_b,GPUDraw.image_texture)
		if cls.brush_curve_texture:shader.uniform_sampler('u_BrushMask',cls.brush_curve_texture)
		shader.uniform_sampler('u_UVProjectTexture',cls.uv_project_offscreen.texture_color);shader.uniform_float('u_BrushPos',mouse_pos);shader.uniform_float(_O,viewport_metrics);shader.uniform_block(_R,GPUDraw.intrinsics_ubo.ubo);shader.uniform_block(_h,cls.uv_project_ubo.ubo);shader.uniform_block('u_MeshProjectParams',cls.mesh_project_ubo.ubo)
		with fb.bind():
			with gpu.matrix.push_pop():fb.clear(color=(_B,_B,_B,_B),depth=_E);gpu.state.line_width_set(_E);gpu.state.blend_set(_N);gpu.state.depth_mask_set(_D);gpu.state.depth_test_set(_S);gpu.state.front_facing_set(_C);gpu.state.face_culling_set(_H);cls.batch_tris.draw(shader)
		texture=fb_framework.get_color_texture()
		if texture:cls.draw_framework.draw(texture=texture)
	@classmethod
	def update_uv_project_ubo(cls,context:Context)->bool:
		if not cls.uv_project_ubo:cls.uv_project_ubo=bhqglsl.ubo.UBO(ubo_type=shaders.UVProjectParams)
		if not cls.update_camera_matrix(context):return _C
		params=cls.uv_project_ubo.data;params.camera_matrix=tuple(_[:]for _ in cls.camera_matrix.col);params.uv_texture_resolution=cls.uv_project_offscreen.width;cls.uv_project_ubo.update();return _D
	@classmethod
	def update_mesh_project_ubo(cls,context:Context)->bool:
		if not cls.mesh_project_ubo:cls.mesh_project_ubo=bhqglsl.ubo.UBO(ubo_type=shaders.MeshProjectParams)
		ob=Workflow.object;camera=Workflow.camera;scene=context.scene;scene_props:SceneProps=scene.cpp
		if not(ob and camera):return _C
		params=cls.mesh_project_ubo.data;params.model_matrix=tuple(_[:]for _ in ob.matrix_world.col);params.brush_radius=Workflow.ImagePaint.size
		if scene_props.highlight_border:params.highlight_border_type=constants.BorderType[scene_props.highlight_border_type].value
		else:params.highlight_border_type=constants.BorderType.NONE.value
		params.highlight_border_color0=scene_props.highlight_border_color_0[:];params.highlight_border_color1=scene_props.highlight_border_color_1[:];params.highlight_border_facing=bhqglsl.ubo.prop_as_enum(enum_cls=constants.Facing,value=scene_props.highlight_border_facing);params.draw_preview=not Workflow.ImagePaint.is_paint;params.use_uniforms=cls.need_uv_project;cls.mesh_project_ubo.update();return _D
	@classmethod
	def uv_project(cls,context:Context)->bool:
		import numpy as np
		if cls.need_uv_project:
			cam:Camera=Workflow.cam
			if cam:cam_props:CameraProps=cam.cpp;cam_props.update_tool_settings(context)
			shader=shaders.get('uv_project');shader.uniform_block(_R,GPUDraw.intrinsics_ubo.ubo);shader.uniform_block(_h,cls.uv_project_ubo.ubo);fb=cls.uv_project_offscreen
			with fb.bind():
				fb=gpu.state.active_framebuffer_get();fb.clear(color=(_B,_B,_B,_B));gpu.state.blend_set(_H);gpu.state.point_size_set(_E)
				with gpu.matrix.push_pop():gpu.matrix.load_matrix(Matrix.Identity(4));gpu.matrix.load_projection_matrix(Matrix.Identity(4));cls.batch_loop_pairs.draw(shader)
			mesh=Workflow.mesh;uv_layer=Workflow.clone_uv_layer;buff:gpu.types.Buffer=cls.uv_project_offscreen.texture_color.read();buff.dimensions=buff.dimensions[0]*buff.dimensions[1]*4;buffer_access=np.array(buff,dtype=np.float32,order=_G,copy=_C);uv_layer.uv.foreach_set('vector',buffer_access[:len(uv_layer.uv)*2]);mesh.update_tag();log.debug('UV Project');cls.need_uv_project=_C;cls.update_mesh_project_ubo(context)
		return _D
class GPUDraw(CameraPainterMain):
	draw_handlers:dict[SpaceView3D|SpaceImageEditor,set[object]]=dict();_image_texture_source:_A|Image=_A;_image_texture:_A|GPUTexture=_A;intrinsics_ubo:_A|bhqglsl.ubo.UBO[shaders.IntrinsicsPixelCoo]=_A
	@classmethod
	def initialize(cls,context:Context)->bool:return cls.invoke_add_handlers()
	@classmethod
	def restore(cls,_context:Context)->bool:cls.remove_handlers();cls._image_texture_source=_A;cls._image_texture=_A;cls.intrinsics_ubo=_A;return _D
	@classmethod
	def handlers_SpaceView3D(cls)->set[object]:return{SpaceView3D.draw_handler_add(cls.cb_SpaceView3D_POST_VIEW,tuple(),_F,'POST_VIEW')}
	@classmethod
	def invoke_add_handlers(cls)->bool:
		space_types=SpaceView3D,SpaceImageEditor
		for space_type in space_types:
			if space_type in cls.draw_handlers:
				for handle in cls.draw_handlers[space_type]:space_type.draw_handler_remove(handle,_F)
			cls.draw_handlers[space_type]=set()
		cls.draw_handlers[SpaceView3D].update(GPUDrawCameras.handlers_SpaceView3D());cls.draw_handlers[SpaceView3D].update(cls.handlers_SpaceView3D());return _D
	@classmethod
	def remove_handlers(cls)->bool:
		for(space,handlers)in cls.draw_handlers.items():
			for handle in handlers:space.draw_handler_remove(handle,_F)
		cls.draw_handlers.clear();return _D
	@classmethod
	@property
	def image_texture(cls)->bool:
		if cls._image_texture_source!=Workflow.image:
			cls._image_texture_source=Workflow.image
			if Workflow.image:
				image_props:ImageProps=Workflow.image.cpp
				if image_props.valid:cls._image_texture=gpu.texture.from_image(Workflow.image)
			else:cls._image_texture=_A
		return cls._image_texture
	@classmethod
	def update_intrinsics_ubo(cls):
		if not cls.intrinsics_ubo:cls.intrinsics_ubo=bhqglsl.ubo.UBO(ubo_type=shaders.IntrinsicsPixelCoo)
		image=Workflow.image
		if image:
			image_props:ImageProps=image.cpp;image_width,image_height=image_props.size
			if image_width and image_height:cam=Workflow.cam;cam_props:CameraProps=cam.cpp;params=cls.intrinsics_ubo.data;params.res=image_width,image_height;params.principal=cam_props.principal_px[0],cam_props.principal_px[1];params.lens=float(cam_props.lens_px);params.skew=float(cam_props.skew_px);params.aspect=float(cam_props.aspect);params.distortion_model=constants.DistortionModel[cam_props.distortion_model].value;params.k1=float(cam_props.k1);params.k2=float(cam_props.k2);params.k3=float(cam_props.k3);params.k4=float(cam_props.k4);params.p1=float(cam_props.p1);params.p2=float(cam_props.p2);cls.intrinsics_ubo.update()
	@classmethod
	def cb_SpaceView3D_POST_VIEW(cls):GPUDrawMesh.cb_SpaceView3D_POST_VIEW();GPUDrawCameras.cb_SpaceView3D_POST_VIEW()
def main(context:Context,event:Event):
	if not Workflow.Cameras.modal_validate_scene_camera_has_been_set(context):return
	if not Workflow.Mesh.modal_validate_uv_layers():return
	addon_pref=get_addon_pref(context)
	if CheckPoint.select_id!=GPUDrawCameras.select_id:GPUDrawCameras.need_update_camera_info=_D;camera:Object=context.scene.objects[GPUDrawCameras.select_id];GPUDrawCameras.update_batches_for_camera(context,camera=camera);GPUDrawCameras.prv_add_to_process_queue(camera=camera,prior=_D);CheckPoint.select_id=GPUDrawCameras.select_id
	if CheckPoint.pref.view.use_mesh_preview!=addon_pref.use_mesh_preview:
		if addon_pref.use_mesh_preview:
			cam:Camera=Workflow.cam
			if cam:cam_props:CameraProps=cam.cpp;cam_props.update_sensor_fit_from_image();cam_props.update_render_settings(context);cam_props.update_tool_settings(context)
		CheckPoint.pref.view.use_mesh_preview=addon_pref.use_mesh_preview
	changed_camera=_C;changed_camera_params=_C;changed_cam=_C;changed_cam_props=_C;changed_image=_C;changed_image_props=_C
	if CheckPoint.camera!=Workflow.camera:changed_camera=_D
	elif CheckPoint.cam!=Workflow.cam:changed_cam=_D
	else:
		camera:Object=CheckPoint.camera
		if camera:
			if CheckPoint.camera_matrix_world!=camera.matrix_world:changed_camera_params=_D
		cam:Camera=CheckPoint.cam
		if cam:
			cam_props:CameraProps=cam.cpp
			if CheckPoint.lens!=cam.lens or CheckPoint.clip_start!=cam.clip_start or CheckPoint.clip_end!=cam.clip_end or CheckPoint.sensor_fit!=cam.sensor_fit or CheckPoint.sensor!=cam_props.sensor or CheckPoint.aspect!=cam_props.aspect or CheckPoint.principal_x!=cam_props.principal_x or CheckPoint.principal_y!=cam_props.principal_y or CheckPoint.skew!=cam_props.skew or CheckPoint.distortion_model!=cam_props.distortion_model or CheckPoint.k1!=cam_props.k1 or CheckPoint.k2!=cam_props.k2 or CheckPoint.k3!=cam_props.k3 or CheckPoint.k4!=cam_props.k4 or CheckPoint.p1!=cam_props.p1 or CheckPoint.p2!=cam_props.p2:changed_cam_props=_D
			if CheckPoint.image!=Workflow.image:changed_image=_D
			else:
				image:Image=CheckPoint.image
				if image:
					image_props:ImageProps=image.cpp
					if CheckPoint.width!=image_props.size[0]or CheckPoint.height!=image_props.size[1]:changed_image_props=_D
	if changed_camera or changed_camera_params or changed_cam or changed_cam_props or changed_image or changed_image_props:
		cam:Camera=Workflow.cam
		if cam:
			cam_props:CameraProps=cam.cpp;cam_props.update_sensor_fit_from_image();cam_props.update_render_settings(context)
			if addon_pref.use_mesh_preview:cam_props.update_tool_settings(context)
		GPUDrawMesh.need_uv_project=_D;GPUDraw.update_intrinsics_ubo();GPUDrawMesh.update_uv_project_ubo(context);GPUDrawMesh.update_mesh_project_ubo(context)
		if CheckPoint.prev_camera_has_changes and changed_camera:GPUDrawCameras.update_batches_for_camera(context,camera=CheckPoint.camera);CheckPoint.prev_camera_has_changes=_C
		elif changed_camera_params or changed_cam or changed_cam_props or changed_image or changed_image_props:CheckPoint.prev_camera_has_changes=_D
	if changed_camera or changed_camera_params or changed_cam or changed_cam_props or changed_image or changed_image_props:
		CheckPoint.camera=Workflow.camera;CheckPoint.cam=Workflow.cam;CheckPoint.image=Workflow.image
		if CheckPoint.camera:CheckPoint.camera_matrix_world=CheckPoint.camera.matrix_world.copy()
		if CheckPoint.cam:cam:Camera=CheckPoint.cam;cam_props:CameraProps=cam.cpp;CheckPoint.lens=cam.lens;CheckPoint.clip_start=cam.clip_start;CheckPoint.clip_end=cam.clip_end;CheckPoint.sensor_fit=cam.sensor_fit;CheckPoint.sensor=cam_props.sensor;CheckPoint.aspect=cam_props.aspect;CheckPoint.principal_x=cam_props.principal_x;CheckPoint.principal_y=cam_props.principal_y;CheckPoint.skew=cam_props.skew;CheckPoint.distortion_model=cam_props.distortion_model;CheckPoint.k1=cam_props.k1;CheckPoint.k2=cam_props.k2;CheckPoint.k3=cam_props.k3;CheckPoint.k4=cam_props.k4;CheckPoint.p1=cam_props.p1;CheckPoint.p2=cam_props.p2
		if CheckPoint.image:cp_image_props:ImageProps=CheckPoint.image.cpp;CheckPoint.width=cp_image_props.size[0];CheckPoint.height=cp_image_props.size[1]
	def _compare_colors_4f(li,ri)->bool:return li[0]==ri[0]and li[1]==ri[1]and li[2]==ri[2]and li[3]==ri[3]
	scene_props:SceneProps=context.scene.cpp
	if Workflow.object and CheckPoint.object_matrix_world!=Workflow.object.matrix_world or CheckPoint.scene_props.image_paint.brush_size!=Workflow.ImagePaint.size or CheckPoint.scene_props.highlight_border!=scene_props.highlight_border or CheckPoint.scene_props.highlight_border_type!=constants.BorderType[scene_props.highlight_border_type]or not _compare_colors_4f(CheckPoint.scene_props.highlight_border_color0,scene_props.highlight_border_color_0)or not _compare_colors_4f(CheckPoint.scene_props.highlight_border_color1,scene_props.highlight_border_color_1)or CheckPoint.scene_props.highlight_border_facing!=scene_props.highlight_border_facing:GPUDrawMesh.update_mesh_project_ubo(context);CheckPoint.object_matrix_world=Workflow.object.matrix_world.copy();CheckPoint.scene_props.image_paint.brush_size=Workflow.ImagePaint.size;CheckPoint.scene_props.highlight_border=scene_props.highlight_border;CheckPoint.scene_props.highlight_border_type=constants.BorderType[scene_props.highlight_border_type];CheckPoint.scene_props.highlight_border_color0=scene_props.highlight_border_color_0[:];CheckPoint.scene_props.highlight_border_color1=scene_props.highlight_border_color_1[:];CheckPoint.scene_props.highlight_border_facing=scene_props.highlight_border_facing
	if'TIMER'==event.type:
		if Workflow.check_object_arr_has_changed(context):log.debug('Objects array has changed at runtime!');GPUDrawCameras.generate_batches(context,force=_D)
		if Workflow.check_image_arr_has_changed():log.debug('Image array has changed at runtime!');GPUDrawCameras.prv_image_indices_validate(context);GPUDrawCameras.generate_batches(context,force=_D)
		GPUDrawCameras.modal_update_ubo_data(context);GPUDrawCameras.update_select_framework(context);GPUDrawCameras.modal_process_previews_render_queue(context);GPUDrawMesh.generate_batches(context);GPUDrawMesh.update_brush_curve_mapping_texture(context);GPUDrawMesh.update_draw_framework(context)
	if event.type=='MOUSEMOVE':WindowInstances.tag_redraw_all_regions()
class CPP_OT_main(Operator):
	bl_idname='cpp.main';bl_label='CPP Main (internal)';bl_translation_context=_U;bl_options={_P};window:Window;initialized:bool=_C;_INIT_QUEUE=WindowInstances,Workflow,EventMouse,GPUDrawCameras,GPUDrawMesh,GPUDraw,CheckPoint
	@classmethod
	def queue_initialized(cls,context:Context)->bool:
		if not cls.initialized:
			log.debug('begin').push_indent();dt0=time.time();shaders.register()
			for item in cls._INIT_QUEUE:
				qualname=item.__qualname__;log.debug(_i.format(qualname=qualname)).push_indent();dt1=time.time();init=getattr(item,'initialize',_A)
				if not init(context):log.pop_indent().warning('{qualname} not done, queue not initialized'.format(qualname=qualname));return _C
				log.pop_indent().debug(_j.format(qualname=qualname,elapsed=time.time()-dt1))
			cls.initialized=_D;log.pop_indent().debug(_k.format(elapsed=time.time()-dt0))
		return _D
	@classmethod
	def queue_restore(cls,context:Context)->bool:
		if cls.initialized:
			log.debug('begin').push_indent();dt0=time.time()
			for item in reversed(cls._INIT_QUEUE):
				qualname=item.__qualname__;dt1=time.time();log.debug(_i.format(qualname=qualname));ret=getattr(item,'restore',_A)
				if not ret(context):log.warning('{qualname} not done, queue not restored'.format(qualname=qualname));return _C
				log.debug(_j.format(qualname=qualname,elapsed=time.time()-dt1))
			cls.initialized=_C;log.pop_indent().debug(_k.format(elapsed=time.time()-dt0)).pop_indent()
		return _D
	def cancel(self,context:Context):
		cls=self.__class__;WindowInstances.cancel_operator_instance(context,operator=self)
		if not WindowInstances.instances:cls.queue_restore(context);WindowInstances.tag_redraw_all_regions();CPP_OT_main.initialized=_C
	def invoke(self,context:Context,_event:Event):WindowInstances.invoke_register_operator_instance_in_window(context,operator=self);return{_l}
	def modal(self,context:Context,event:Event):
		cls=self.__class__;WindowInstances.modal_ensure_operator_invoked_in_all_windows(context,idname=CPP_OT_main.bl_idname)
		if Workflow.ImagePaint.tool_poll(context):
			WindowInstances.modal_verify_window_timer(context,time_step=constants.TIME_STEP.ACTIVE);EventMouse.update_from(context,event)
			if cls.queue_initialized(context):main(context,event)
		else:WindowInstances.modal_verify_window_timer(context,time_step=constants.TIME_STEP.IDLE);cls.queue_restore(context)
		return{'PASS_THROUGH'}
class CPP_OT_draw(Operator):
	bl_idname='cpp.draw';bl_label='Draw';bl_options={_P};bl_translation_context=_V
	@classmethod
	def poll(cls,_context:Context):return GPUDrawCameras.select_id==constants.CAMERA.SELECT.OFFSET
	def invoke(self,context:Context,_event:Event):GPUDrawMesh.uv_project(context);wm=context.window_manager;wm.modal_handler_add(self);Workflow.ImagePaint.is_paint=_D;return bpy.ops.paint.image_paint(_m)
	def modal(self,context:Context,event:Event):
		EventMouse.update_from(context,event)
		if event.type!='TIMER':Workflow.ImagePaint.is_paint=_C;return{_T}
		return{_l}
class CPP_OT_select(Operator):
	bl_idname='cpp.select';bl_label='Select';bl_options={_P};bl_translation_context=_W
	@classmethod
	def poll(cls,_context:Context):return GPUDrawCameras.select_id!=constants.CAMERA.SELECT.OFFSET
	@reports.log_execution_helper
	def execute(self,context:Context):
		scene=context.scene;camera=scene.objects[GPUDrawCameras.select_id]
		if context.scene.camera!=camera:context.scene.camera=camera
		cam:Camera=camera.data;cam_props:CameraProps=cam.cpp;image:_A|Image=cam_props.image
		if image:
			if image.has_data:log.debug('Image has data loaded into memory')
			else:log.debug('Image is not loaded into memory')
		else:log.debug('Camera missing image')
		return{_T}
class CPP_OT_view_camera(Operator):
	bl_idname='cpp.exit_camera_view';bl_label='Exit Camera View';bl_options={_P};bl_translation_context=_X
	@classmethod
	def poll(cls,context:Context):view_3d=context.region_data;return Workflow.ImagePaint.tool_poll(context)and view_3d and view_3d.view_perspective==_I
	@reports.log_execution_helper
	def execute(self,context:Context):bpy.ops.view3d.view_camera(_m);return{_T}