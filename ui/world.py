from bl_ui.properties_world import WorldButtonsPanel
from bpy.types import Panel
from ..utils import ui as utils_ui
from . import ICON_VOLUME


class LUXCORE_PT_context_world(WorldButtonsPanel, Panel):
    """
    World UI Panel
    """
    COMPAT_ENGINES = {"LUXCORE"}
    bl_label = ""
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.world and engine == "LUXCORE"

    def draw(self, context):
        layout = self.layout
        world = context.world
        layout.prop(world.luxcore, "light", expand=True)

        if world.luxcore.light != "none":
            # TODO: id (light group)
            split = layout.split(percentage=0.33)
            split.prop(world.luxcore, "rgb_gain", text="")

            is_sky = world.luxcore.light == "sky2"
            has_sun = world.luxcore.sun and world.luxcore.sun.type == "LAMP"

            if is_sky and has_sun and world.luxcore.use_sun_gain_for_sky:
                split.prop(world.luxcore.sun.data.luxcore, "gain")
            else:
                split.prop(world.luxcore, "gain")

            if is_sky and has_sun:
                split.prop(world.luxcore, "use_sun_gain_for_sky")

        layout.label("Default Volume (used on materials without attached volume):")
        utils_ui.template_node_tree(layout, world.luxcore, "volume", ICON_VOLUME,
                                    "LUXCORE_VOLUME_MT_world_select_volume_node_tree",
                                    "luxcore.world_show_volume_node_tree",
                                    "luxcore.world_new_volume_node_tree",
                                    "luxcore.world_unlink_volume_node_tree")


class LUXCORE_WORLD_PT_sky2(WorldButtonsPanel, Panel):
    """
    Sky2 UI Panel
    """
    COMPAT_ENGINES = {"LUXCORE"}
    bl_label = "Sky Settings"

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        correct_light = context.world.luxcore.light == "sky2"
        return context.world and engine == "LUXCORE" and correct_light

    def draw(self, context):
        layout = self.layout
        world = context.world

        layout.prop(world.luxcore, "sun")
        sun = world.luxcore.sun
        if sun:
            is_really_a_sun = sun.type == "LAMP" and sun.data and sun.data.type == "SUN"

            if is_really_a_sun:
                layout.label("Using turbidity of sun light:", icon="INFO")
                layout.prop(sun.data.luxcore, "turbidity")
            else:
                layout.label("Not a sun lamp", icon="ERROR")
        else:
            layout.prop(world.luxcore, "turbidity")

        # Note: ground albedo can be used without ground color
        layout.prop(world.luxcore, "groundalbedo")
        layout.prop(world.luxcore, "ground_enable")

        if world.luxcore.ground_enable:
            layout.prop(world.luxcore, "ground_color")


class LUXCORE_WORLD_PT_infinite(WorldButtonsPanel, Panel):
    """
    Infinite UI Panel
    """
    COMPAT_ENGINES = {"LUXCORE"}
    bl_label = "HDRI Settings"

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.world and engine == "LUXCORE" and context.world.luxcore.light == "infinite"

    def draw(self, context):
        layout = self.layout
        world = context.world

        layout.template_ID(world.luxcore, "image", open="image.open")

        sub = layout.column()
        sub.enabled = world.luxcore.image is not None
        sub.prop(world.luxcore, "gamma")
        sub.prop(world.luxcore, "rotation")
        sub.label("For free transformation use a hemi lamp", icon="INFO")
        sub.prop(world.luxcore, "sampleupperhemisphereonly")


class LUXCORE_WORLD_PT_performance(WorldButtonsPanel, Panel):
    """
    World UI Panel, shows stuff that affects the performance of the render
    """
    COMPAT_ENGINES = {"LUXCORE"}
    bl_label = "Performance"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.world and engine == "LUXCORE" and context.world.luxcore.light != "none"

    def draw(self, context):
        layout = self.layout
        world = context.world

        layout.prop(world.luxcore, "samples")
        layout.prop(world.luxcore, "importance")

        layout.prop(world.luxcore, "visibilitymap_enable")


class LUXCORE_WORLD_PT_visibility(WorldButtonsPanel, Panel):
    COMPAT_ENGINES = {"LUXCORE"}
    bl_label = "Visibility"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        visible = context.world and context.world.luxcore.light != "none"
        return engine == "LUXCORE" and visible

    def draw(self, context):
        layout = self.layout
        world = context.world

        # These settings only work with PATH and TILEPATH, not with BIDIR
        enabled = context.scene.luxcore.config.engine == "PATH"

        sub = layout.column()
        sub.enabled = enabled
        sub.label("Visibility for indirect light rays:")
        row = sub.row()
        row.prop(world.luxcore, "visibility_indirect_diffuse")
        row.prop(world.luxcore, "visibility_indirect_glossy")
        row.prop(world.luxcore, "visibility_indirect_specular")

        if not enabled:
            layout.label("Only supported by Path engines (not by Bidir)", icon="INFO")
