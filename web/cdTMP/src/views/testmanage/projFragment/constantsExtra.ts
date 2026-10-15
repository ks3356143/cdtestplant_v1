export const TestStrategyHTML = `<p>依据《军用软件测试指南》以及相关国军标的要求，测试组分析了系统研制总要求、系统研制任务书、软件需求规格说明等文档，结合XXXX软件特点和研制方提供的测试环境，制定以下第三方测试策略：</p>
<p>a）文档审查内容为审查文档的测试齐套性、准确性、一致性和完整性，对于文档差距较大的软件，由测评机构提出申请，测评机构组织开展会议审查。</p>
<p>b）XXXX软件为XXXX（例：关键）软件，需对全部程序开展静态分析和代码审查。</p>
<p>c）本测试先实施配置项测试，待配置项测试发现问题闭环后再实施系统级测试；</p>
<p>d）对于配置项测试，先开展文档审查、代码审查、静态分析等静态测试，待静态测试发现问题闭环后再开展动态测试；</p>
<p>e）本次测评对于性能指标（除时间强度指标外）的验证，需采集10次数据进行验证；</p>
<p>f）测试过程中存在有争议的问题，应组织研制单位、软件测评机构、软件总体单位、软件测评总体单位（如有）等相关方确认进行确认。</p>
<p>g）软件需求中未明确余量指标要求，依据《军用软件测评实验室测评过程和技能能力要求》按照20%的余量指标要求开展余量测试；</p>
<p>h）无法采用动态测试手段验证的内容采用代码审查的方式检查逻辑实现的正确性；</p>
<p>i）若存在需要观测中间运行状态等采用动态测试手段无法直接验证的功能时，借助插桩测试手段验证。</p>
<p>针对XX功能中的XX等功能/算法，首先采用代码审查的方式，人工审查软件代码实现满足软件需求规格说明、软件设计说明等文档的要求，然后开展动态测试。在动态测试过程中，受XXX限制/影响，采取XXXX方式，模拟典型的/边界上的场景，设计相应测试用例的XXX的测试输入数据，并查看软件能够进行XX功能/算法。</p>
<p>经分析，本次第三方测试需要开展的测试类型所对应的测试内容及测试方法见下表所示。</p>
<p style="text-align: center;">表6-3测试类型及测试方法</p>
<div align="center">&nbsp;</div>
<div align="center">
<table border="1" cellspacing="0" cellpadding="0">
<thead>
<tr>
<td width="100">
<p align="center">测试类型</p>
<p align="center">名称</p>
</td>
<td width="64">
<p align="center">测试类型标识</p>
</td>
<td width="416">
<p align="center">测试内容及方法描述</p>
</td>
</tr>
</thead>
<tbody>
<tr>
<td width="100">
<p align="center">文档审查</p>
</td>
<td width="64">
<p align="center">DC</p>
</td>
<td valign="top" width="416">
<p align="left">通过人工审查的方式，依据《军用软件开发文档通用要求》，对研制方提交的软件需求规格说明、设计文档进行审查。文档审查依据文档检查单。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">静态分析</p>
</td>
<td width="64">
<p align="center">SA</p>
</td>
<td valign="top" width="416">
<p align="left">利用静态分析工具辅助进行控制流分析、数据流分析、接口特性分析和表达式分析，验证软件质量度量和编码规则是否满足标准要求</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">代码审查</p>
</td>
<td width="64">
<p align="center">CR</p>
</td>
<td valign="top" width="416">
<p align="left">按照经过评审的代码审查单，使用测试工具Klocwork和人工审查相结合的方式，对软件进行代码和设计的一致性、代码编程规范性检查。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">逻辑测试</p>
</td>
<td width="64">
<p align="center">LT</p>
</td>
<td width="416">
<p align="left">测试程序代码逻辑结构设计的合理性、实现的正确性，并对代码的分支覆盖率，语句覆盖率，判定/条件覆盖率、状态机覆盖率的进行统计、分析，评估是否满足覆盖率要求，对无法覆盖的内容逐一进行分析和人工确认。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">功能测试</p>
</td>
<td width="64">
<p align="center">SU</p>
</td>
<td valign="top" width="416">
<p align="left">功能测试根据被测软件的功能特点，</p>
<p align="left">用正常值的等价类输入数据值测试；</p>
<p align="left">b）用非正常值的等价类输入数据值测试；</p>
<p align="left">c）进行每个功能的合法边界值和非法边界值输入的测试；</p>
<p align="left">d）用一系列真实的数据类型和数据值运行，测试超负荷、饱和及其他&ldquo;最坏情况&rdquo;的结果；</p>
<p align="left">e）对控制流程的正确性、合理性等进行验证；</p>
<p align="left">f）对用户接口正常和异常数据输入的测试。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">接口测试</p>
</td>
<td width="64">
<p align="center">IO</p>
</td>
<td valign="top" width="416">
<p align="left">对配置项接口测试主要测试配置项软件的对外接口，对子系统接口进行测试主要测试子系统的对外接口；</p>
<p align="left">1、测试输出的数据格式是否满足通信协议的要求；</p>
<p align="left">2、对传输发生异常的数据，软件是否有相应的容错机制。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">性能测试</p>
</td>
<td width="64">
<p align="center">AC</p>
</td>
<td valign="top" width="416">
<p align="left">检查被测软件是否满足需求规格说明中规定的性能指标。性能测试需要进行多次读取测量值，每次测量值均满足测试要求，则测试通过。</p>
<p align="left">抗干扰、移动性等性能使用信号源、信道仪等设备进行辅助测试；</p>
<p align="left">传输性能、自组网性能使用windows自带ping工具、iperf工具等软件工具进行辅助测试；</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">强度测试</p>
</td>
<td width="64">
<p align="center">ST</p>
</td>
<td valign="top" width="416">
<p align="left">强制软件运行在不正常到发生故障的情况下（设计的极限状态到超出极限），检验软件可以运行到何种程度的测试；</p>
<p align="left">强度测试通过长时间运行系统、加大通信力度等方式进行验证系统的抗压能力。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">安全性测试</p>
</td>
<td width="64">
<p align="center">SE</p>
</td>
<td valign="top" width="416">
<p align="left">进行对异常条件下软件的处理和保护能力的测试（以表明不会因为可能的单个或多个输入错误而导致的不安全状态）；</p>
<p align="left">安全性针对用户鉴权、用户登录安全、参数合法性检查、异常断电安全等情况进行测试；</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">人机交互界面测试</p>
</td>
<td width="64">
<p align="center">GUI</p>
</td>
<td valign="top" width="416">
<p align="left">依据软件人机界面规范，验证软件人机交互界面的完整性，一致性，准确性，友好性，合理性，指导性；</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">余量测试</p>
</td>
<td width="64">
<p align="center">AT</p>
</td>
<td valign="top" width="416">
<p align="left">余量测试主要是验证程序存储空间、程序运行空间、数据存储空间以及软件控制周期的余量是否达到需求规格说明中的要求，若无明确要求时，一般要求留有不少于20%的余量。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">边界测试</p>
</td>
<td width="64">
<p align="center">BT</p>
</td>
<td valign="top" width="416">
<p align="left">针对各属性值的边界值，采用边界值左侧临界点、右侧临界点、边界值以及正常值等采样点数值进行验证。测试包括对正常范围内的边界进行测试，还包括对异常边界进行测试。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">恢复性测试</p>
</td>
<td width="64">
<p align="center">RE</p>
</td>
<td valign="top" width="416">
<p align="left">对软件在故障或复位后是否能够恢复到正确的状态进行测试。</p>
<p align="left">恢复性包括系统配置恢复、单通恢复、告警恢复等异常状态的恢复情况进行验证；</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">数据处理测试</p>
</td>
<td width="64">
<p align="center">DP</p>
</td>
<td valign="top" width="416">
<p align="left">a）应对数据文件存取、数据库操作、数据采集、数据融合、数据转换、数据解析等专门数据处理功能进行测试；</p>
<p align="left">b）应对剔除坏数据、数据滤波、数据容错等数据特殊处理功能进行测试；</p>
<p align="left">c）应针对数据读取/写入过程中的容错、保护、超时等进行测试；</p>
<p align="left">d）应对大数据处理算法、模型的实现正确性进行测试。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">兼容性测试</p>
</td>
<td width="64">
<p align="center">JR</p>
</td>
<td valign="top" width="416">
<p align="left">测试软件不同版本之间、不同软件产品之间、不同软硬件环境之间兼容程度</p>
<p align="left">主要测试内容如下：</p>
<p align="left">a) 当新版本软件替代旧版本软件时，对软件进行向下兼容性测试；</p>
<p align="left">b) 当多个软件版本可以同时使用时，对软件进行相互兼容性测试；</p>
<p align="left">c) 当两个软件产品可在同一硬件环境中替换使用时，对软件进行交错兼容性测试；</p>
<p align="left">d) 当软件产品可能在不同的硬件设备中使用时，对软件进行适配兼容性测试；</p>
<p align="left">e) 当软件产品可能在不同的软件环境中使用时，对软件进行环境兼容性测试；</p>
<p align="left">f) 针对替代国外软件的国产化软件，对软件进行交错兼容性测试。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">安装性测试</p>
</td>
<td width="64">
<p align="center">AZ</p>
</td>
<td valign="top" width="416">
<p align="left">测试软件安装过程是否满足安装需求、是否符合安装规程。</p>
<p align="left">主要测试内容如下：</p>
<p align="left">a) 对软件安装到应用系统中的操作过程是否正确进行测试</p>
<p align="left">b) 测试安装过程与产品规格说明或用户手册中所说明的安装规程是否文实一致；</p>
<p align="left">c) 对软件卸载功能进行测试，并测试卸载后系统中的软件痕迹是否彻底清除干净；</p>
<p align="left">d) 对适用于多种操作系统或多种系统配置的软件，应对软件在各种环境下的安装性进行测试；</p>
<p align="left">e) 系统级测试中对应用软件的部署与撤收进行测试，包括在线升级、数据迁移、系统配置等相关。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">容量测试</p>
</td>
<td width="64">
<p align="center">RL</p>
</td>
<td valign="top" width="416">
<p align="left">测试软件在正常情况下所具备的最高能力。</p>
<p align="left">主要测试内容如下：</p>
<p align="left">a) 针对具有时间约束要求的功能，测试出正常工作条件下实际执行时间的最值范围；</p>
<p align="left">b) 针对具有空间约束要求的功能，测试出正常工作条件下实际占用空间的最值范围；</p>
<p align="left">c) 针对通讯接口，测试出正常工作条件下实际传输时间、传输数据量的最值范围；</p>
<p align="left">d) 针对软件的处理能力，如处理目标数等，测试出正常工作条件下处理能力的最值范围。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">互操作性测试</p>
</td>
<td width="64">
<p align="center">HZ</p>
</td>
<td valign="top" width="416">
<p align="left">测试本软件与其他对同一功能或同一数据操作处理的协调性和一致。</p>
<p align="left">主要测试内容如下：</p>
<p align="left">a) 对同一功能通过配置可在不同软件中实现的相关软件，测试各种配置下功能的正确性；</p>
<p align="left">b) 对因软件降级而将部分功能移交给其他软件执行的相关软件，测试功能移交的正确性；</p>
<p align="left">c) 对可异步并发操作同一共享数据源的相关软件，测试对数据源操作的相容性和一致性；</p>
<p align="left">d) 当同一功能（如指令条件判别、控制指令下达等）被不同软件（装备）同时进行操作时，测试操作处理的协调性和一致性。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">可靠性测试</p>
</td>
<td width="64">
<p align="center">KK</p>
</td>
<td valign="top" width="416">
<p align="left">从用户视角出发进行情景想定分析，建立软件的使用剖面（任务剖面/业务剖面/运行剖面/操作剖面等），在保证输入覆盖要求的情况下对软件进行定量度量，如，使用剖面的概率分布、使用特征的覆盖率等；监测软件出现的故障， 记录并统计软件的故障数据，依据故障数据对软件可靠性指标进行量化评估。</p>
</td>
</tr>
<tr>
<td width="100">
<p align="center">数据审查</p>
</td>
<td width="64">
<p align="center">DT</p>
</td>
<td valign="top" width="416">
<p align="left">a) 针对装订参数、诸元参数、安装参数等软件依赖数据的完整性、有效性、格式规范性等进行审查；</p>
<p align="left">b) 针对影响软件初始运行配置的数据，应对软件最大、最小、典型、默认配置下的数据的有效性进行审查；</p>
<p align="left">c) 针对用于控制的数据，应根据控制要求对数据的精度、门限/阈值数据的合理性、数据用于控制过程的准确性等进行审查；</p>
<p align="left">d) 针对数据的不可更改性等安全保护措施进行审查。</p>
</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: center;">&nbsp;</p>`
