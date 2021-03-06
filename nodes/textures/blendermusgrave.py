import bpy
from bpy.props import EnumProperty, FloatProperty
from .. import LuxCoreNodeTexture

from .. import NOISE_BASIS_ITEMS

from .. import sockets
from ... import utils

class LuxCoreNodeTexBlenderMusgrave(LuxCoreNodeTexture):
    bl_label = "Blender Musgrave"
    bl_width_default = 200    

    musgrave_type_items = [
        ("multifractal", "Multifractal", ""),
        ("ridged_multifractal", "Ridged Multifractal", ""),
        ("hybrid_multifractal", "Hybrid Multifractal", ""),
        ("hetero_terrain", "Hetero Terrain", ""),
        ("fbm", "FBM", ""),
    ]

    musgrave_type = EnumProperty(name="Noise Type", description="Type of noise used", items=musgrave_type_items, default="multifractal")
    noise_basis = EnumProperty(name="Basis", description="Basis of noise used", items=NOISE_BASIS_ITEMS, default="blender_original")
    noise_size = FloatProperty(name="Noise Size", default=0.25, min=0)
    h =FloatProperty(name="Dimension", default=1.0, min=0)
    lacu = FloatProperty(name="Lacunarity", default=2.0)
    octs = FloatProperty(name="Octaves", default=2.0, min=0)
    offset = FloatProperty(name="Offset", default=1.0)
    gain = FloatProperty(name="Gain", default=1.0, min=0)
    iscale = FloatProperty(name="Intensity", default=1.0)
    bright = FloatProperty(name="Brightness", default=1.0, min=0)
    contrast = FloatProperty(name="Contrast", default=1.0, min=0)

    def init(self, context):
        self.add_input("LuxCoreSocketMapping3D", "3D Mapping")
        self.outputs.new("LuxCoreSocketColor", "Color")

    def draw_buttons(self, context, layout):
        layout.prop(self, "musgrave_type")
        layout.prop(self, "noise_basis")
        layout.prop(self, "noise_size")
        layout.prop(self, "h")
        layout.prop(self, "lacu")
        layout.prop(self, "octs")

        if self.musgrave_type in ("ridged_multifractal", "hybrid_multifractal", "hetero_terrain"):
            layout.prop(self, "offset")

        if self.musgrave_type in ("ridged_multifractal", "hybrid_multifractal"):
            layout.prop(self, "gain")

        if self.musgrave_type != "fbm":
            layout.prop(self, "iscale")

        layout.separator()
        column = layout.column(align=True)
        column.prop(self, "bright")
        column.prop(self, "contrast")

    def export(self, props, luxcore_name=None):
        mapping_type, transformation = self.inputs["3D Mapping"].export(props)
       
        definitions = {
            "type": "blender_musgrave",
            "musgravetype": self.musgrave_type,
            "noisebasis": self.noise_basis,
            "noisesize": self.noise_size,
            "h": self.h,
            "lacu": self.lacu,
            "octs": self.octs,
            "bright": self.bright,
            "contrast": self.contrast,
            # Mapping
            "mapping.type": mapping_type,
            "mapping.transformation": utils.matrix_to_list(transformation),
        }
        if self.musgrave_type in ('ridged_multifractal', 'hybrid_multifractal', 'hetero_terrain'):
            definitions["offset"] = self.offset

        if self.musgrave_type in ('ridged_multifractal', 'hybrid_multifractal'):
            definitions["gain"] = self.gain

        if self.musgrave_type != 'fbm':
            definitions["iscale"] = self.iscale            
        
        return self.base_export(props, definitions, luxcore_name)
