# testcases design

> Kevin  
> 26/11/13  

## 说明

本文档是我设计的一些 testcases，用于对本项目进行实验

说实话按照这个模型的设计，主要就是对图像进行微调，并不会进行大面积的修改工作，但是我还是想看看整体的效果如何

所以整体来说，测试点主要会分为以下的几个部分：

普通测试点：或者接近于示例的那几个测试点，检查模型是否真的如paper所说有这么好的效果

极端测试点：精心设计的普通测试点，使用我认为的边界case进行测试，看看模型整体的抗压能力

边界测试点：这里说实话没有完全想好，因为小模型主要负责的是微调，而不是大面积调整，但是我依然想看大面积进行修改的效果如何，看看会不会有惊喜

## 普通测试点

部分图片以及提示词出处：

https://chordedit.github.io/

当然这些case设计的不一定合理，同时数量也不算特别多，但是下面都是我自己设计的，蛮有意思的

后续 AI 可以进行补充，或者提出一些修改意见什么的

### case 1_1

样例图片 1

a dog looking at the camera -> a dog with a red dog collar looking at the camera

### case 1_2

样例图片 2

a white car driving -> a stripe car driving

### case 1_3

样例图片 3（提示词修改，lion -> cat）

a cup of coffee with drawing of tulip -> a cup of coffee with drawing a cat

### case 1_4

自编

a girl with brown hair -> a girl with golden hair

### case 1_5

自编

a table with an opening macbook air on it -> a table with a closed macbook air on it

## 极端测试点

### case 2_1

自编

a girl with brown hair holding a white cat -> a girl with brown hair holding a green cat

### case 2_2

自编，说实话感觉有点简单，放进普通测试点也行

a boy with blonde hair holding a black dog -> a girl with blonde hair holding a black dog

### case 2_3

自编，到时候翻译成英文

一只在食指上佩戴钻石戒指的右手 -> 一只在中指上佩戴黄金戒指的右手

### case 2_4

自编，到时候翻译成英文

一只在食指上佩戴钻石戒指的右手 -> 一只在中指上佩戴黄金戒指的左手

### case 2_5

自编

a smiling girl -> a whiping girl

### case 2_6

自编

a book named "Harry Potter" -> a book named "the lord of rings"

## 边界测试点

### case 3_1

自编

pure black background -> add a dog on it

### case 3_2

自编，应该需要增加一些细节，意思差不多

a sunny day near the lake -> a bright night near the lake

### case 3_3

自编

a library with thousands of books -> a playground with dozens of kids

### case 3_4

自编

a busy kitchen -> a quite bedroom

## AI 设计的经典图片编辑 case

> 以下 case 全部为 AI 设计，建议为每个 case 准备一张与 source prompt 真实匹配的原图，并固定 source/target prompt 的句式。每个 case 最好用多个 seed 重复，不要只凭一张输出下结论。

### A. 局部属性与附件编辑

#### AI-case A1：物体颜色变化

`a red ceramic mug on a wooden table -> a blue ceramic mug on the same wooden table`

观察重点：杯子形状、位置、桌面纹理和光照是否保持；这是最适合做基础 sanity check 的局部编辑。

#### AI-case A2：添加可穿戴附件

`a golden retriever sitting on a lawn -> a golden retriever wearing a blue bandana, sitting on the same lawn`

观察重点：是否只在狗颈部增加 bandana，狗的姿态、草地和背景是否发生泄漏。

#### AI-case A3：移除附件

`a woman wearing round sunglasses in a city street -> a woman without sunglasses in the same city street`

观察重点：眼睛、眉毛和面部结构是否自然恢复；这是“删除”方向，可能比添加更不稳定。

### B. 物体状态、材质和身份编辑

#### AI-case B1：状态改变

`a red umbrella opened beside a park bench -> a red umbrella closed beside the same park bench`

观察重点：伞的开合、杆的位置和手/地面接触关系；适合测试结构变化而非简单颜色变化。

#### AI-case B2：材质替换

`a wooden chair in a bright room -> a metal chair in the same bright room`

观察重点：木纹是否消失、金属高光是否合理，以及房间背景和椅子轮廓是否保持。

#### AI-case B3：同位置物体替换

`a tabby cat sitting on a sofa -> a small brown dog sitting in the same position on the same sofa`

观察重点：动物身份是否真正改变，同时保留坐姿、构图、沙发和光照；这是经典 object replacement。

### C. 几何关系和数量编辑

#### AI-case C1：空间关系变化

`a coffee cup beside an open book on a desk -> a coffee cup on top of the open book on the same desk`

观察重点：杯子与书的遮挡关系、接触阴影和书页结构；这是比颜色编辑更能暴露空间一致性问题的 case。

#### AI-case C2：数量变化

`one red apple on a white plate -> three red apples on the same white plate`

观察重点：新增物体是否完整、遮挡关系是否合理、盘子和桌面是否被无关改动。该 case 属于中等强度编辑。

#### AI-case C3：人物表情变化

`a close-up portrait of a young woman with a neutral expression -> a close-up portrait of the same young woman smiling`

观察重点：身份、眼睛和发型保持程度，以及嘴部变化是否自然；应避免 source 图像本来就带有明显笑容。

### D. 全局属性与风格编辑

#### AI-case D1：季节变化

`a small wooden cabin beside a lake in summer -> the same wooden cabin beside a frozen lake in winter, with snow-covered trees`

观察重点：这是全局编辑，不应只看目标语义，还要记录背景保真度下降；可用于测试 ChordEdit 的适用边界。

#### AI-case D2：时间与光照变化

`a city park in bright daylight -> the same city park at night under warm street lights`

观察重点：建筑、道路和树木结构是否保留，夜景照明是否覆盖合理；与单个物体编辑分开统计。

#### AI-case D3：艺术风格变化

`a realistic photograph of a bicycle leaning against a brick wall -> a watercolor painting of the same bicycle leaning against the same brick wall`

观察重点：构图和主体是否保留，同时风格是否真正变化；不要把风格变化后的像素差直接当作背景破坏。

### E. 经典困难 case

#### AI-case E1：文字内容变化

`a storefront with a blank sign above the door -> a storefront with the word CAFE clearly written on the sign above the door`

观察重点：文字可读性、拼写正确率、招牌位置和透视。文字编辑通常是生成模型的困难项，应单独报告，不宜与普通颜色编辑混合平均。

#### AI-case E2：手部拓扑与左右方向

`a close-up of a right hand, palm facing the camera, wearing a diamond ring on the index finger -> a close-up of the same right hand, palm facing the camera, wearing a gold ring on the middle finger`

观察重点：手指数量、左右手、戒指材质和具体手指位置。该 case 对空间关系很敏感，建议作为极端 case，而不是普通基线。

#### AI-case E3：反射一致性

`a red sports car parked beside a calm lake -> a blue sports car parked beside the same lake, with the blue car reflected consistently in the water`

观察重点：车身颜色是否修改，同时水面倒影是否同步；可以检验编辑是否只影响显著主体而忽略其关联区域。



