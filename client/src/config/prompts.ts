// Prompt types and target models configuration

export const PROMPT_TYPES = [
  { value: 'programmer', label: '程序员助手' },
  { value: 'ai_image_prompt', label: 'AI绘图' },
  { value: 'fashion_lookbook', label: '时尚分镜' },
  { value: 'photography_advisor', label: '摄影顾问' },
  { value: 'character_designer', label: '角色设计' },
  { value: 'brand_strategist', label: '品牌策略' },
  { value: 'creative_design', label: '创意设计' },
  { value: 'customer_service', label: '客服系统' },
  { value: 'content_creator', label: '内容创作' },
  { value: 'data_analyst', label: '数据分析' },
  { value: 'education', label: '教育培训' },
  { value: 'research', label: '研究分析' },
  { value: 'general', label: '通用助手' },
];

export const PROMPT_TYPES_EN = [
  { value: 'programmer', label: 'Programmer Assistant' },
  { value: 'ai_image_prompt', label: 'AI Image Prompt' },
  { value: 'fashion_lookbook', label: 'Fashion Lookbook' },
  { value: 'photography_advisor', label: 'Photography Advisor' },
  { value: 'character_designer', label: 'Character Designer' },
  { value: 'brand_strategist', label: 'Brand Strategist' },
  { value: 'creative_design', label: 'Creative Design' },
  { value: 'customer_service', label: 'Customer Service' },
  { value: 'content_creator', label: 'Content Creator' },
  { value: 'data_analyst', label: 'Data Analyst' },
  { value: 'education', label: 'Education & Training' },
  { value: 'research', label: 'Research & Analysis' },
  { value: 'general', label: 'General Assistant' },
];

// 选择类型后自动填充的提示文字（中文）
// 列出该类型助手的典型能力，用户可以删除不需要的
export const PROMPT_TYPE_TEMPLATES_CN: Record<string, string> = {
  ai_image_prompt: `我需要一个 AI 绘图提示词助手。

目标平台：[Midjourney / Stable Diffusion / DALL-E / Flux]
主要用途：[描述你的使用场景，如：产品图生成 / 概念设计 / 艺术创作]
风格偏好：[如：写实摄影 / 插画 / 3D渲染 / 油画]

核心需求：
- 根据简单描述生成专业的图像提示词
- 优化光影、构图、色调等美学元素
- 支持迭代修改和风格调整`,

  fashion_lookbook: `我需要一个时尚分镜助手，能分析图片并生成多角度分镜。

应用场景：[如：时尚大片 / Lookbook / 故事板 / 产品展示]
分镜数量：[如：6格 / 9格 / 自定义]
输出格式：JSON结构化数据

工作流程：
1. 分析图片：提取人物、服装、配饰、背景、光影等核心元素
2. 锁定风格：确定视觉基准（色调、氛围、摄影风格）
3. 生成分镜：输出JSON，每帧包含机位、姿势、构图、光影描述

核心需求：
- 精准分析原图元素，确保分镜一致性
- 每帧提供完整的AI绘图提示词
- 输出结构化JSON便于批量生成`,

  photography_advisor: `我需要一个摄影顾问助手。

摄影类型：[如：人像 / 风光 / 产品 / 街拍 / 美食]
使用场景：[如：商业拍摄 / 个人创作 / 社交媒体 / 学习提升]
设备情况：[如：手机 / 单反 / 微单 / 具体型号]

核心需求：
- 提供构图、光影、色彩的专业指导
- 根据场景推荐拍摄参数和技巧
- 后期调色和修图思路建议`,

  character_designer: `我需要一个角色设计助手。

角色用途：[如：游戏角色 / 动画人物 / 小说插图 / IP形象]
风格方向：[如：日系动漫 / 美式卡通 / 写实 / Q版]
角色类型：[如：主角 / 反派 / NPC / 吉祥物]

核心需求：
- 设计角色外观、服装、配饰细节
- 定义角色性格特征和背景故事
- 生成多角度、多表情的设计描述`,

  brand_strategist: `我需要一个品牌策略助手。

品牌阶段：[如：新品牌创建 / 品牌升级 / 品牌延伸]
行业领域：[如：消费品 / 科技 / 餐饮 / 服务]
目标市场：[描述你的目标用户群体]

核心需求：
- 定义品牌定位和核心价值主张
- 规划品牌视觉识别系统方向
- 制定品牌传播策略和调性`,

  programmer: `我需要一个编程助手。

技术领域：[如：Web开发 / 后端服务 / 数据处理 / 移动应用]
主要语言：[如：Python / JavaScript / Java / Go]
工作场景：[如：日常开发 / 代码审查 / 学习新技术 / 解决bug]

核心需求：
- 编写高质量代码并解释实现思路
- 发现代码问题并提供优化建议
- 回答技术问题和最佳实践`,

  customer_service: `我需要一个智能客服助手。

业务类型：[如：电商 / SaaS产品 / 金融服务 / 在线教育]
服务对象：[描述你的用户群体]
常见问题：[列举几个典型的用户咨询场景]

核心需求：
- 准确回答产品和服务相关问题
- 友好处理用户投诉和反馈
- 引导用户完成操作流程`,

  content_creator: `我需要一个内容创作助手。

内容形式：[如：公众号文章 / 短视频脚本 / 营销文案 / 产品描述]
目标受众：[描述你的读者/观众群体]
内容风格：[如：专业严谨 / 轻松幽默 / 情感共鸣]

核心需求：
- 根据主题快速生成高质量内容
- 保持一致的品牌调性和风格
- 优化标题和结构提升传播效果`,

  data_analyst: `我需要一个数据分析助手。

数据类型：[如：销售数据 / 用户行为 / 运营指标 / 市场数据]
分析目的：[如：业务洞察 / 决策支持 / 异常监控 / 趋势预测]
输出形式：[如：分析报告 / 可视化图表 / 数据看板]

核心需求：
- 从数据中发现有价值的洞察
- 用清晰的方式呈现分析结果
- 提供可执行的业务建议`,

  creative_design: `我需要一个创意设计助手。

设计类型：[如：品牌视觉 / UI界面 / 营销物料 / 产品包装]
项目背景：[描述你的项目和设计需求]
风格方向：[如：简约现代 / 复古怀旧 / 科技感 / 自然清新]

核心需求：
- 提供创意方向和设计建议
- 生成设计方案描述和视觉参考
- 协助完善和迭代设计细节`,

  education: `我需要一个教育助手。

使用场景：[如：自学编程 / 备考英语 / 辅导孩子 / 培训员工]
学习内容：[描述具体要学习的知识或技能]
当前水平：[入门 / 有基础 / 进阶提升]

核心需求：
- 用易懂的方式讲解知识点
- 提供练习和及时反馈
- 制定合理的学习计划`,

  research: `我需要一个研究分析助手。

研究方向：[如：行业分析 / 竞品调研 / 学术研究 / 政策解读]
研究主题：[描述你要研究的具体问题]
输出要求：[如：研究报告 / 摘要总结 / 对比分析]

核心需求：
- 系统收集和整理相关信息
- 进行深度分析并得出结论
- 结构化呈现研究成果`,

  general: `我需要一个通用助手。

主要用途：[描述你最常用的场景，如：写作辅助 / 信息整理 / 问题解答]
工作领域：[如：互联网 / 金融 / 教育 / 医疗]

核心需求：
- 快速准确地回答各类问题
- 协助完成文档和内容编写
- 提供建议和解决方案`,
};

// 选择类型后自动填充的提示文字（英文）
export const PROMPT_TYPE_TEMPLATES_EN: Record<string, string> = {
  ai_image_prompt: `I need an AI image prompt assistant.

Target platform: [Midjourney / Stable Diffusion / DALL-E / Flux]
Main use case: [describe your scenario, e.g.: product images / concept design / art creation]
Style preference: [e.g.: realistic photography / illustration / 3D render / oil painting]

Core requirements:
- Generate professional image prompts from simple descriptions
- Optimize lighting, composition, color and other aesthetic elements
- Support iterative refinement and style adjustments`,

  fashion_lookbook: `I need a fashion storyboard assistant that analyzes images and generates multi-angle frames.

Use case: [e.g.: fashion editorial / lookbook / storyboard / product showcase]
Frame count: [e.g.: 6 frames / 9 frames / custom]
Output format: Structured JSON data

Workflow:
1. Analyze image: Extract character, clothing, accessories, background, lighting elements
2. Lock style: Define visual baseline (color tone, mood, photography style)
3. Generate frames: Output JSON with camera angle, pose, composition, lighting for each frame

Core requirements:
- Precisely analyze original image elements to ensure frame consistency
- Provide complete AI image prompts for each frame
- Output structured JSON for batch generation`,

  photography_advisor: `I need a photography advisor assistant.

Photography type: [e.g.: portrait / landscape / product / street / food]
Use case: [e.g.: commercial shoots / personal projects / social media / skill improvement]
Equipment: [e.g.: smartphone / DSLR / mirrorless / specific model]

Core requirements:
- Provide professional guidance on composition, lighting, and color
- Recommend shooting parameters and techniques for different scenarios
- Suggest post-processing and color grading approaches`,

  character_designer: `I need a character design assistant.

Character purpose: [e.g.: game character / animation / novel illustration / IP mascot]
Style direction: [e.g.: anime / western cartoon / realistic / chibi]
Character type: [e.g.: protagonist / villain / NPC / mascot]

Core requirements:
- Design character appearance, clothing, and accessory details
- Define personality traits and backstory
- Generate multi-angle and multi-expression design descriptions`,

  brand_strategist: `I need a brand strategy assistant.

Brand stage: [e.g.: new brand creation / brand refresh / brand extension]
Industry: [e.g.: consumer goods / tech / F&B / services]
Target market: [describe your target audience]

Core requirements:
- Define brand positioning and core value proposition
- Plan brand visual identity system direction
- Develop brand communication strategy and tone`,

  programmer: `I need a programming assistant.

Tech domain: [e.g.: Web development / Backend services / Data processing / Mobile apps]
Main languages: [e.g.: Python / JavaScript / Java / Go]
Work scenarios: [e.g.: daily coding / code review / learning new tech / debugging]

Core requirements:
- Write quality code and explain implementation
- Find issues and provide optimization suggestions
- Answer technical questions and best practices`,

  customer_service: `I need a smart customer service assistant.

Business type: [e.g.: E-commerce / SaaS product / Financial services / Online education]
Target users: [describe your user base]
Common issues: [list a few typical customer inquiry scenarios]

Core requirements:
- Accurately answer product and service questions
- Handle complaints and feedback professionally
- Guide users through processes`,

  content_creator: `I need a content creation assistant.

Content format: [e.g.: blog posts / video scripts / marketing copy / product descriptions]
Target audience: [describe your readers/viewers]
Content style: [e.g.: professional / casual and fun / emotional]

Core requirements:
- Quickly generate quality content based on topics
- Maintain consistent brand voice and style
- Optimize headlines and structure for engagement`,

  data_analyst: `I need a data analysis assistant.

Data type: [e.g.: sales data / user behavior / operational metrics / market data]
Analysis purpose: [e.g.: business insights / decision support / anomaly detection / trend forecasting]
Output format: [e.g.: analysis report / visualizations / dashboards]

Core requirements:
- Discover valuable insights from data
- Present analysis results clearly
- Provide actionable business recommendations`,

  creative_design: `I need a creative design assistant.

Design type: [e.g.: brand identity / UI design / marketing materials / product packaging]
Project background: [describe your project and design needs]
Style direction: [e.g.: minimal modern / retro vintage / tech-forward / natural organic]

Core requirements:
- Provide creative direction and design suggestions
- Generate design briefs and visual references
- Help refine and iterate on design details`,

  education: `I need an education assistant.

Use case: [e.g.: self-learning programming / exam prep / tutoring kids / employee training]
Learning content: [describe the specific knowledge or skills]
Current level: [beginner / intermediate / advanced]

Core requirements:
- Explain concepts in easy-to-understand ways
- Provide practice and timely feedback
- Create reasonable learning plans`,

  research: `I need a research analysis assistant.

Research area: [e.g.: industry analysis / competitive research / academic study / policy review]
Research topic: [describe the specific question you're researching]
Output requirements: [e.g.: research report / summary / comparative analysis]

Core requirements:
- Systematically collect and organize information
- Conduct deep analysis and draw conclusions
- Present findings in a structured format`,

  general: `I need a general assistant.

Main use: [describe your most common scenarios, e.g.: writing help / info organization / Q&A]
Work domain: [e.g.: tech / finance / education / healthcare]

Core requirements:
- Answer various questions quickly and accurately
- Help with documents and content writing
- Provide suggestions and solutions`,
};

