import os
import time

import bpy
# import bmesh
import mathutils

from utils import matrix_util
from utils.matrix_util import mat3_to_vec_roll
from utils.node_arrange import nodes_iterate
from utils.node_util import load_tex, get_tree
from generated.formats.ms2 import Mdl2File
from generated.formats.fgm import FgmFile


def add_psys(ob):
	name = "hair"
	ps_mod = ob.modifiers.new(name, 'PARTICLE_SYSTEM')
	psys = ob.particle_systems[ps_mod.name]
	psys.settings.count = len(ob.data.vertices)
	psys.settings.type = 'HAIR'
	psys.settings.emit_from = 'VERT'
	psys.settings.use_emit_random = False
	psys.settings.hair_length = 1.0
	psys.vertex_group_length = "fur_length"


def load_mdl2(file_path):
	"""Loads a mdl2 from the given file path"""
	print(f"Importing {file_path}")

	data = Mdl2File()
	data.load(file_path)
	return data


def ovl_bones(b_armature_data):
	# first just get the roots, then extend it
	roots = [bone for bone in b_armature_data.bones if not bone.parent]
	# this_level = []
	out_bones = roots
	# next_level = []
	for bone in roots:
		out_bones += [child for child in bone.children]
	
	return [b.name for b in out_bones]


def import_armature(data):
	"""Scans an armature hierarchy, and returns a whole armature.
	This is done outside the normal node tree scan to allow for positioning
	of the bones before skins are attached."""
	bone_info = data.ms2_file.bone_info
	if bone_info:
		armature_name = "Test"
		b_armature_data = bpy.data.armatures.new(armature_name)
		b_armature_data.display_type = 'STICK'
		# b_armature_data.show_axes = True
		# set axis orientation for export
		# b_armature_data.niftools.axis_forward = NifOp.props.axis_forward
		# b_armature_data.niftools.axis_up = NifOp.props.axis_up
		b_armature_obj = create_ob(armature_name, b_armature_data)
		b_armature_obj.show_in_front = True
		bone_names = [matrix_util.bone_name_for_blender(n) for n in data.ms2_file.bone_names]
		# make armature editable and create bones
		bpy.ops.object.mode_set(mode='EDIT', toggle=False)
		mats = {}
		for bone_name, bone, o_parent_ind in zip(bone_names, bone_info.bones, bone_info.bone_parents):
			if not bone_name:
				bone_name = "Dummy"
			b_edit_bone = b_armature_data.edit_bones.new(bone_name)

			# local space matrix, in ms2 orientation
			n_bind = mathutils.Quaternion((bone.rot.w, bone.rot.x, bone.rot.y, bone.rot.z)).to_matrix().to_4x4()
			n_bind.translation = (bone.loc.x, bone.loc.y, bone.loc.z)

			# link to parent
			try:
				if o_parent_ind != 255:
					parent_name = bone_names[o_parent_ind]
					b_parent_bone = b_armature_data.edit_bones[parent_name]
					b_edit_bone.parent = b_parent_bone
					# calculate ms2 armature space matrix
					n_bind = mats[parent_name] @ n_bind
			except:
				print(f"Bone hierarchy error for bone {bone_name} with parent index {o_parent_ind}")

			# store the ms2 armature space matrix
			mats[bone_name] = n_bind

			# print()
			# print(bone_name)
			# print("ms2\n",n_bind)
			# change orientation for blender bones
			b_bind = matrix_util.nif_bind_to_blender_bind(n_bind)
			# b_bind = n_bind
			# print("n_bindxflip")
			# print(matrix_util.xflip @ n_bind)
			# set orientation to blender bone

			tail, roll = mat3_to_vec_roll(b_bind.to_3x3())
			# https://developer.blender.org/T82930
			# our matrices have negative determinants due to the x axis flip
			# this is broken since 2.82 - we need to use our workaround
			# tail, roll = bpy.types.Bone.AxisRollFromMatrix(b_bind.to_3x3())
			b_edit_bone.head = b_bind.to_translation()
			b_edit_bone.tail = tail + b_edit_bone.head
			b_edit_bone.roll = roll
			# print(b_bind)
			# print(roll)

		fix_bone_lengths(b_armature_data)
		bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

		# print("blender order")
		# for bone in b_armature_data.bones:
		# 	print(bone.name)
		# print("restored order")
		# bone_names_restored = ovl_bones(b_armature_data)
		# for bone in bone_names_restored:
		# 	print(bone)

		# store original bone index as custom property
		for i, bone_name in enumerate(bone_names):
			bone = b_armature_obj.pose.bones[bone_name]
			bone["index"] = i

		return b_armature_obj


def fix_bone_lengths(b_armature_data):
	"""Sets all edit_bones to a suitable length."""
	for b_edit_bone in b_armature_data.edit_bones:
		# don't change root bones
		if b_edit_bone.parent:
			# take the desired length from the mean of all children's heads
			if b_edit_bone.children:
				child_heads = mathutils.Vector()
				for b_child in b_edit_bone.children:
					child_heads += b_child.head
				bone_length = (b_edit_bone.head - child_heads / len(b_edit_bone.children)).length
				if bone_length < 0.0001:
					bone_length = 0.1
			# end of a chain
			else:
				bone_length = b_edit_bone.parent.length
			b_edit_bone.length = bone_length


def append_armature_modifier(b_obj, b_armature):
	"""Append an armature modifier for the object."""
	if b_obj and b_armature:
		b_obj.parent = b_armature
		armature_name = b_armature.name
		b_mod = b_obj.modifiers.new(armature_name, 'ARMATURE')
		b_mod.object = b_armature
		b_mod.use_bone_envelopes = False
		b_mod.use_vertex_groups = True


def create_material(in_dir, matname):
	
	print(f"Importing material {matname}")
	# only create the material if it doesn't exist in the blend file, then just grab it
	# but we overwrite its contents anyway
	if matname not in bpy.data.materials:
		mat = bpy.data.materials.new(matname)
	else:
		mat = bpy.data.materials[matname]

	fgm_path = os.path.join(in_dir, matname + ".fgm")
	# print(fgm_path)
	try:
		fgm_data = FgmFile()
		fgm_data.load(fgm_path)
	except FileNotFoundError:
		print(f"{fgm_path} does not exist!")
		return mat
	# base_index = fgm_data.textures[0].layers[1]
	# height_index = fgm_data.textures[1].layers[1]
	tree = get_tree(mat)
	output = tree.nodes.new('ShaderNodeOutputMaterial')
	principled = tree.nodes.new('ShaderNodeBsdfPrincipled')

	all_textures = [file for file in os.listdir(in_dir) if file.lower().endswith(".png")]
	# map texture names to node
	tex_dic = {}
	for fgm_texture in fgm_data.textures:
		png_base = fgm_texture.name.lower()
		if "blendweights" in png_base or "warpoffset" in png_base:
			continue
		textures = [file for file in all_textures if file.lower().startswith(png_base)]
		if not textures:
			png_base = png_base.lower().replace("_eyes", "").replace("_fin", "").replace("_shell", "")
			textures = [file for file in all_textures if file.lower().startswith(png_base)]
		if not textures:
			textures = [png_base + ".png", ]
		# print(textures)
		for png_name in textures:
			png_path = os.path.join(in_dir, png_name)
			b_tex = load_tex(tree, png_path)
			k = png_name.lower().split(".")[1]
			tex_dic[k] = b_tex

	# get diffuse and AO
	for diffuse_name in ("pbasediffusetexture", "pbasecolourtexture", "pbasecolourandmasktexture", "pdiffusealphatexture", "palbinobasecolourandmasktexture"):
		# get diffuse
		if diffuse_name in tex_dic:
			diffuse = tex_dic[diffuse_name]
			# get AO
			for ao_name in ("paotexture", "pbasepackedtexture_03"):
				if ao_name in tex_dic:
					ao = tex_dic[ao_name]
					ao.image.colorspace_settings.name = "Non-Color"

					# apply AO to diffuse
					diffuse_premix = tree.nodes.new('ShaderNodeMixRGB')
					diffuse_premix.blend_type = "MULTIPLY"
					diffuse_premix.inputs["Fac"].default_value = .25
					tree.links.new(diffuse.outputs[0], diffuse_premix.inputs["Color1"])
					tree.links.new(ao.outputs[0], diffuse_premix.inputs["Color2"])
					diffuse = diffuse_premix
					break
			# get marking
			fur_names = [k for k in tex_dic.keys() if "marking" in k and "noise" not in k and "patchwork" not in k]
			lut_names = [k for k in tex_dic.keys() if "pclut" in k]
			if fur_names and lut_names:
				marking = tex_dic[sorted(fur_names)[0]]
				lut = tex_dic[sorted(lut_names)[0]]
				marking.image.colorspace_settings.name = "Non-Color"

				# PZ LUTs usually occupy half of the texture, so scale the incoming greyscale coordinates so that
				# 1 lands in the center of the LUT
				scaler = tree.nodes.new('ShaderNodeMath')
				scaler.operation = "MULTIPLY"
				tree.links.new(marking.outputs[0], scaler.inputs[0])
				scaler.inputs[1].default_value = 0.5
				tree.links.new(scaler.outputs[0], lut.inputs[0])

				# apply AO to diffuse
				diffuse_premix = tree.nodes.new('ShaderNodeMixRGB')
				diffuse_premix.blend_type = "MIX"
				tree.links.new(diffuse.outputs[0], diffuse_premix.inputs["Color1"])
				tree.links.new(lut.outputs[0], diffuse_premix.inputs["Color2"])
				tree.links.new(marking.outputs[0], diffuse_premix.inputs["Fac"])
				diffuse = diffuse_premix
			#  link finished diffuse to shader
			tree.links.new(diffuse.outputs[0], principled.inputs["Base Color"])
			break

	if "pnormaltexture" in tex_dic:
		normal = tex_dic["pnormaltexture"]
		normal.image.colorspace_settings.name = "Non-Color"
		normal_map = tree.nodes.new('ShaderNodeNormalMap')
		tree.links.new(normal.outputs[0], normal_map.inputs[1])
		# normal_map.inputs["Strength"].default_value = 1.0
		tree.links.new(normal_map.outputs[0], principled.inputs["Normal"])

	# PZ - specularity?
	for spec_name in ( "proughnesspackedtexture_02",):
		if spec_name in tex_dic:
			specular = tex_dic[spec_name]
			specular.image.colorspace_settings.name = "Non-Color"
			tree.links.new(specular.outputs[0], principled.inputs["Specular"])

	# PZ - roughness?
	for roughness_name in ( "proughnesspackedtexture_01",):
		if roughness_name in tex_dic:
			roughness = tex_dic[roughness_name]
			roughness.image.colorspace_settings.name = "Non-Color"
			tree.links.new(roughness.outputs[0], principled.inputs["Roughness"])

	# JWE dinos - metalness
	for metal_name in ("pbasepackedtexture_02",):
		if metal_name in tex_dic:
			metal = tex_dic[metal_name]
			metal.image.colorspace_settings.name = "Non-Color"
			tree.links.new(metal.outputs[0], principled.inputs["Metallic"])

	# alpha
	alpha = None
	# JWE billboard: Foliage_Billboard
	if "pdiffusealphatexture" in tex_dic:
		alpha = tex_dic["pdiffusealphatexture"]
		alpha_pass = alpha.outputs[1]
	# PZ penguin
	elif "popacitytexture" in tex_dic:
		alpha = tex_dic["popacitytexture"]
		alpha_pass = alpha.outputs[0]
	elif "proughnesspackedtexture_00" in tex_dic and "Foliage_Clip" in fgm_data.shader_name:
		alpha = tex_dic["proughnesspackedtexture_00"]
		alpha_pass = alpha.outputs[0]
	# parrot: Metallic_Roughness_Clip -> 03
	elif "proughnesspackedtexture_03" in tex_dic and "Foliage_Clip" not in fgm_data.shader_name:
		alpha = tex_dic["proughnesspackedtexture_03"]
		alpha_pass = alpha.outputs[0]
	if alpha:
		# transparency
		mat.blend_method = "CLIP"
		mat.shadow_method = "CLIP"
		for attrib in fgm_data.attributes:
			if attrib.name.lower() == "palphatestref":
				mat.alpha_threshold = attrib.value[0]
				break
		transp = tree.nodes.new('ShaderNodeBsdfTransparent')
		alpha_mixer = tree.nodes.new('ShaderNodeMixShader')
		tree.links.new(alpha_pass, alpha_mixer.inputs[0])

		tree.links.new(transp.outputs[0], alpha_mixer.inputs[1])
		tree.links.new(principled.outputs[0], alpha_mixer.inputs[2])
		tree.links.new(alpha_mixer.outputs[0], output.inputs[0])
		alpha_mixer.update()
	# no alpha
	else:
		mat.blend_method = "OPAQUE"
		tree.links.new(principled.outputs[0], output.inputs[0])

	nodes_iterate(tree, output)
	return mat


def create_ob(ob_name, ob_data):
	ob = bpy.data.objects.new(ob_name, ob_data)
	bpy.context.scene.collection.objects.link(ob)
	bpy.context.view_layer.objects.active = ob
	return ob


def mesh_from_data(name, verts, faces, wireframe=True):
	me = bpy.data.meshes.new(name)
	start_time = time.time()
	me.from_pydata(verts, [], faces)
	print(f"from_pydata() took {time.time()-start_time:.2f} seconds for {len(verts)} verts")
	me.update()
	ob = create_ob(name, me)
	# if wireframe:
	# 	ob.draw_type = 'WIRE'
	return ob, me


def get_weights(model):
	dic = {}
	for i, vert in enumerate(model.weights):
		for bone_index, weight in vert:
			if bone_index not in dic:
				dic[bone_index] = {}
			if weight not in dic[bone_index]:
				dic[bone_index][weight] = []
			dic[bone_index][weight].append(i)
	return dic


def import_vertex_groups(ob, model):
	# create vgroups and store weights
	for bone_index, weights_dic in get_weights(model).items():
		try:
			bonename = model.bone_names[bone_index]
		except:
			bonename = str(bone_index)
		bonename = matrix_util.bone_name_for_blender(bonename)
		ob.vertex_groups.new(name=bonename)
		for weight, vert_indices in weights_dic.items():
			ob.vertex_groups[bonename].add(vert_indices, weight/255, 'REPLACE')


def load(operator, context, filepath="", use_custom_normals=False, mirror_mesh=False):
	start_time = time.time()
	in_dir, mdl2_name = os.path.split(filepath)
	bare_name = os.path.splitext(mdl2_name)[0]
	data = load_mdl2(filepath)

	errors = []
	b_armature_obj = import_armature(data)
	created_materials = {}
	# print("data.models",data.models)
	for model_i, model in enumerate(data.models):
		lod_i = model.lod_index
		print("\nmodel_i", model_i)
		print("lod_i", lod_i)
		print("flag", model.flag)
		print("bits", bin(model.flag))
		tris = model.tris
		if model.flag in (1013, 821, 885, 565):
			tris = model.tris[:len(model.tris)//6]
			print("automatically stripped shells from ", model_i)
			num_add_shells = 5
		else:
			num_add_shells = 0
		# create object and mesh from data
		ob, me = mesh_from_data(f"{bare_name}_model{model_i}", model.vertices, tris, wireframe=False)
		# cast the bitfield to int
		ob["flag"] = int(model.flag)
		ob["add_shells"] = num_add_shells

		# additionally keep track here so we create a node tree only once during import
		# but make sure that we overwrite existing materials:
		if model.material not in created_materials:
			mat = create_material(in_dir, model.material)
			created_materials[model.material] = mat
		else:
			print(f"Already imported material {model.material}")
			mat = created_materials[model.material]
		# link material to mesh
		me = ob.data
		me.materials.append(mat)

		# set uv data
		if model.uvs is not None:
			num_uv_layers = model.uvs.shape[1]
			for uv_i in range(num_uv_layers):
				uvs = model.uvs[:, uv_i]
				me.uv_layers.new(name=f"UV{uv_i}")
				me.uv_layers[-1].data.foreach_set("uv", [uv for pair in [uvs[l.vertex_index] for l in me.loops] for uv in (pair[0], 1-pair[1])])

		if model.colors is not None:
			num_vcol_layers = model.colors.shape[1]
			for col_i in range(num_vcol_layers):
				vcols = model.colors[:, col_i]
				me.vertex_colors.new(name=f"RGBA{col_i}")
				me.vertex_colors[-1].data.foreach_set("color", [c for col in [vcols[l.vertex_index] for l in me.loops] for c in col])

		# me.vertex_colors.new(name="tangents")
		# me.vertex_colors[-1].data.foreach_set("color", [c for col in [model.tangents[l.vertex_index] for l in me.loops] for c in (*col, 1,)])
		#
		# me.vertex_colors.new(name="normals")
		# me.vertex_colors[-1].data.foreach_set("color", [c for col in [model.normals[l.vertex_index] for l in me.loops] for c in (*col,1,)])

		mesh_start_time = time.time()

		import_vertex_groups(ob, model)
		print(f"mesh cleanup took {time.time() - mesh_start_time:.2f} seconds")

		# set faces to smooth
		me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
		# set normals
		if use_custom_normals:
			# map normals so we can set them to the edge corners (stored per loop)
			no_array = [model.normals[vertex_index] for face in me.polygons for vertex_index in face.vertices]
			me.use_auto_smooth = True
			me.normals_split_custom_set(no_array)
		# else:
		# # no operator, but bmesh
		# 	bm = bmesh.new()
		# 	bm.from_mesh(me)
		# 	bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
		# 	bm.to_mesh(me)
		# 	me.update()
		# 	bm.clear()
		# 	bm.free()

		bpy.ops.object.mode_set(mode='EDIT')
		if mirror_mesh:
			bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), clear_inner=True)
			bpy.ops.mesh.select_all(action='SELECT')
			mod = ob.modifiers.new('Mirror', 'MIRROR')
			mod.use_clip = True
			mod.use_mirror_merge = True
			mod.use_mirror_vertex_groups = True
			mod.use_x = True
			mod.merge_threshold = 0.001
		bpy.ops.mesh.tris_convert_to_quads()
		# shells are messed up by remove doubles, affected faces have their dupe faces removed
		# since we are now stripping shells, shell meshes can use remove doubles but fins still can not
		if not use_custom_normals and model.flag not in (565, ):
			bpy.ops.mesh.remove_doubles(threshold=0.000001, use_unselected=False)
		try:
			bpy.ops.uv.seams_from_islands()
		except:
			print(ob.name+" has no UV coordinates!")
		bpy.ops.object.mode_set(mode='OBJECT')

		# link to armature, only after mirror so the order is good and weights are mirrored
		if data.ms2_file.bone_info:
			append_armature_modifier(ob, b_armature_obj)
		if model.flag in (1013, 821, 853, 885):
			add_psys(ob)
		# only set the lod index here so that hiding it does not mess with any operators applied above
		matrix_util.to_lod(ob, lod_i)

	print(f"Finished MDL2 import in {time.time()-start_time:.2f} seconds!")
	return errors
