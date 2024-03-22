import os
import hou

class USDmigrationUtils:
    def __init__(self):
        pass

    def extractGLBfile(self, dir_path):
        glb_file = [file for file in os.listdir(dir_path) if file.endswith(".glb")][0]
        print(glb_file)

        #create gltf_hierarchy node in /geo to extract textures
        rootpath = "/obj"
        gltf_hier = hou.node(rootpath).createNode("gltf_hierarchy")
        gltf_hier.parm("filename").set(dir_path + "/" + glb_file)
        gltf_hier.parm("flattenhierarchy").set(1)
        gltf_hier.parm("buildscene").pressButton()
        gltf_hier.destroy()


    def createMainTemplate(self, dir_path):
        print("Executing template structure...")

        glb_file = [file for file in os.listdir(dir_path) if file.endswith(".glb")][0]
        print(glb_file)

        #sopcreate lop node
        root_path = "/stage"
        sopcreate_lop = hou.node(root_path).createNode("sopcreate", "avatar01")
        sopcreate_lop.parm("enable_partitionattribs").set(0)

        #file sop inside sopcreate
        file_sop = hou.node(sopcreate_lop.path() + "/sopnet/create").createNode("gltf")
        file_sop.parm("filename").set(dir_path + "/" + glb_file)
        file_sop.parm("materialassigns").set(1)

        #attribute wrangle to clean 'shop_materialpath'
        attr_wrangle_pre = file_sop.createOutputNode("attribwrangle")
        attr_wrangle_pre.parm("class").set(1)
        attr_wrangle_pre.parm("snippet").set('string inputString = s@shop_materialpath;\nstring parts[] = split(inputString, "_");\nstring lastPart = parts[-1];\ns@shop_materialpath = lastPart;')

        #for loop
        for_each_begin = attr_wrangle_pre.createOutputNode("block_begin", "foreach_begin1")
        for_each_begin.parm("method").set(1)
        for_each_begin.parm("blockpath").set("../foreach_end1")
        for_each_begin.parm("createmetablock").pressButton()
        meta_node = hou.node(for_each_begin.parent().path() + "/foreach_begin1_metadata1")
        meta_node.parm("blockpath").set("../foreach_end1")

        #attribute wrangle
        attr_wrangle = for_each_begin.createOutputNode("attribwrangle")
        attr_wrangle.setInput(1,meta_node)
        attr_wrangle.parm("class").set(1)
        attr_wrangle.parm("snippet").set('string assets[] = {"Body", "Bottom", "Eye", "Footwear", "Hair", "Skin", "Teeth", "Top"};\ns@path = "/" + assets[detail(1,"iteration")];')

        #end loop
        for_each_end = attr_wrangle.createOutputNode("block_end", "foreach_end1")
        for_each_end.parm("itermethod").set(1)
        for_each_end.parm("method").set(1)
        for_each_end.parm("class").set(0)
        for_each_end.parm("useattrib").set(1)
        for_each_end.parm("attrib").set("shop_materialpath")
        for_each_end.parm("blockpath").set("../foreach_begin1")
        for_each_end.parm("templatepath").set("../foreach_begin1")

        #attrib delete
        att_delete = for_each_end.createOutputNode("attribdelete")
        att_delete.parm("vtxdel").set("JOINTS_0 WEIGHTS_0 tangentu")
        att_delete.parm("primdel").set("shop_materialpath name")

        #output
        output_sop = att_delete.createOutputNode("output")
        output_sop.setDisplayFlag(True)

        #create primite lop
        primitive_lop = hou.node(root_path).createNode("primitive")
        primitive_lop.parm("primpath").set("/avatar01")
        primitive_lop.parm("primkind").set("component")

        #graft stages
        graft_stages_lop = primitive_lop.createOutputNode("graftstages")
        graft_stages_lop.setNextInput(sopcreate_lop)
        graft_stages_lop.parm("primkind").set("subcomponent")

        #material library lop with the number of materials
        materials = ["Body", "Bottom", "Eye", "Footwear", "Hair", "Skin", "Teeth", "Top"]
        materiallib_lop = graft_stages_lop.createOutputNode("materiallibrary")
        materiallib_lop.parm("materials").set(len(materials))
        materiallib_lop.setDisplayFlag(True)

        #material lop fill out info
        for i, material in enumerate(materials):
            materiallib_lop.parm(f"matnode{i+1}").set(material)
            materiallib_lop.parm(f"matpath{i+1}").set(f"/avatar01/materials/{material}_mat")
            materiallib_lop.parm(f"assign{i+1}").set(1)
            materiallib_lop.parm(f"geopath{i+1}").set(f"/avatar01/avatar01/{material}")

            #set mat network inside
            mat_network = hou.node(materiallib_lop.path()).createNode("subnet",material)

            #texture maps and nodes
            usd_uv_texture = hou.node(mat_network.path()).createNode("usduvtexture::2.0")
            texture_dir_ref = dir_path + "/glTF_Assets"

            if material == "Body":
                texture_map_color = [file for file in os.listdir(texture_dir_ref) if file.endswith("15_baseColor.jpg")][0]
            elif material == "Bottom":
                texture_map_color = [file for file in os.listdir(texture_dir_ref) if file.endswith("bottom-D.jpg")][0]
            elif material == "Eye":
                texture_map_color = [file for file in os.listdir(texture_dir_ref) if file.endswith("2_baseColor.jpg")][0]
            elif material == "Footwear":
                texture_map_color = [file for file in os.listdir(texture_dir_ref) if file.endswith("footwear-D.jpg")][0]
            elif material == "Hair":
                texture_map_color = [file for file in os.listdir(texture_dir_ref) if file.endswith("4_baseColor.jpg")][0]
            elif material == "Skin":
                texture_map_color = [file for file in os.listdir(texture_dir_ref) if file.endswith("1_baseColor.jpg")][0]
            elif material == "Teeth":
                texture_map_color = [file for file in os.listdir(texture_dir_ref) if file.endswith("Teeth.jpg")][0]
            elif material == "Top":
                texture_map_color = [file for file in os.listdir(texture_dir_ref) if file.endswith("top-D.jpg")][0]
            
            usd_uv_texture.parm("file").set(texture_dir_ref + "/" + texture_map_color)

            mtlsurface = hou.node(mat_network.path()).createNode("mtlxstandard_surface")
            mtlsurface.parm("specular_roughness").set(.7)
            output_ref = hou.node(mat_network.path()+ "/suboutput1")

            usd_uv_texture_output = usd_uv_texture.outputIndex("rgb")
            mtlsurface_input = mtlsurface.inputIndex("base_color")
            mtlsurface_output = mtlsurface.outputIndex("out")

            # Connect 
            mtlsurface.setInput(mtlsurface_input, usd_uv_texture, usd_uv_texture_output)
            output_ref.setNextInput(mtlsurface, mtlsurface_output)
            
            mat_network.setMaterialFlag(True)

        #usd rop export
        asset_name = glb_file[:-4]
        usd_rop_export = materiallib_lop.createOutputNode("usd_rop")
        usd_rop_export.parm("lopoutput").set(dir_path + "/usd_export/" + asset_name + ".usd")
        usd_rop_export.parm("execute").pressButton()
