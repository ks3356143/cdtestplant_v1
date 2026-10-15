// 该文件导出一些常量以及文档片段预制文档名称
enum fragmentName {
    NotSelect = "不使用模版(X)",
    TestObject = "测评对象",
    StaticEnv = "静态测试环境说明",
    StaticSoft = "静态软件项",
    StaticHard = "静态硬件和固件项",
    DynamicEnv = "动态测试环境说明",
    DynamicSoft = "动态软件项",
    DynamicHard = "动态硬件和固件项",
    TestData = "测评数据",
    EnvDiff = "环境差异性分析",
    TestLevelAndType = "测试级别和测试类型",
    TestStrategy = "测试策略"
}

export { fragmentName }

// TestObject-测评对象模版
export const TestObjectHTML = `<p>CX-3E(01/02/03)ZCL数据处理机主要用于接收星上载荷3台广域监视相机和1台精密跟踪相机的原始数据并实时处理，完成目标在轨检测、图像定位、天文定位以及目标异动识别。</p>
<p>广域图像处理机、广域精跟图像处理机主要用于接收相机的图像数据，进行图像处理并将数据处理结果转发至天文定位数据处理机。数据处理分系统的连接关系如图所示：</p>
<p><img style="display: block; margin-left: auto; margin-right: auto;" src="" width="400" height="300" ></p>
<p style="text-align: center;">图<!-- [if supportFields]> STYLEREF 1 \s <![endif]-->5<!-- [if supportFields]><![endif]-->‑<!-- [if supportFields]> SEQ 图 \* ARABIC \s 1 <![endif]-->1数据处理分析系统连接关系图</p>
<p style="text-align: left;">图像处理机分为广域图像处理机和广域精跟图像处理机，硬件和软件均做统型设计，硬件按照最大接口包络设计，软件通过BOOT_FLAG标示，识别当前为广域处理机或者精跟处理机；其中广域图像处理机为2路2711图像输入，接收6个DSP的图像处理结果；精跟图像处理机为1路2711图像输入，1路LVDS图像输入，接收4个DSP的图像处理结果；接口管理FPGA通过BOOT_FLAG选通两路数据作为图像输入源，在接口管理FPGA内部，两路图像数据通道完全独立，独立的处理数据并通过各自独立的SRIO发送出去，接口管理FPGA交联图如下：</p>
<p style="text-align: left;"><img style="display: block; margin-left: auto; margin-right: auto;" src="" width="684" height="370"></p>
<p style="text-align: center;">图<!-- [if supportFields]> STYLEREF 1 \s <![endif]-->5<!-- [if supportFields]><![endif]-->‑<!-- [if supportFields]> SEQ 图 \* ARABIC \s 1 <![endif]-->1接口管理FPGA外部交联图</p>
<p>接口管理FPGA主要完成以下功能：</p>
<p>1）通过EMIF接口与处理器进行数据传输；</p>
<p>2）接口管理FPGA通过2711/LVDS接口接收广域/精跟相机的图像数据，并通过SRIO转发至FPGA计算节点；FPGA提供异步串口接口，由处理器控制，实现与各个计算节点的遥控遥测数据传输；</p>
<p>3）接收DSP计算节点的IPD数据和图像处理日志，并通过LVDS接口发送至天文定位数据处理机；</p>
<p>4）控制AD采集芯片SAD0832的时序，周期性完成各个计算节点的电压采集，由处理器读取结果；</p>
<p>5）控制SPI FLASH时序，可以根据处理器指令提取相应位置的配置文件，实现对不同计算节点的原始配置文件重构，能够根据处理器指令要求，缓存新的配置文件；</p>
<p>6）模拟LSMEU03的JTAG时序，实现对LSMEU03的上注功能；</p>
<p>7）OC指令输出功能；</p>
<p style="text-align: left;">8）状态检测等功能；</p>`

export const StaticEnvHTML = `<p>静态测试环境由1台测试计算机组成，测试计算机部署了Klocwork、Understand、Testbed等软件，对被测软件文档、源代码开展文档审查、静态分析、代码审查、代码走查等静态测试。</p>
<p><img style="display: block; margin-left: auto; margin-right: auto;" src="" width="447" height="196"></p>
<p style="text-align: center;">图5.4静态测试环境示意图</p>`

export const StaticSoftHTML = `<p>此次软件静态测试环境使用的软件项见下表。</p>
<p style="text-align: center;">表5-5静态测评环境软件项</p>
<div align="center">
<table border="1" width="100%" cellspacing="0" cellpadding="0">
<thead>
<tr>
<td width="6%">
<p align="center">序号</p>
</td>
<td width="24%">
<p align="center">软件项名称</p>
</td>
<td width="14%">
<p align="center">版本</p>
</td>
<td width="23%">
<p align="center">提供单位</p>
</td>
<td width="31%">
<p align="center">用途</p>
</td>
</tr>
</thead>
<tbody>
<tr>
<td width="6%">
<p align="center">1&nbsp;</p>
</td>
<td width="24%">
<p align="center">XXXX软件</p>
</td>
<td width="14%">
<p>VX.X</p>
</td>
<td rowspan="8" width="23%">
<p>中国科学院卫星软件评测中心</p>
</td>
<td width="31%">
<p>被测软件</p>
</td>
</tr>
<tr>
<td width="6%">
<p align="center">2&nbsp;</p>
</td>
<td width="24%">
<p align="center">Klocwork</p>
</td>
<td width="14%">
<p>V2018</p>
</td>
<td width="31%">
<p>用于运行错误检测</p>
</td>
</tr>
<tr>
<td width="6%">
<p align="center">3&nbsp;</p>
</td>
<td width="24%">
<p>Testbed</p>
</td>
<td width="14%">
<p>V9.4</p>
</td>
<td width="31%">
<p>用于静态分析</p>
</td>
</tr>
<tr>
<td width="6%">
<p align="center">4&nbsp;</p>
</td>
<td width="24%">
<p>Understand</p>
</td>
<td width="14%">
<p>V5.0</p>
</td>
<td width="31%">
<p>用于静态分析、质量度量</p>
</td>
</tr>
<tr>
<td width="6%">
<p align="center">5&nbsp;</p>
</td>
<td width="24%">
<p align="center">Source Insight</p>
</td>
<td width="14%">
<p>V4.0</p>
</td>
<td width="31%">
<p>阅读代码工具</p>
</td>
</tr>
<tr>
<td width="6%">
<p align="center">6&nbsp;</p>
</td>
<td width="24%">
<p align="center">Beyond Compare</p>
</td>
<td width="14%">
<p>V4.4</p>
</td>
<td width="31%">
<p>代码对比工具</p>
</td>
</tr>
<tr>
<td width="6%">
<p align="center">7&nbsp;</p>
</td>
<td width="24%">
<p align="center">SourceCounter</p>
</td>
<td width="14%">
<p>V3.4.16.85</p>
</td>
<td width="31%">
<p>代码行统计工具</p>
</td>
</tr>
<tr>
<td width="6%">
<p align="center">8&nbsp;</p>
</td>
<td width="24%">
<p align="center">Microsoft Office</p>
</td>
<td width="14%">
<p>2016</p>
</td>
<td width="31%">
<p>文档阅读、编辑工具</p>
</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: left;">&nbsp;</p>`

export const StaticHardHTML = `<p>此次静态测试环境使用的硬件和固件项详见下表所示。</p>
<p style="text-align: center;">表<!-- [if supportFields]><b
style='mso-bidi-font-weight:normal'></b> STYLEREF 1 \s <b
style='mso-bidi-font-weight:normal'></b><![endif]-->5<!-- [if supportFields]><b
style='mso-bidi-font-weight:normal'></b><![endif]-->‑<!-- [if supportFields]><b
style='mso-bidi-font-weight:normal'></b> SEQ 表 \* ARABIC \s 1 <b style='mso-bidi-font-weight:normal'></b><![endif]-->6<!-- [if supportFields]><b
style='mso-bidi-font-weight:normal'></b><![endif]--> 静态测评环境硬件和固件项</p>
<div align="center">
<table border="1" width="100%" cellspacing="0" cellpadding="0">
<thead>
<tr>
<td width="6%">
<p align="center">序号</p>
</td>
<td width="11%">
<p align="center">硬件或固件项名称</p>
</td>
<td width="23%">
<p align="center">配置信息</p>
</td>
<td width="14%">
<p align="center">设备编号</p>
</td>
<td width="16%">
<p align="center">提供单位</p>
</td>
<td width="26%">
<p align="center">用途</p>
</td>
</tr>
</thead>
<tbody>
<tr>
<td width="6%">
<p align="center">1&nbsp;</p>
</td>
<td width="11%">
<p>计算机</p>
</td>
<td width="23%">
<p>CPU:intel i7 6700</p>
<p>内存：16G</p>
<p>硬盘：500G</p>
<p>操作系统：Windows 7(64)</p>
</td>
<td width="14%">
<p>TY20191200277</p>
</td>
<td width="16%">
<p>中国科学院卫星软件评测中心</p>
</td>
<td width="26%">
<p>运行Klocwork、Source Insight等测试工具以及相关辅助软件，用于静态测试。</p>
</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: center;">&nbsp;</p>`

export const DynamicEnvHTML = `<p>实物测试环境1的测试设备包括广域图像处理机、测试计算机（含2711发送板卡和LVDS接收发送板卡）、电源。广域精跟图像处理机接口管理FPGA软件运行于广域图像处理机；广域精跟地面应用软件、上注软件运行于测试计算机结合用于模拟2711相机源，发送广域图像数据；模拟天文处理机，接收处理后的IPD和日志信息；模拟星务发送上注指令，接收遥测信息。软件实物测试环境图如下图所示。</p>
<p>在广域精跟地面应用软件模拟2711相机源，发送广域图像，通过2711发送板卡给输入广域图像处理机，广域图像处理机再通过LVDS接收发送板卡接收处理后图像，并发送给广域精跟地面应用软件。在广域精跟地面应用软件向广域图像处理机发送控制指令（节点配置、软复位、串口数据等），并查看下传的遥测数据。通过上注软件进行程序上注，并接收下传测遥测信息。</p>
<p><img style="display: block; margin-left: auto; margin-right: auto;" src="" width="798" height="313"></p>
<p style="text-align: center;">图5-2图像处理机接口管理FPGA软件测试环境1示意图</p>`

export const DynamicSoftHTML = `<p>图像处理机接口管理FPGA软件配置项实物测试环境1使用的软件项见<!-- [if supportFields]> REF _Ref175830279 \h  \* MERGEFORMAT <![endif]-->表5‑13<!-- [if gte mso 9]><xml>
 <w:data>08D0C9EA79F9BACE118C8200AA004BA90B02000000080000000E0000005F005200650066003100370035003800330030003200370039000000</w:data>
</xml><![endif]--><!-- [if supportFields]><![endif]-->所示。</p>
<p style="text-align: center;">表5-7实物测试环境1软件项</p>
<div align="center">
<table border="1" width="100%" cellspacing="0" cellpadding="0">
<thead>
<tr>
<td width="6%">
<p align="center">序号</p>
</td>
<td width="22%">
<p align="center">软件项名称</p>
</td>
<td width="18%">
<p align="center">版本</p>
</td>
<td width="21%">
<p align="center">提供单位</p>
</td>
<td width="31%">
<p align="center">用途</p>
</td>
</tr>
</thead>
<tbody>
<tr>
<td width="6%">
<p align="center">1&nbsp;</p>
</td>
<td width="22%">
<p align="center">XX系统软件</p>
</td>
<td width="18%">
<p>静态测评结束后版本</p>
</td>
<td width="21%">
<p>XX单位</p>
</td>
<td width="31%">
<p>被测软件</p>
</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: center;">&nbsp;</p>`

export const DynamicHardHTML = `<p>图像处理机接口管理FPGA软件配置项测试环境1使用的硬件和固件项见下表所示。</p>
<p style="text-align: center;">表5-8实物测试环境1硬件和固件项</p>
<div align="center">
<table style="height: 609.853px; width: 85.5195%;" border="1" cellspacing="0" cellpadding="0">
<thead>
<tr style="height: 29.5952px;">
<td style="width: 8.74796%;" width="39">
<p align="center">序号</p>
</td>
<td style="width: 13.6554%;" width="84">
<p align="center">硬件或固件项名称</p>
</td>
<td style="width: 21.3365%;" width="132">
<p align="center">配置信息</p>
</td>
<td style="width: 11.9484%;" width="73">
<p align="center">设备标识</p>
</td>
<td style="width: 12.4829%;" width="87">
<p align="center">检定有效期</p>
</td>
<td style="width: 13.761%;" width="76">
<p align="center">提供单位</p>
</td>
<td style="width: 17.9227%;" width="112">
<p align="center">用途</p>
</td>
</tr>
</thead>
<tbody>
<tr style="height: 115.565px;">
<td style="width: 8.74796%;" width="39">
<p align="center">1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td style="width: 13.6554%;" width="84">
<p>XX设备（含被测软件）</p>
</td>
<td style="width: 21.3365%;" width="132">
<p>设备型号：XX</p>
<p>设备配置：XX</p>
<p>运行软件：XX、XX</p>
<p>（如果有多套应说明套数）</p>
</td>
<td style="width: 11.9484%;" width="73">
<p>&nbsp;</p>
</td>
<td style="width: 12.4829%;" width="87">
<p>2023.08.11～2025.08.10</p>
</td>
<td style="width: 13.761%;" width="76">
<p>XX单位</p>
</td>
<td style="width: 17.9227%;" width="112">
<p>XX为被测设备</p>
</td>
</tr>
<tr style="height: 115.565px;">
<td style="width: 8.74796%;" width="39">
<p align="center">2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td style="width: 13.6554%;" width="84">
<p>YY设备</p>
</td>
<td style="width: 21.3365%;" width="132">
<p>设备型号：XX</p>
<p>设备配置：XX</p>
<p>运行软件：XX、XX</p>
<p>（如果有多套应说明套数）</p>
</td>
<td style="width: 11.9484%;" width="73">
<p>&nbsp;</p>
</td>
<td style="width: 12.4829%;" width="87">
<p>检定日期：2023.08.11</p>
<p>有效期：3年</p>
</td>
<td style="width: 13.761%;" width="76">
<p>XX单位</p>
</td>
<td style="width: 17.9227%;" width="112">
<p>真实陪测设备，用来与被测设备进行XX接口的数据通信</p>
</td>
</tr>
<tr style="height: 138.552px;">
<td style="width: 8.74796%;" width="39">
<p align="center">3&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td style="width: 13.6554%;" width="84">
<p>ZZ综合测试设备</p>
</td>
<td style="width: 21.3365%;" width="132">
<p>设备标识：XX</p>
<p>设备型号：XX</p>
<p>设备配置：XX</p>
<p>运行软件：XX、XX</p>
<p>（如果有多套应说明套数）</p>
</td>
<td style="width: 11.9484%;" width="73">
<p>&nbsp;</p>
</td>
<td style="width: 12.4829%;" width="87">
<p>&nbsp;</p>
</td>
<td style="width: 13.761%;" width="76">
<p>XX单位</p>
</td>
<td style="width: 17.9227%;" width="112">
<p>模拟发送 XX接口数据</p>
</td>
</tr>
<tr style="height: 92.5794px;">
<td style="width: 8.74796%;" width="39">
<p align="center">4&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td style="width: 13.6554%;" width="84">
<p>示波器</p>
</td>
<td style="width: 21.3365%;" width="132">
<p>设备型号：XX</p>
<p>设备配置：XX</p>
<p>（如果有多套应说明套数）</p>
</td>
<td style="width: 11.9484%;" width="73">
<p>&nbsp;</p>
</td>
<td style="width: 12.4829%;" width="87">
<p>&nbsp;</p>
</td>
<td style="width: 13.761%;" width="76">
<p>XX单位</p>
</td>
<td style="width: 17.9227%;" width="112">
<p>测量定时器采样周期</p>
</td>
</tr>
<tr style="height: 117.996px;">
<td style="width: 8.74796%;" width="39">
<p align="center">5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td style="width: 13.6554%;" width="84">
<p>工控机</p>
</td>
<td style="width: 21.3365%;" width="132">
<p>设备型号：XX</p>
<p>设备配置：XX</p>
<p>运行软件：XX、XX</p>
<p>（如果有多套应说明套数）</p>
</td>
<td style="width: 11.9484%;" width="73">
<p>&nbsp;</p>
</td>
<td style="width: 12.4829%;" width="87">
<p>&nbsp;</p>
</td>
<td style="width: 13.761%;" width="76">
<p>XX单位</p>
</td>
<td style="width: 17.9227%;" width="112">
<p>运行 XX软件模拟 XX</p>
</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: center;">&nbsp;</p>`

export const TestDataHTML = `<p>图像处理机接口管理FPGA软件配置项测试所需的测评数据详见<!-- [if supportFields]> REF _Ref175830319 \h  \* MERGEFORMAT <![endif]-->下表<!-- [if gte mso 9]><xml>
 <w:data>08D0C9EA79F9BACE118C8200AA004BA90B02000000080000000E0000005F005200650066003100370035003800330030003300310039000000</w:data>
</xml><![endif]--><!-- [if supportFields]><![endif]-->所示。</p>
<p style="text-align: center;">表5-9测评数据</p>
<div align="center">
<div align="center">
<div align="center">
<table border="1" width="604" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td valign="top" width="45">
<p align="center">序号</p>
</td>
<td valign="top" width="136">
<p align="center">数据描述</p>
</td>
<td valign="top" width="69">
<p align="center">性质</p>
</td>
<td valign="top" width="115">
<p align="center">规格</p>
</td>
<td valign="top" width="88">
<p align="center">数量</p>
</td>
<td valign="top" width="56">
<p align="center">密级</p>
</td>
<td valign="top" width="96">
<p align="center">提供单位</p>
</td>
</tr>
<tr>
<td width="45">
<p align="center">1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="136">
<p align="center">FLASH配置参数</p>
</td>
<td width="69">
<p align="center">真实</p>
</td>
<td width="115">
<p align="center">单位：字节</p>
<p align="center">大小：4.2MB</p>
</td>
<td width="88">
<p align="center">1组</p>
</td>
<td width="56">
<p align="center">非密</p>
</td>
<td width="96">
<p align="center">XX单位</p>
</td>
</tr>
<tr>
<td width="45">
<p align="center">2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="136">
<p align="center">卫星星地反馈数据</p>
</td>
<td width="69">
<p align="center">模拟</p>
</td>
<td width="115">
<p align="center">符合星地传输接口协议的数据</p>
</td>
<td width="88">
<p align="center">连续2小时</p>
</td>
<td width="56">
<p align="center">&nbsp;</p>
</td>
<td width="96">
<p align="center">XX单位</p>
</td>
</tr>
<tr>
<td width="45">
<p align="center">3&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="136">
<p align="center">&nbsp;</p>
</td>
<td width="69">
<p align="center">&nbsp;</p>
</td>
<td width="115">
<p align="center">&nbsp;</p>
</td>
<td width="88">
<p align="center">&nbsp;</p>
</td>
<td width="56">
<p align="center">&nbsp;</p>
</td>
<td width="96">
<p align="center">&nbsp;</p>
</td>
</tr>
<tr>
<td width="45">
<p align="center">4&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="136">
<p align="center">&nbsp;</p>
</td>
<td width="69">
<p align="center">&nbsp;</p>
</td>
<td width="115">
<p align="center">&nbsp;</p>
</td>
<td width="88">
<p align="center">&nbsp;</p>
</td>
<td width="56">
<p align="center">&nbsp;</p>
</td>
<td width="96">
<p align="center">&nbsp;</p>
</td>
</tr>
</tbody>
</table>
</div>
</div>
</div>
<p>&nbsp;</p>`

export const EnvDiffHTML = `<p>测评环境中的软硬件可以有效支持测试输入输出，能够保障测试顺利有效，但XX数据采用仿真数据，XX设备采用仿真软件模拟，与真实环境有差异，具体环境差异及影响分析见下表。</p>
<p style="text-align: center;">表5-10测评环境差异影响分析表</p>
<div align="center">
<table border="1" width="601" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td width="43">
<p align="center">序号</p>
</td>
<td width="124">
<p align="center">真实环境</p>
</td>
<td width="149">
<p align="center">测试环境</p>
</td>
<td width="285">
<p align="center">环境差异及对测评结果影响</p>
</td>
</tr>
<tr>
<td width="43">
<p align="center">1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="124">
<p align="left">XX设备</p>
</td>
<td width="149">
<p align="left">YY设备</p>
</td>
<td width="285">
<p align="left">YY设备为与XX设备配置、功能相同的真实设备，无差异。</p>
</td>
</tr>
<tr>
<td width="43">
<p align="center">2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="124">
<p align="left">XX设备</p>
</td>
<td width="149">
<p align="left">XX仿真设备（内含XX仿真软件）</p>
</td>
<td width="285">
<p>XX仿真设备可仿真XX软件全部交联接口，测试数据格式满足XX功能测试要求，但仿真测试数据为非真实飞行数据，无法针对XX性能指标进行测试，该项指标的测试结果需要采信XX试飞结果。</p>
</td>
</tr>
<tr>
<td width="43">
<p align="center">3&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="124">
<p>&nbsp;</p>
</td>
<td width="149">
<p>&nbsp;</p>
</td>
<td width="285">
<p>&nbsp;</p>
</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: center;">&nbsp;</p>`

export const TestLevelAndTypeHTML = `<p>根据《军用软件鉴定测试指南》、软件需求规格说明及其他等效文档，本次测评的测试级别为配置项测试。所选取的测试类型有文档审查、静态分析、功能测试、性能测试、接口测试、边界测试、<em>XX</em>等，具体详见下表。</p>
<p style="text-align: center;">表6-1测试级别和测试类型一览表</p>
<div align="center">
<table border="1" width="595" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td width="125">
<p><strong>按照软件重要程度及软件类型必须保留的测试类型</strong></p>
</td>
<td valign="top" width="31">
<p align="center"><strong>均需要</strong></p>
</td>
<td valign="top" width="31">
<p align="center"><strong>均需要</strong></p>
</td>
<td valign="top" width="28">
<p align="center"><strong>重要及以上需要</strong></p>
</td>
<td valign="top" width="31">
<p align="center"><strong>921</strong><strong>、海军项目需要</strong></p>
</td>
<td valign="top" width="31">
<p align="center"><strong>均需要</strong></p>
</td>
<td valign="top" width="31">
<p align="center"><strong>均需要</strong></p>
</td>
<td valign="top" width="31">
<p align="center"><strong>均需要</strong></p>
</td>
<td valign="top" width="31">
<p align="center"><strong>关键软件需要</strong></p>
</td>
<td valign="top" width="30">
<p align="center"><strong>非嵌入式软件需要</strong></p>
</td>
<td valign="top" width="31">
<p align="center"><strong>含数据处理功能需要</strong></p>
</td>
<td valign="top" width="33">
<p align="center"><strong>重要及以上需要</strong></p>
</td>
<td valign="top" width="35">
<p align="center"><strong>均需要</strong></p>
</td>
<td valign="top" width="34">
<p align="center"><strong>均需要</strong></p>
</td>
<td valign="top" width="33">
<p align="center"><strong>非嵌入式软件需要</strong></p>
</td>
<td valign="top" width="33">
<p align="center"><strong>&nbsp;</strong></p>
</td>
</tr>
<tr>
<td width="125">
<p align="center">软件名称</p>
</td>
<td width="31">
<p align="center">文档审查</p>
</td>
<td width="31">
<p align="center">静态分析</p>
</td>
<td width="28">
<p align="center">代码审查</p>
</td>
<td width="31">
<p align="center">逻辑测试</p>
</td>
<td width="31">
<p align="center">功能测试</p>
</td>
<td width="31">
<p align="center">性能测试</p>
</td>
<td width="31">
<p align="center">边界测试</p>
</td>
<td width="31">
<p align="center">恢复性测试</p>
</td>
<td width="30">
<p align="center">安装性测试</p>
</td>
<td width="31">
<p align="center">数据处理测试</p>
</td>
<td width="33">
<p align="center">余量测试</p>
</td>
<td width="35">
<p align="center">强度测试</p>
</td>
<td width="34">
<p align="center">接口测试</p>
</td>
<td width="33">
<p align="center">人机交互界面测试</p>
</td>
<td width="33">
<p align="center">兼容性测试</p>
</td>
</tr>
<tr>
<td width="125">
<p align="left">XX软件配置项测试</p>
</td>
<td width="31">
<p align="center">&radic;</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="28">
<p align="center">&nbsp;</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="30">
<p align="center">&nbsp;</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="33">
<p align="center">&nbsp;</p>
</td>
<td width="35">
<p align="center">&nbsp;</p>
</td>
<td width="34">
<p align="center">&nbsp;</p>
</td>
<td width="33">
<p align="center">&nbsp;</p>
</td>
<td width="33">
<p align="center">&nbsp;</p>
</td>
</tr>
<tr>
<td width="125">
<p>系统测试要求的测试类型</p>
</td>
<td width="31">
<p align="center">必须</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="28">
<p align="center">&nbsp;</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="31">
<p align="center">必须</p>
</td>
<td width="31">
<p align="center">必须</p>
</td>
<td width="31">
<p align="center">必须</p>
</td>
<td width="31">
<p align="center">必须</p>
</td>
<td width="30">
<p align="center">&nbsp;</p>
</td>
<td width="31">
<p align="center">&nbsp;</p>
</td>
<td width="33">
<p align="center">必须</p>
</td>
<td width="35">
<p align="center">必须</p>
</td>
<td width="34">
<p align="center">必须</p>
</td>
<td width="33">
<p align="center">&nbsp;</p>
</td>
<td width="33">
<p align="center">必须</p>
</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: left;">注：表格中的&ldquo;&radic;&rdquo;表示需要进行此项测试，&ldquo;－&rdquo;表示不进行此项测试。</p>
<p style="text-align: center;">表6-2未选取测试类型原因说明</p>
<div align="center">
<table border="1" width="597" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td width="45">
<p align="center">序号</p>
</td>
<td width="140">
<p align="center">软件测试</p>
</td>
<td width="154">
<p align="center">测试类型</p>
</td>
<td width="259">
<p align="center">未选取原因</p>
</td>
</tr>
<tr>
<td width="45">
<p align="center">1&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td rowspan="4" width="140">
<p align="left">XX软件配置项测试</p>
</td>
<td width="154">
<p>安装性测试</p>
</td>
<td width="259">
<p>软件为嵌入式软件，且无安装性需求，故不开展相关测试类型测试</p>
</td>
</tr>
<tr>
<td width="45">
<p align="center">2&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="154">
<p>人机交互界面测试</p>
</td>
<td width="259">
<p>软件为嵌入式软件，且无人机交互界面需求，故不开展相关测试类型测试</p>
</td>
</tr>
<tr>
<td width="45">
<p align="center">3&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="154">
<p>数据处理测试</p>
</td>
<td width="259">
<p>软件需求规模说明中无数据处理要求，且无隐含要求，故不开展相关测试类型测试。</p>
</td>
</tr>
<tr>
<td width="45">
<p align="center">4&nbsp;&nbsp;&nbsp; &nbsp;</p>
</td>
<td width="154">
<p>兼容性测试</p>
</td>
<td width="259">
<p>软件需求规模说明中无兼容性要求，且无隐含要求，故不开展相关测试类型测试。</p>
</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: center;">&nbsp;</p>`
