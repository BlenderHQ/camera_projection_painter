import bpy

from ... import engine


class CPP_OT_bind_camera_image(bpy.types.Operator):
    bl_idname = "cpp.bind_camera_image"
    bl_label = "Bind Image By Name"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        items=[
            ('ACTIVEOB', "Active Object", ""),
            ('SCENECAM', "Scene Camera", ""),
            ('SELECTED', "Selected Cameras", ""),
            ('ALL', "All Cameras", ""),
            ('GS', "Current Camera", "")  # Gizmo-selected
        ],
        name="Mode",
        default='ALL'
    )

    refresh_image_previews: bpy.props.BoolProperty(
        name="Refresh Image Preview",
        default=False,
        description="Refresh image files previews (large) and icons (small). "
        "Previews, which are already set, will be skipped.\n\n"
        "Warning: this operation may be slow for large datasets"
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "refresh_image_previews")

    @classmethod
    def description(cls, context, properties):
        mode = properties.mode

        if mode == 'ACTIVEOB':
            return "Binding image to camera data by name matching"
        elif mode == 'SCENECAM':
            return "Binding an image to the current scene camera by name matching"
        elif mode == 'SELECTED':
            return "Binding images to selected cameras by name matching"
        elif mode == 'ALL':
            return "Binding images to all cameras in the scene by name matching"
        elif mode == 'GS':
            return "Binding image to context camera data by name matching"

    def iter_processed_cameras(self, context):
        scene = context.scene
        if self.mode == 'ACTIVEOB':
            active_ob = context.active_object
            if active_ob and active_ob.type == 'CAMERA':
                yield active_ob

        elif self.mode == 'SCENECAM':
            active_ob = scene.camera
            if active_ob and active_ob.type == 'CAMERA':
                yield active_ob

        elif self.mode == 'SELECTED':
            for active_ob in scene.cpp.selected_camera_objects:
                yield active_ob
            return

        elif self.mode == 'ALL':
            for active_ob in scene.cpp.camera_objects:
                yield active_ob
            return

        elif self.mode == 'GS':
            active_ob = context.window_manager.cpp.current_selected_camera_ob
            if active_ob and active_ob.type == 'CAMERA':
                yield active_ob

    def execute(self, context):
        scene = context.scene
        camera_ob_seq = list([_ for _ in self.iter_processed_cameras(context)])

        result = engine.io.bind_camera_image_seq(camera_ob_seq, scene.cpp.source_dir)

        if result is None:
            self.report(type={'WARNING'}, message=f"No matches found")
            return {'CANCELLED'}

        engine.images.update_image_seq_static_size(skip_already_set=False)

        succeded_by_src_dir, succeded_by_existing = result

        if self.refresh_image_previews:
            bpy.ops.cpp.refresh_image_preview(
                'INVOKE_DEFAULT',
                True
            )

        def _camera_word(num: int):
            if num == 1:
                return "camera"
            else:
                return "cameras"

        wm = context.window_manager
        if not wm.cpp.is_preview_refresh_modal:
            self.report(
                type={'INFO'},
                message=f"Binded {succeded_by_src_dir} {_camera_word(succeded_by_src_dir)} from dataset directory, "
                        f"{succeded_by_existing} {_camera_word(succeded_by_existing)} from already opened images."
            )

        return {'FINISHED'}
