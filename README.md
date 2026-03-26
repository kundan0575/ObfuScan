# ObfuScan

[English](#english) | [中文](#中文)

## 中文

一个面向 **Android APK Native SO 预筛选** 的小工具。  
核心目标不是“完整还原逻辑”，而是作为**逆向分析 / 安全审计前的前置探针**，帮助你在一堆 `arm64-v8a` 的 `.so` 里，**更快发现高价值目标**。

它适合用在下面这类场景：

- 在正式打开 IDA / Ghidra / Hopper 之前，先快速扫一遍 APK
- 从大量 Native 库中优先找出更值得投入时间的目标
- 提前识别疑似：
    - 加壳 / loader 型保护
    - 强混淆 / OLLVM 类特征
    - ZIP 容器伪装 SO
    - 可疑入口（`ELF入口` / `.init_array` / `JNI_OnLoad` / `Java_*`）

---

## 项目定位

**ObfuScan 不是一个“全自动还原保护逻辑”的工具。**  
它更像一个**审计前的前哨站**：

- 帮你快速扫 APK 中所有 64 位 SO
- 给出简洁的中文风险摘要
- 按 **高 / 中 / 低** 风险排序
- 对高风险样本进一步展示关键入口预览
- 让你更快决定：
    - 哪几个 SO 值得先看
    - 哪些入口值得先下断点 / 先反汇编 / 先做动态跟踪

一句话总结：

> **先筛选，再深挖。**  
> 把有限的逆向时间优先花在更可能有价值的目标上。

---

## 快速开始

### 方法一：Web 界面（推荐）

1. **启动 Web 服务器**
   ```bash
   cd ObfuScan
   python web_server.py
   ```

2. **访问 Web 界面**
   打开浏览器，访问 `http://127.0.0.1:8080`

3. **上传 APK 并分析**
   - 点击“选择APK文件”按钮，选择要分析的APK文件
   - 点击“开始分析”按钮
   - 等待分析完成后查看结果

### 方法二：命令行

1. **运行 ObfuScan**
   ```bash
   ObfuScan.exe <apk_path>
   ```

2. **查看输出**
   命令行会输出 JSON 格式的分析结果

---

## 当前支持的能力

### 1. APK 内 `arm64-v8a` SO 扫描
自动枚举 APK 中的：

- `lib/arm64-v8a/*.so`

### 2. ELF 基础分析
支持提取和统计：

- ELF 文件头校验
- Program Header / Section Header
- `.text / .rodata / .data / .init_array`
- `.dynsym / .dynstr`
- 导入符号 / 导出符号
- 可执行段熵
- 大块高熵数据
- 是否裁剪符号表（strip）

### 3. AArch64 指令统计（基于 Capstone）
对 `.text` 或可执行段进行线性反汇编，统计：

- 分支密度
- 间接跳转密度
- 算术 / 逻辑 / 比较类指令密度

用于辅助判断：

- 疑似 OLLVM
- 疑似强控制流混淆
- 疑似自定义保护逻辑

### 4. ZIP 容器伪装 SO 识别
有些 APK 里的 `.so` 条目，实际上并不是裸 ELF，而是 ZIP 容器或二次包装资源。

ObfuScan 支持：

- 识别 ZIP 伪装 SO
- 自动尝试提取内层 ELF
- 对内层 ELF 继续分析

### 5. 高风险样本入口预览
对高风险 SO，会进一步尝试预览：

- `ELF入口`
- `.init_array`
- `JNI_OnLoad`
- `Java_*`
- 名称中包含 `init / load / register` 的导出函数

输出形式尽量保持简洁，方便快速人工判断。

### 6. 中文摘要输出
默认输出为**中文简洁结果**，重点展示：

- SO 文件名
- 检测结果
- 风险等级
- 说明
- 可疑点
- 关键入口预览（高风险样本）
- 建议

适合在大量样本里先看重点，而不是一上来就被技术细节淹没。

---

## 适合什么场景

这个工具更适合下面这些任务：

- 逆向分析前，先筛出值得看的一批 SO
- 安全审计前，先找“可能藏逻辑 / 藏保护 / 藏入口”的目标
- 从几百个 Native 库中快速找出更高价值的样本
- 对 APK 的 Native 层做第一轮快速体检

## 不适合什么场景

ObfuScan **不适合**拿来做这些事情：

- 精确还原完整 CFG
- 精确恢复函数边界
- 自动还原 VMP 逻辑
- 自动还原壳 / VM / handler 细节
- 替代 IDA / Ghidra / 动态调试器

它更像是：

> **“真正开始逆向之前的筛选器”**  
> 而不是“逆向工作的终点”。

---

## 输出结果怎么看

通常可以按这个思路理解：

### 高风险
优先看。  
这类目标往往更可能存在：

- 加壳 / loader
- 强混淆
- 可疑初始化逻辑
- 异常入口
- 值得深入跟踪的保护层

### 中风险
有一定可疑度，但未必真有强保护。  
适合结合具体业务背景决定是否深入。

### 低风险
通常更像普通发布版本、基础库、轻度混淆样本。  
一般不作为第一优先级。

---

## 关于准确率的说明

### 高风险检测
目前来看，**高风险样本的筛选价值相对更高**。  
它的定位不是“百分百准确分类”，而是：

> **尽量把更值得逆向的人先排到前面。**

在这个意义上，高风险结果通常更有参考价值。

### VMP 检测
**VMP 检测目前只是启发式参考，不保证准确。**

原因很简单：

- 各种自研 VM 差异很大
- 一些强混淆、壳、linker 逻辑也会出现类似特征
- 静态线性反汇编本身就有局限
- 没有做完整的 dispatcher / handler / bytecode 数据流恢复

所以当前版本里：

- **“疑似 VMP” = 值得重点看**
- **不等于已经确认是 VMP**
- **“未见明显 VMP 特征” 也不等于绝对没有 VMP**

建议把它理解为：

> **一个帮助你优先级排序的辅助信号**  
> 而不是最终结论。

---

## 一个典型使用思路

实际工作里，我更推荐这样用：

1. 先用 ObfuScan 扫 APK（Web 界面或命令行）
2. 重点看高风险样本
3. 再看这些高风险样本的入口预览
4. 选出最值得深入的几个 SO
5. 再进入：
    - IDA / Ghidra
    - Frida / 自研 JNI 监控
    - 动态跟踪 / 断点调试
    - CFG / dispatcher / handler 深挖

这样通常会比一开始盲开几十上百个 SO 更省时间。

---

## 当前已知局限

- 主要面向 **Android 64 位 AArch64 SO**
- 不是完整反编译器
- OLLVM / 强混淆判断是启发式
- VMP 检测目前精度有限
- 对某些非常规壳 / 自研 VM / 深度伪装样本可能漏报或误报
- 当前更偏向“前置筛选”而不是“最终定性”

---

## 后续可能的方向

后面可能继续完善的方向包括：
- 接入AI
- 更稳的入口函数深挖
- 更细的 dispatcher / handler 识别
- 基本块切分
- 更强的 OLLVM / flatten 检测
- 更严格的 VMP 结构级识别
- 更详细的可选 verbose 输出
- 批量 APK 目录扫描

---

## 适合谁使用

这个工具更适合：

- 做 Android Native 逆向的人
- 做 APK 安全审计的人
- 需要批量初筛 SO 的研究人员
- 想先快速找高价值目标，再投入深度分析的人

---

## 最后说明

这个项目的核心思想很简单：

> **在真正开始逆向之前，先帮你找到更值得逆向的目标。**

如果它能帮你把“本来要花在 100 个普通 SO 上的时间”，  
提前集中到那几个真正值得看的目标上，那它就已经完成任务了。

---

## 致谢

感谢以下项目 / 工具：

- **GPT**
- **Capstone**
- **miniz**

---

## English

### ObfuScan

A lightweight tool for **Android APK Native SO pre-screening**.  
The core goal is not to "completely restore logic", but to serve as a **pre-probe before reverse analysis / security audit**, helping you **quickly find high-value targets** among a bunch of `arm64-v8a` `.so` files.

It is suitable for scenarios like:

- Quickly scanning an APK before opening IDA / Ghidra / Hopper
- Prioritizing Native libraries that are more worth investing time in
- Early identification of suspected:
    - Packing / loader-type protection
    - Strong obfuscation / OLLVM-like features
    - ZIP container disguised as SO
    - Suspicious entries (`ELF entry` / `.init_array` / `JNI_OnLoad` / `Java_*`)

---

### Project Positioning

**ObfuScan is not a "fully automatic protection logic restoration" tool.**  
It is more like an **outpost before audit**:

- Helps you quickly scan all 64-bit SOs in an APK
- Provides concise Chinese risk summaries
- Sorts by **high / medium / low** risk levels
- Further displays key entry previews for high-risk samples
- Helps you decide faster:
    - Which SOs are worth looking at first
    - Which entries are worth setting breakpoints / disassembling / dynamic tracking first

In a nutshell:

> **Screen first, then dig deeper.**  
> Prioritize your limited reverse engineering time on targets that are more likely to be valuable.

---

### Quick Start

#### Method 1: Web Interface (Recommended)

1. **Start the Web Server**
   ```bash
   cd ObfuScan
   python web_server.py
   ```

2. **Access the Web Interface**
   Open your browser and visit `http://127.0.0.1:8080`

3. **Upload APK and Analyze**
   - Click the "Select APK File" button to choose the APK file to analyze
   - Click the "Start Analysis" button
   - Wait for the analysis to complete and view the results

#### Method 2: Command Line

1. **Run ObfuScan**
   ```bash
   ObfuScan.exe <apk_path>
   ```

2. **View Output**
   The command line will output analysis results in JSON format

---

### Currently Supported Capabilities

#### 1. APK `arm64-v8a` SO Scanning
Automatically enumerates in APK:

- `lib/arm64-v8a/*.so`

#### 2. ELF Basic Analysis
Supports extraction and statistics of:

- ELF file header verification
- Program Header / Section Header
- `.text / .rodata / .data / .init_array`
- `.dynsym / .dynstr`
- Import symbols / Export symbols
- Executable segment entropy
- Large high-entropy data
- Whether the symbol table is stripped

#### 3. AArch64 Instruction Statistics (based on Capstone)
Performs linear disassembly on `.text` or executable segments,统计：

- Branch density
- Indirect jump density
- Arithmetic / logical / comparison instruction density

Used to assist in judging:

- Suspected OLLVM
- Suspected strong control flow obfuscation
- Suspected custom protection logic

#### 4. ZIP Container Disguised as SO Identification
Some `.so` entries in APKs are not actually bare ELF files, but ZIP containers or secondary packaged resources.

ObfuScan supports:

- Identifying ZIP disguised SO
- Automatically attempting to extract inner ELF
- Continuing analysis on inner ELF

#### 5. High-Risk Sample Entry Preview
For high-risk SOs, it will further attempt to preview:

- `ELF entry`
- `.init_array`
- `JNI_OnLoad`
- `Java_*`
- Exported functions containing `init / load / register` in their names

The output format is kept as concise as possible for quick manual judgment.

#### 6. Chinese Summary Output
The default output is **concise Chinese results**, focusing on displaying:

- SO file name
- Detection result
- Risk level
- Description
- Suspicious points
- Key entry previews (for high-risk samples)
- Recommendations

Suitable for focusing on key points in a large number of samples, rather than being overwhelmed by technical details at the beginning.

---

### What Scenarios It's Suitable For

This tool is more suitable for tasks like:

- Screening out a batch of SOs worth looking at before reverse analysis
- Finding targets that "may hide logic / protection / entries" before security audit
- Quickly identifying higher-value samples from hundreds of Native libraries
- Conducting a first-round quick check on the Native layer of APKs

### What Scenarios It's Not Suitable For

ObfuScan **is not suitable** for these things:

- Precisely restoring complete CFG
- Precisely recovering function boundaries
- Automatically restoring VMP logic
- Automatically restoring shell / VM / handler details
- Replacing IDA / Ghidra / dynamic debuggers

It is more like:

> **"A filter before真正开始逆向"**  
> Rather than "the end of reverse engineering work."

---

### How to Interpret Output Results

You can generally understand it with this思路：

#### High Risk
Priority viewing.  
Such targets are more likely to have:

- Packing / loader
- Strong obfuscation
- Suspicious initialization logic
- Abnormal entries
- Protection layers worth in-depth tracking

#### Medium Risk
Has a certain degree of suspicion, but may not really have strong protection.  
Suitable for deciding whether to深入 based on specific business context.

#### Low Risk
Usually more like ordinary release versions, basic libraries, or lightly obfuscated samples.  
Generally not prioritized.

---

### About Accuracy

#### High-Risk Detection
Currently, **the screening value of high-risk samples is relatively higher**.  
Its positioning is not "100% accurate classification", but:

> **Try to put people who are more worth reversing at the front.**

In this sense, high-risk results are usually more valuable for reference.

#### VMP Detection
**VMP detection is currently only a heuristic reference and not guaranteed to be accurate.**

The reasons are simple:

- Various self-developed VMs differ greatly
- Some strong obfuscation, shells, and linker logic also exhibit similar characteristics
- Static linear disassembly itself has limitations
- No complete dispatcher / handler / bytecode data flow recovery

So in the current version:

- **"Suspected VMP" = worth focusing on**
- **Does not mean confirmed VMP**
- **"No obvious VMP characteristics" does not mean absolutely no VMP**

It is recommended to understand it as:

> **An auxiliary signal to help you prioritize**  
> Rather than a final conclusion.

---

### A Typical Usage Approach

In actual work, I recommend using it like this:

1. First scan the APK with ObfuScan (Web interface or command line)
2. Focus on high-risk samples
3. Then look at the entry previews of these high-risk samples
4. Select the few SOs most worth in-depth analysis
5. Then enter:
    - IDA / Ghidra
    - Frida / self-developed JNI monitoring
    - Dynamic tracking / breakpoint debugging
    - CFG / dispatcher / handler in-depth analysis

This usually saves time compared to blindly opening dozens or hundreds of SOs at the beginning.

---

### Current Known Limitations

- Mainly oriented to **Android 64-bit AArch64 SO**
- Not a complete decompiler
- OLLVM / strong obfuscation judgment is heuristic
- VMP detection currently has limited accuracy
- May miss or false alarm on some unconventional shells / self-developed VMs / deeply disguised samples
- Currently more biased towards "pre-screening" rather than "final定性"

---

### Possible Future Directions

Possible future improvements include:
- AI integration
- More stable entry function in-depth analysis
- More detailed dispatcher / handler identification
- Basic block splitting
- Stronger OLLVM / flatten detection
- More strict VMP structural-level identification
- More detailed optional verbose output
- Batch APK directory scanning

---

### Who It's For

This tool is more suitable for:

- People doing Android Native reverse engineering
- People doing APK security audits
- Researchers who need to batch pre-screen SOs
- People who want to quickly find high-value targets before investing in in-depth analysis

---

### Final Note

The core idea of this project is simple:

> **Before you really start reversing, help you find targets that are more worth reversing.**

If it can help you focus the time you would have spent on 100 ordinary SOs on the few truly worth-looking targets in advance, then it has completed its task.

---

### Acknowledgments

Thanks to the following projects / tools:

- **GPT**
- **Capstone**
- **miniz**