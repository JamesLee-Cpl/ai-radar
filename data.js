/* ============================================================
 *  AI硬件瓶颈雷达 · 数据文件
 *  季度更新方法：只动本文件，index.html 不必碰。
 *  字段说明：
 *    id          : 唯一英文短名（突破标记按此持久化，改动会丢标记）
 *    name        : 显示名
 *    cat         : 分类标签
 *    start, end  : 商用窗口（年份，可带小数）
 *    mult        : 突破倍率显示文字
 *    multType    : 倍率维度（带宽/能效/集成度…）
 *    status      : 'in-progress' | 'watching' | 'long-term'
 *                  ('breakthrough' 状态由用户标记动态生成，不写在此处)
 *    relevance   : 'direct' | 'indirect' | 'low' （与你持仓的关联度）
 *    players     : 代表玩家
 *    stocks      : 关联标的
 *      ticker    : 雅虎格式（日股 XXXX.T、韩股 XXXXXX.KS、美股 ticker、未上市 '-'）
 *      name      : 公司名
 *      market    : '日股' | '美股' | '韩股' | '未上市' | 'OTC'
 *      rel       : 与该瓶颈的关系说明
 *    note        : 卡片注解（投资视角）
 *  ============================================================ */

window.RADAR_META = {
  basisDate: '2026-06',
  portfolioView: '日股 AI/半导体',
};

window.BOTTLENECKS = [
  {
    id:'hbm', name:'HBM4 / HBM5', cat:'内存带宽（HBM）',
    start:2026, end:2028, mult:'2–3×', multType:'带宽',
    status:'in-progress', relevance:'indirect',
    players:['SK Hynix','Samsung','Micron'],
    stocks:[
      {ticker:'4063.T', name:'信越化学工業', market:'日股', rel:'HBM用シリコン・関連材料'},
      {ticker:'3436.T', name:'SUMCO',       market:'日股', rel:'300mmシリコンウェハ'},
      {ticker:'6857.T', name:'アドバンテスト', market:'日股', rel:'HBMテスター（独占）'},
      {ticker:'000660.KS', name:'SK Hynix', market:'韩股', rel:'HBM龙头'},
      {ticker:'MU', name:'Micron', market:'美股', rel:'HBM3E/HBM4 跟进'},
    ],
    note:'HBM3E 已商用，HBM4 2026 出货爆发，HBM5 路线图在 2027–2028。日股侧最纯正受益是测试机（6857）与材料（4063/3436）。'
  },
  {
    id:'cpo', name:'CPO 共封装光学', cat:'互联/带宽',
    start:2026, end:2030, mult:'10×带宽', multType:'I/O带宽',
    status:'in-progress', relevance:'direct',
    players:['NVIDIA','Broadcom','TSMC','新光電気工業','フジクラ'],
    stocks:[
      {ticker:'5803.T', name:'フジクラ',           market:'日股', rel:'CPO 核心光纤/连接器（核心持仓）'},
      {ticker:'4062.T', name:'イビデン',             market:'日股', rel:'AI/CPO 用 IC 基板（新光退市后日股主力）'},
      {ticker:'AVGO',   name:'Broadcom',         market:'美股', rel:'交换机 + CPO 路线图'},
      {ticker:'NVDA',   name:'NVIDIA',           market:'美股', rel:'Quantum-X / Spectrum-X CPO'},
      {ticker:'COHR',   name:'Coherent',         market:'美股', rel:'光收发器/光源'},
    ],
    note:'你的「フジクラ核心」标签——CPO 是 2026–2027 最有可能爆发的瓶颈突破，看 NVIDIA GTC 与 OCP 发布节奏。'
  },
  {
    id:'pkg3d', name:'3D 封装（CoWoS / SoIC）', cat:'封装',
    start:2026, end:2029, mult:'2–4×', multType:'集成度',
    status:'in-progress', relevance:'indirect',
    players:['TSMC','Intel','Samsung'],
    stocks:[
      {ticker:'7735.T', name:'SCREEN HD',          market:'日股', rel:'前/后段洗净・先进封装设备'},
      {ticker:'6146.T', name:'ディスコ',            market:'日股', rel:'切割/研磨设备（封装关键）'},
      {ticker:'6857.T', name:'アドバンテスト',        market:'日股', rel:'先进封装后测试'},
      {ticker:'TSM',    name:'TSMC',              market:'美股', rel:'CoWoS / SoIC 产能瓶颈方'},
      {ticker:'7741.T', name:'HOYA',              market:'日股', rel:'EUV 掩膜底板'},
    ],
    note:'CoWoS 产能 2025→2026 翻倍，2027 继续。日股侧设备链普涨，注意 TSMC 资本支出指引拐点。'
  },
  {
    id:'sip', name:'硅光子集成（Silicon Photonics）', cat:'光集成',
    start:2027, end:2032, mult:'5–10×', multType:'能效',
    status:'watching', relevance:'direct',
    players:['Intel','Coherent','Lightmatter','京セラ'],
    stocks:[
      {ticker:'6971.T', name:'京セラ',             market:'日股', rel:'硅光子封装基板（直接持仓候选）'},
      {ticker:'COHR',   name:'Coherent',          market:'美股', rel:'光器件 + InP/SiPh'},
      {ticker:'INTC',   name:'Intel',             market:'美股', rel:'硅光收发器商用最早'},
      {ticker:'5803.T', name:'フジクラ',           market:'日股', rel:'SiPh 与 CPO 互补'},
    ],
    note:'CPO 之后的下一棒；2027 起会有"硅光算力"概念股二次估值。京セラ估值低、是 2027–2030 的"埋伏型"标的。'
  },
  {
    id:'inp', name:'InP 化合物半导体', cat:'材料',
    start:2027, end:2035, mult:'关键', multType:'材料',
    status:'watching', relevance:'direct',
    players:['Coherent','II-VI','JX金属'],
    stocks:[
      {ticker:'5016.T', name:'JX Advanced Metals', market:'日股', rel:'InP 基板全球龙头（直接持仓候选）'},
      {ticker:'COHR',   name:'Coherent',           market:'美股', rel:'InP 器件主要消费方'},
      {ticker:'5713.T', name:'住友金属鉱山',         market:'日股', rel:'化合物半导体材料'},
    ],
    note:'JX Advanced Metals 2024 IPO 后即被高盛/野村重点覆盖。InP 是数据中心 100G→800G→1.6T 光模块的核心材料，与 SiPh/CPO 同向。'
  },
  {
    id:'dc800', name:'800V DC 数据中心供电', cat:'电源/能效',
    start:2027, end:2030, mult:'30%+', multType:'能效',
    status:'in-progress', relevance:'direct',
    players:['NVIDIA','富士电机','Schneider','Ferrotec'],
    stocks:[
      {ticker:'6504.T', name:'富士電機',           market:'日股', rel:'IGBT/SiC・800V DC（已关注）'},
      {ticker:'6890.T', name:'Ferrotec HD',       market:'日股', rel:'电源/热管理（已关注）'},
      {ticker:'6594.T', name:'ニデック',           market:'日股', rel:'数据中心电机/冷却'},
      {ticker:'6503.T', name:'三菱電機',           market:'日股', rel:'SiC 功率器件'},
    ],
    note:'NVIDIA 已公开承诺 2027 转向 800V DC，整链条会有时序明确的"政策性"催化。富士电机+Ferrotec 是日股最纯的两个。'
  },
  {
    id:'cool', name:'液冷 / 浸没式冷却', cat:'散热',
    start:2025, end:2028, mult:'50%+', multType:'散热',
    status:'in-progress', relevance:'indirect',
    players:['Vertiv','Schneider','日本電産','3M'],
    stocks:[
      {ticker:'VRT',    name:'Vertiv',            market:'美股', rel:'液冷集成纯标的'},
      {ticker:'6594.T', name:'ニデック',           market:'日股', rel:'液冷泵/CDU'},
      {ticker:'6367.T', name:'ダイキン工業',         market:'日股', rel:'数据中心空调全球龙头（替代退市的富士通ゼネラル 6755）'},
      {ticker:'6845.T', name:'アズビル',            market:'日股', rel:'数据中心 BMS'},
    ],
    note:'液冷 2025 已大规模出货 Blackwell GB200，2026 进入 Rubin。判断"已突破" vs "进行中"——目前归类为进行中，渗透率仍只 30%。'
  },
  {
    id:'neuro', name:'神经形态芯片（Neuromorphic）', cat:'新架构',
    start:2030, end:2040, mult:'100×+', multType:'能效',
    status:'watching', relevance:'low',
    players:['Intel Loihi','IBM TrueNorth','BrainChip'],
    stocks:[
      {ticker:'INTC', name:'Intel',     market:'美股', rel:'Loihi 系列'},
      {ticker:'IBM',  name:'IBM',       market:'美股', rel:'TrueNorth / NorthPole'},
      {ticker:'BRCHF',name:'BrainChip', market:'OTC', rel:'纯标的（小市值高波动）'},
    ],
    note:'与你 2027 末 50M 目标的窗口不重叠，仅作长期观察。'
  },
  {
    id:'photonic', name:'光子计算（Photonic Computing）', cat:'新架构',
    start:2028, end:2035, mult:'10–100×', multType:'能效',
    status:'watching', relevance:'low',
    players:['Lightmatter','Lightelligence'],
    stocks:[
      {ticker:'-', name:'Lightmatter',  market:'未上市', rel:'2025 已估值 44 亿美元 · IPO 待观察'},
      {ticker:'-', name:'Lightelligence',market:'未上市', rel:'中美双总部'},
    ],
    note:'监控 IPO 节奏；当出现 IPO 时点，相关概念日股（フジクラ・京セラ・5803）会有联动反应。'
  },
  {
    id:'quantum', name:'量子计算', cat:'新架构',
    start:2035, end:2045, mult:'不解决AI', multType:'-',
    status:'long-term', relevance:'low',
    players:['IBM','Google','IonQ','PsiQuantum','富士通'],
    stocks:[
      {ticker:'IONQ', name:'IonQ',    market:'美股', rel:'纯量子标的'},
      {ticker:'IBM',  name:'IBM',     market:'美股', rel:'路线图最透明'},
      {ticker:'6702.T',name:'富士通',  market:'日股', rel:'理研 + 富士通量子机'},
    ],
    note:'对 AI 推理几乎无贡献——仅作"科学加速器"观察，不进入投资主线。'
  },
];
