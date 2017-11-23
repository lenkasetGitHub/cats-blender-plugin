# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: Shotariya
# Repo: https://github.com/Grim-es/shotariya
# Edits by: GiveMeAllYourCats

import bpy

import tools.common
import tools.translate

from mmd_tools import bpyutils
from mmd_tools.core.bone import FnBone
from mmd_tools.translations import DictionaryEnum
import mmd_tools.core.model as mmd_model

import math
import mathutils
import numpy as np
from math import radians
from mathutils import Vector, Matrix


bone_list = ['ControlNode', 'ParentNode', 'Center', 'CenterTip', 'Groove', 'Waist', 'LowerBody2', 'Eyes', 'EyesTip',
             'LowerBodyTip', 'UpperBody2Tip', 'GrooveTip', 'NeckTip']
bone_list_with = ['_shadow_', '_dummy_', 'Dummy_', 'WaistCancel', 'LegIKParent', 'LegIK', 'LegIKTip', 'ToeTipIK',
                  'ToeTipIKTip', 'ShoulderP_', 'EyeTip_', 'ThumbTip_', 'IndexFingerTip_', 'MiddleFingerTip_',
                  'RingFingerTip_', 'LittleFingerTip_', 'HandDummy_', 'ArmTwist', 'HandTwist', 'LegD', 'KneeD_L',
                  'AnkleD', 'LegTipEX', 'HandTip_', 'ShoulderC_', 'SleeveShoulderIK_']

bone_list_parenting = {
    'Head': 'Neck',
    'Neck': 'Chest',
    'Chest': 'Spine',
    'Spine': 'Hips',
    'UpperBody': 'LowerBody',
    'Shoulder_L': 'UpperBody2',
    'Shoulder_R': 'UpperBody2',
    'Arm_L': 'Shoulder_L',
    'Arm_R': 'Shoulder_R',
    'Elbow_L': 'Arm_L',
    'Elbow_R': 'Arm_R',
    'Wrist_L': 'Elbow_L',
    'Wrist_R': 'Elbow_R',
    'LegD_L': 'Leg_L',
    'LegD_R': 'Leg_R',
    'KneeD_L': 'Knee_L',
    'KneeD_R': 'Knee_R',
    'Knee_L': 'Leg_L',
    'Knee_R': 'Leg_R',
    'AnkleD_L': 'Ankle_L',
    'AnkleD_R': 'Ankle_R',
    'Ankle_L': 'Knee_L',
    'Ankle_R': 'Knee_R',
    'LegTipEX_L': 'ToeTip_L',
    'LegTipEX_R': 'ToeTip_R',
    'ToeTip_L': 'Ankle_L',
    'ToeTip_R': 'Ankle_R'
}
bone_list_weight = {
    'LegD_L': 'Left leg',
    'LegD_R': 'Right leg',
    'KneeD_L': 'Left knee',
    'KneeD_R': 'Right knee',
    'AnkleD_L': 'Left ankle',
    'AnkleD_R': 'Right ankle',
    'LegTipEX_L': 'Left toe',
    'LegTipEX_R': 'Right toe',
    'Shoulder_L': 'ShoulderC_L',
    'Shoulder_R': 'ShoulderC_R',
    'Shoulder_L': 'SleeveShoulderIK_L',
    'Shoulder_R': 'SleeveShoulderIK_R',
    'ArmTwist_L': 'Left arm',
    'ArmTwist_R': 'Right arm',
    'ArmTwist1_L': 'Left arm',
    'ArmTwist1_R': 'Right arm',
    'ArmTwist2_L': 'Left arm',
    'ArmTwist2_R': 'Right arm',
    'ArmTwist3_L': 'Left arm',
    'ArmTwist3_R': 'Right arm',
    'HandTwist_L': 'Left elbow',
    'HandTwist_R': 'Right elbow',
    'HandTwist1_L': 'Left elbow',
    'HandTwist1_R': 'Right elbow',
    'HandTwist2_L': 'Left elbow',
    'HandTwist2_R': 'Right elbow',
    'HandTwist3_L': 'Left elbow',
    'HandTwist3_R': 'Right elbow'
}
bone_list_translate = {
    'LowerBody': 'Hips',
    'Leg_L': 'Left leg',
    'Leg_R': 'Right leg',
    'Knee_L': 'Left knee',
    'Knee_R': 'Right knee',
    'Ankle_L': 'Left ankle',
    'Ankle_R': 'Right ankle',
    'ToeTip_L': 'Left toe',
    'ToeTip_R': 'Right toe',
    'UpperBody': 'Spine',
    'UpperBody2': 'Chest',
    'Shoulder_L': 'Left shoulder',
    'Shoulder_R': 'Right shoulder',
    'Arm_L': 'Left arm',
    'Arm_R': 'Right arm',
    'Elbow_L': 'Left elbow',
    'Elbow_R': 'Right elbow',
    'Wrist_L': 'Left wrist',
    'Wrist_R': 'Right wrist'
}


def delete_hierarchy(obj):
    names = {obj.name}

    def get_child_names(objz):
        for child in objz.children:
            names.add(child.name)
            if child.children:
                get_child_names(child)

    get_child_names(obj)
    objects = bpy.data.objects
    [setattr(objects[n], 'select', True) for n in names]

    bpy.ops.object.delete()


class FixArmature(bpy.types.Operator):
    bl_idname = 'armature.fix'
    bl_label = 'Fix armature'

    dictionary = bpy.props.EnumProperty(
        name='Dictionary',
        items=DictionaryEnum.get_dictionary_items,
        description='Translate names from Japanese to English using selected dictionary',
    )

    def execute(self, context):
        bpy.ops.object.hide_view_clear()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        armature = tools.common.get_armature()
        mesh = None

        # Empty objects should be removed
        tools.common.remove_empty()

        # Rigidbodies and joints should be removed
        for obj in bpy.data.objects:
            if obj.name == 'rigidbodies' or obj.name == 'joints':
                delete_hierarchy(obj)
                bpy.data.objects.remove(obj)

        # Model should be in rest position
        armature.data.pose_position = 'REST'

        # Armature should be named correctly
        armature.name = 'Armature'
        armature.data.name = 'Armature'

        # Meshes should be combined
        tools.common.unselect_all()
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                tools.common.select(ob)
        bpy.ops.object.join()

        # Mesh should be renamed to Body
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                ob.name = 'Body'
                mesh = ob

        # Armature should be selected
        tools.common.unselect_all()
        tools.common.select(armature)

        # Do a mmd_tools dictionary translate
        # TODO: L/R suffix should be enabled
        # TODO: underscore must be used instead of dot
        try:
            self.__translator = DictionaryEnum.get_translator(self.dictionary)
        except Exception as e:
            self.report({'ERROR'}, 'Failed to load dictionary: %s'%e)
            return {'CANCELLED'}

        for bone in armature.data.bones:
            bone.name = self.__translator.translate(bone.name)

        # Should reparent all bones to be correct for unity mapping and vrc itself
        bpy.ops.object.mode_set(mode='EDIT')
        for key, value in bone_list_parenting.items():
            pb = armature.pose.bones.get(key)
            pb2 = armature.pose.bones.get(value)
            if pb is None or pb2 is None:
                continue
            armature.data.edit_bones[key].parent = armature.data.edit_bones[value]

        for key, value in bone_list_translate.items():
            pb = armature.pose.bones.get(key)
            if pb is None:
                continue
            pb.name = value

        for bone in armature.data.edit_bones:
            if bone.name in bone_list or bone.name.startswith(tuple(bone_list_with)):
                armature.data.edit_bones.remove(bone)

        # Weights should be mixed
        bpy.ops.object.mode_set(mode='OBJECT')
        tools.common.unselect_all()
        tools.common.select(mesh)
        for key, value in bone_list_weight.items():
            pb = mesh.vertex_groups.get(key)
            pb2 = mesh.vertex_groups.get(value)
            if pb is None or pb2 is None:
                continue
            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
            bpy.context.object.modifiers['VertexWeightMix'].vertex_group_a = value
            bpy.context.object.modifiers['VertexWeightMix'].vertex_group_b = key
            bpy.context.object.modifiers['VertexWeightMix'].mix_mode = 'ADD'
            bpy.context.object.modifiers['VertexWeightMix'].mix_set = 'B'
            bpy.ops.object.modifier_apply(modifier='VertexWeightMix')
            mesh.vertex_groups.remove(pb)

        bpy.ops.object.mode_set(mode='EDIT')
        tools.common.unselect_all()
        tools.common.select(armature)

        # Zero weight bones should be deleted
        if context.scene.remove_zero_weight:
            delete_zero_weight()

        # Bone constraints should be deleted
        if context.scene.remove_constraints:
            delete_bone_constraints()
            
        # Hips bone should be fixed as per specification from the SDK code
        if 'Hips' in armature.data.edit_bones:
            if 'Left leg' in armature.data.edit_bones:
            if 'Right leg' in armature.data.edit_bones:
                hip_bone = armature.data.edit_bones['Hips']
                left_leg = armature.data.edit_bones['Left leg']
                right_leg = armature.data.edit_bones['Right leg']

                # Make sure the left legs (head tip) have the same Y values as right leg (head tip)
                left_leg.head[1] = right_leg.head[1]

                # Make sure the hips bone (tail and head tip) is aligned with the legs Y
                hip_bone.head[1] = right_leg.head[1]
                hip_bone.tail[1] = hip_bone.head[1]

                # Make sure the hips bone is not under the legs bone
                hip_bone.tail[2] = right_leg.head[2]

                left_leg_angle = tools.common.get_bone_angle(hip_bone, left_leg)
                right_leg_angle = tools.common.get_bone_angle(hip_bone, right_leg)

                # Developer print, useful for debugz
                if (left_leg_angle < 5 and right_leg_angle < 5):
                    print('SDK WILL ERROR:', max(left_leg_angle, right_leg_angle), ' degrees for hipbone.. should be as close to 0 as possible')

        # At this point, everything should be fixed and now we validate and give errors if need be

        # The bone hierachy needs to be validated
        hierachy_check_hips = check_hierachy([
            ['Hips', 'Spine', 'Chest', 'Neck', 'Head'],
            ['Hips', 'Left leg', 'Left knee', 'Left ankle'],
            ['Hips', 'Right leg', 'Right knee', 'Right ankle'],
            ['Hips', 'Left shoulder', 'Left arm', 'Left elbow', 'Left wrist'],
            ['Hips', 'Right shoulder', 'Right arm', 'Right elbow', 'Right wrist'],
        ])

        if hierachy_check_hips['result'] is False:
            self.report({'WARNING'}, hierachy_check_hips['message'])
            return {'FINISHED'}

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        self.report({'INFO'}, 'Armature fixed.')
        return {'FINISHED'}

def check_hierachy(correct_hierachy_array):
    armature = tools.common.get_armature()

    for correct_hierachy in correct_hierachy_array:
        for item in correct_hierachy:
            if item in armature.data.edit_bones is False:
                return {'result': False,  'message': item + ' was not found in the hierachy, this will cause problems!'}

        for index, item in enumerate(correct_hierachy):
            try:
                bone = armature.data.edit_bones[item]
            except:
                return {'result': False,  'message': item + ' bone does not exist!'}
            if item is 'Hips':
                # Hips should always be unparented
                if bone.parent is not None:
                    bone.parent = None
            else:
                prevbone = armature.data.edit_bones[correct_hierachy[index - 1]]
                if bone.parent is None:
                    return {'result': False,  'message': bone.name + ' is not parented at all, this will cause problems!'}

                if bone.parent.name != prevbone.name:
                    return {'result': False,  'message': bone.name + ' is not parented to ' + prevbone.name + ', this will cause problems!'}

        return {'result': True}


def delete_zero_weight():
    bpy.ops.object.mode_set(mode='EDIT')
    armature = tools.common.get_armature()
    tools.common.select(armature)

    bone_names_to_work_on = set([bone.name for bone in armature.data.edit_bones])

    bone_name_to_edit_bone = dict()
    for edit_bone in armature.data.edit_bones:
        bone_name_to_edit_bone[edit_bone.name] = edit_bone

    vertex_group_names_used = set()
    vertex_group_name_to_objects_having_same_named_vertex_group = dict()
    for object in armature.children:
        vertex_group_id_to_vertex_group_name = dict()
        for vertex_group in object.vertex_groups:               
            vertex_group_id_to_vertex_group_name[vertex_group.index] = vertex_group.name
            if not vertex_group.name in vertex_group_name_to_objects_having_same_named_vertex_group:
                vertex_group_name_to_objects_having_same_named_vertex_group[vertex_group.name] = set()
            vertex_group_name_to_objects_having_same_named_vertex_group[vertex_group.name].add(object)
        for vertex in object.data.vertices:
            for group in vertex.groups:
                if group.weight > 0:
                    vertex_group_names_used.add(vertex_group_id_to_vertex_group_name[group.group])

    not_used_bone_names = bone_names_to_work_on - vertex_group_names_used

    for bone_name in not_used_bone_names:
        armature.data.edit_bones.remove(bone_name_to_edit_bone[bone_name])  # delete bone
        if bone_name in vertex_group_name_to_objects_having_same_named_vertex_group:
            for objects in vertex_group_name_to_objects_having_same_named_vertex_group[bone_name]:  # delete vertex groups
                vertex_group = object.vertex_groups.get(bone_name)
                if vertex_group is not None:
                    object.vertex_groups.remove(vertex_group)


def delete_bone_constraints():
    bpy.ops.object.mode_set(mode='EDIT')
    armature = tools.common.get_armature()
    tools.common.select(armature)

    bone_names_to_work_on = set([bone.name for bone in armature.data.edit_bones])

    bone_name_to_pose_bone = dict()
    for bone in armature.pose.bones:
        bone_name_to_pose_bone[bone.name] = bone

    bones_worked_on = 0
    constraints_deleted = 0

    for bone_name in bone_names_to_work_on:
        bone = bone_name_to_pose_bone[bone_name]
        if len(bone.constraints) > 0:
            bones_worked_on += 1
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)
                constraints_deleted += 1

def delete_bone_add_weights():
    bpy.ops.object.mode_set(mode='EDIT')
    armature = tools.common.get_armature()
    tools.common.select(armature)

    bone_names_to_work_on = set([bone.name for bone in armature.data.edit_bones])

    bone_name_to_edit_bone = dict()
    for edit_bone in armature.data.edit_bones:
        bone_name_to_edit_bone[edit_bone.name] = edit_bone

    for bone_name_to_remove in bone_names_to_work_on:
        bone_name_to_add_weights_to = bone_name_to_edit_bone[bone_name_to_remove].parent.name
        armature.data.edit_bones.remove(bone_name_to_edit_bone[bone_name_to_remove])  # delete bone

        for object in self._objects_to_work_on:
            vertex_group_to_remove = object.vertex_groups.get(bone_name_to_remove)
            vertex_group_to_add_weights_to = object.vertex_groups.get(bone_name_to_add_weights_to)

            if vertex_group_to_remove is not None:
                if vertex_group_to_add_weights_to is None:
                    vertex_group_to_add_weights_to = object.vertex_groups.add(bone_name_to_add_weights_to)

                for vertex in object.data.vertices:  # transfer weight for each vertex
                        weight_to_transfer = 0
                        for group in vertex.groups:
                            if group.group == vertex_group_to_remove.index:
                                weight_to_transfer = group.weight
                                break
                        if weight_to_transfer > 0:
                            vertex_group_to_add_weights_to.add([vertex.index], weight_to_transfer, "ADD")

                object.vertex_groups.remove(vertex_group_to_remove)  # delete vertex group
