import maya.cmds as mc
import maya.mel as mel
import pymel.core as pm

# menu
if mc.window("ribbon", exists=True):
    mc.deleteUI("ribbon")
RibbonWindow = mc.window("ribbon", t="Geo to Ribbon", w=399, h=50)
mc.gridLayout(nc=1, cwh=[415, 25], w=415, h=400)
mc.radioButtonGrp("Side",l="Side",nrb=2,la2=["left","right"],sl=1)
mc.radioButtonGrp("Primary",l="Primary Axis",nrb=3,la3=["X","Y","Z"],sl=1)
mc.radioButtonGrp("Secondary",l="Secondary Axis",nrb=3,la3=["X","Y","Z"],sl=2)
mc.radioButtonGrp("WorldOrientation",l="World orientation",nrb=3,la3=["X","Y","Z"],sl=3)
mc.radioButtonGrp("Orient",l="Orient",nrb=2,la2=["+","-"],sl=1)
mc.separator()
mc.text("select the upper edge first and the lower edge second")
mc.button(l="select the first edge", c="getEdge1()")
mc.button(l="select the second edge", c="getEdge2()")
mc.textFieldGrp('prefix', l='write the prefix')
mc.intSliderGrp('numCtrl', l='number of ctrls', f=1, v=3, min=3)
mc.button(l="create ribbon", c="ribbon()")
mc.showWindow()

# declare the edges
edge1 = []

def getEdge1():
    edge1.clear()
    sel = mc.ls(sl=True)
    edge1.extend(sel)

edge2 = []

def getEdge2():
    edge2.clear()
    sel = mc.ls(sl=True)
    edge2.extend(sel)

# def ribbon command

def ribbon():
    # variable declaration
    numCtrls = mc.intSliderGrp('numCtrl', q=1, v=1)
    prefixName = mc.textFieldGrp('prefix', tx=1, q=1)
    PrimaryAxisNum = mc.radioButtonGrp('Primary',q=1,sl=1)
    SecondaryAxisNum = mc.radioButtonGrp('Secondary',q=1,sl=1)
    WorldOrientNum = mc.radioButtonGrp('WorldOrientation',q=1,sl=1)
    OrientNum = mc.radioButtonGrp('Orient',q=1,sl=1)
    Side = mc.radioButtonGrp('Side',q=1,sl=1)
    axis = ["x","y","z"]
    PrimaryAxis = []
    PrimaryAxis.append(axis[PrimaryAxisNum-1])
    SecondaryAxis = []
    SecondaryAxis.append(axis[SecondaryAxisNum-1])
    
    WorldOrient = []
    WorldOrient.append(axis[WorldOrientNum-1])
    orientation = ["up","down"]
    orient = []
    orient.append(orientation[OrientNum-1])
    axis.remove(PrimaryAxis[0])
    axis.remove(SecondaryAxis[0])
    
    mc.select(edge1,r=1)
    curveTest = mel.eval("polyToCurve -form 2 -degree 1 -conformToSmoothMeshPreview 1;")
    sizeCurve = mc.getAttr(curveTest[0]+".spans")
    mc.delete(curveTest)
    # verify if there is more ctrl than bind joints
    if numCtrls > sizeCurve:
        print("you cant have more ctrl than the number of edge on your ribbon")
    else:
        #create the groups
        mainGroup = mc.group(em=1,n=prefixName+"_grp")
        jntGroup = mc.group(em=1,n=prefixName+"Jnt_grp")
        componentGroup = mc.group(em=1,n=prefixName+"Components_grp")
        ctrlGroup = mc.group(em=1,n=prefixName+"Ctrl_grp")
        mc.parent(jntGroup,mainGroup)
        mc.parent(componentGroup,mainGroup)
        mc.parent(ctrlGroup,mainGroup)
        
        # make the nurbs
        mc.select(edge1, r=1)
        curve1 = mel.eval("polyToCurve -form 2 -degree 3 -conformToSmoothMeshPreview 1;")
        mc.select(edge2, r=1)
        curve2 = mel.eval("polyToCurve -form 2 -degree 3 -conformToSmoothMeshPreview 1;")
        mc.select(curve1, curve2, r=1)
        mc.loft(ch=1,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0)
        ribbonLoft = mc.rename(prefixName + "_ribbon")
        mc.select(curve1, r=1)
        # declare the lenght of the curve in mel
        mel.eval("$Org =`ls -sl`;")
        mel.eval(' string $lenghtCurve = `getAttr ($Org[0] + ".spans")`;')
        lenghtCurve = mc.getAttr(curve1[0]+".spans")
        ctrlDiv = lenghtCurve / (numCtrls - 1)
        
        mc.delete(curve1, curve2)
        # make the nHair
        mc.select(ribbonLoft, r=1)
        mel.eval("$name =`ls -sl`;")
        lenghtCurved = lenghtCurve +1
        mc.select(cl=1)
        for _ in range(lenghtCurved):
            num = str(_)
            mc.select(ribbonLoft+".uv[0.5][" + num +"]",add=1)

        mel.eval("createHair 1 $lenghtCurve 2 0 0 1 0 0.4898 0 1 1 2;")
        # delete crap
        if mc.objExists("hairSystem?"):
            mc.delete("hairSystem?")
        if mc.objExists("pfxHair?"):
            mc.delete("pfxHair?")
        if mc.objExists("nucleus?"):
            mc.delete( "nucleus?")
        # rename follicles and create the bind joints
        mc.select("hairSystem?Follicles", r=1)
        folGrp = mc.rename(prefixName + "Fol_grp")
        mc.select(hi=1)
        mc.pickWalk(d='up')
        mc.select(folGrp, d=1)
        fol = mc.ls(sl=1)
        mc.pickWalk(d='down')
        mc.pickWalk(d='right')
        mc.delete()
        fols = []
        for node in fol:
            mc.select(node, r=1)
            renamedFol = mc.rename(prefixName + "_Follicle01")
            fols.append(renamedFol)

        Fols = []
        for node in fols:
            mc.joint(n=node + "_bJnt")
            jnt = mc.ls(sl=1)
            mc.matchTransform(jnt,node)
            mel.eval("FreezeTransformations;")
            #mc.select(node, r=1)
            #mc.select(jnt, add=1)
            
            #prnt = mc.parentConstraint()
            #mc.delete(prnt)
            mc.parent(jnt, node)
            #mc.matchTransform(jnt,node)
            Fols.extend(jnt)

        
        #orient the joints
        FolsLength = len(Fols)
        for _ in range(FolsLength):
            if _ == 0 :
                mc.select(Fols[_],Fols[_+1],r=1)
                clone = mc.duplicate()
                if Side == 1:
                    mc.parent(clone[0],clone[1])
                    mc.select(clone[1],r=1)
                else:
                    mc.parent(clone[1],clone[0])
                    mc.select(clone[0],r=1)
                
                crap =PrimaryAxis[0]+SecondaryAxis[0]+axis[0]
                oas = WorldOrient[0]+orient[0]
                print(crap)
                print(oas)
                
                mc.joint(e=1,oj=crap,sao=oas)
                orientJoint = mc.joint(q=1,o=1)
                mc.delete(clone)
                
                mc.select(Fols[_],r=1)
                mc.joint(e=1,o=orientJoint)
            else:
                mc.select(Fols[_-1],Fols[_],r=1)
                clone = mc.duplicate()
                if Side == 1:
                    mc.parent(clone[0],clone[1])
                    mc.select(clone[1],r=1)
                else:
                    mc.parent(clone[1],clone[0])
                    mc.select(clone[0],r=1)
                
                crap =PrimaryAxis[0]+SecondaryAxis[0]+axis[0]
                oas = WorldOrient[0]+orient[0]
                print(crap)
                print(oas)
                
                mc.joint(e=1,oj=crap,sao=oas)
                orientJoint = mc.joint(q=1,o=1)
                mc.delete(clone)
                
                mc.select(Fols[_],r=1)
                mc.joint(e=1,o=orientJoint)
        mc.select(Fols, r=1)
        Name = mc.ls(sl=1)
        newNamed = []
        for node in Name:
            mc.select(node, r=1)
            renamed = pm.ls(sl=1)
            for node in renamed:
                name = node.nodeName().replace("_Follicle", "")
                node.rename(name)
            new = mc.ls(sl=1)
            
            newNamed.extend(new)

            # print(new)
        # create the drv joint
        drvJnt = []
        loc = []
        ctrls = []
        groups = []
        for _ in range(numCtrls):
            trueNum = (_ + 1)
            strNum = str(trueNum)
            location = []
            if _ == 0:
                locRef = int(_ * ctrlDiv)
                location.clear()
                location.append(locRef)
            else:
                locRef = int(_ * ctrlDiv)
                location.clear()
                location.append(locRef)

            currentLocation = newNamed[locRef]
            #print(currentLocation)
            mc.select(cl=1)
            jnt = mc.joint(n=prefixName + strNum + "_drvJnt")
            mc.parent(jnt,jntGroup)
            mc.matchTransform(jnt,currentLocation)
            mc.select(jnt,r=1)
            mc.select(currentLocation,add=1)
            mc.scaleConstraint()
            
            ctrl = mc.circle(n=prefixName+strNum+"Drv_ctrl")
            grp = mc.group(n= ctrl[0]+"_srtBuffer")
            mc.parent(grp,ctrlGroup)
            mc.matchTransform(grp,jnt)
            mc.select(ctrl[0],r=1)
            mel.eval("DeleteHistory;")
            mc.select(jnt,add=1)
            mc.parentConstraint()
            mc.scaleConstraint()
            mc.select(cl=1)
            
            loc1 = mc.xform(newNamed[0],q=1,ws=1,t=1)
            loc2 = mc.xform(newNamed[1],q=1,ws=1,t=1)
            crv = mc.curve(d=1,p=[(loc1[0],loc1[1],loc1[2]),(loc2[0],loc2[1],loc2[2])])
            leng = int(mc.arclen(crv))
            mc.delete(crv)
            
            #change the look of the ctrl
            mc.select(ctrl[0]+".cv[0:7]",r=1)
            mc.rotate(90,x=1)
            mc.scale(leng*2,leng*2,leng*2)
            
            #append the variable out of the loop
            groups.append(grp)
            ctrls.append(ctrl)
            drvJnt.append(jnt)
            loc.extend(location)
            mc.select(cl=1)
        
        #scale constraint for range in between driver jnts
        rangeScale = numCtrls -1
        for _ in range(rangeScale):
            num1 = _
            num2 = _ + 1
            trueNum1 = loc[num1]
            trueNum2 = loc[num2]
            rangeNum1 = trueNum1 + 1
            rangeNum2 = trueNum2 - 1
            loopRange = range(rangeNum1, trueNum2)
            truelen = len(loopRange)
            TrueRange = range(trueNum1, trueNum2)
            for _ in range(truelen):
                multiplier = _ + 1
                rangeNum = TrueRange[_] +1
                trueLength = rangeNum2 - rangeNum1 + 2
        
                #print(multiplier)
                num1Percent = 1 / trueLength
                firstPercent = multiplier * num1Percent
                num2Percent = 1 - firstPercent
                jnt = newNamed[rangeNum]
                mc.select(drvJnt[num1],r=1)
                mc.select(jnt,add=1)
                mc.scaleConstraint(w=num2Percent)
                mc.select(drvJnt[num2],r=1)
                mc.select(jnt,add=1)
                mc.scaleConstraint(w=firstPercent)
                #print(drvJnt[num1])        
                #print(jnt)
                #print(drvJnt[num2])
                #print(num2Percent)
        
        mc.parent(folGrp,componentGroup)
        mc.parent(ribbonLoft,componentGroup)
        mc.select(drvJnt,r=1)
        mc.select(ribbonLoft,add=1)
        mc.skinCluster(inf=2,n=prefixName+"_skinCluster")
