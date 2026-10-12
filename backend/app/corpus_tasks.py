MAPPINGS = [
    {
        "id": "map-mfg-amount", "kind": "mapping", "code": "对照-制-01", "name": "示例制造企业合同金额",
        "plate": "采购、合同与资产管理", "shape": "mapping", "status": "已发布", "maturity": "可指导",
        "summary": "台账「合同金额」是不含税口径，标准项按含税。直接比较会把已超限额的项目看成未超。",
        "owner_org": "示例制造企业", "maintainer": "党风廉政办", "applicable": "示例制造企业演示台账",
        "period": "2026年样本", "version": "演示2026-1", "source_doc": "示例制造企业采购台账说明", "source_locator": "字段E",
        "body": {
            "unit": "示例制造企业", "system": "演示采购台账", "source_field": "合同金额",
            "source_caliber": "不含税，人民币元", "standard_code": "D.04.07.006",
            "standard_expect": "合同金额（含税）", "conversion": "含税金额 = 不含税金额 ×（1+税率）。样本税率13%。",
            "same_object": "按合同编号可以认定是同一合同", "path": "台账工作表「合同」E列，用合同编号与立项编号关联",
            "checked_by": "演示核对", "checked_on": "2026-04-20", "verified": True,
        },
    },
    {
        "id": "map-mfg-dept", "kind": "mapping", "code": "对照-制-02", "name": "示例制造企业需求部门",
        "plate": "采购、合同与资产管理", "shape": "mapping", "status": "已发布", "maturity": "可参考",
        "summary": "台账用简称「安防组」，组织名录中的全称是生产保障部。合并计算时必须先还原部门。",
        "owner_org": "示例制造企业", "maintainer": "党风廉政办", "applicable": "示例制造企业",
        "period": "2026年样本", "version": "演示2026-1", "source_doc": "示例制造企业采购台账说明", "source_locator": "字段C",
        "body": {
            "unit": "示例制造企业", "system": "演示采购台账", "source_field": "需求部门",
            "source_caliber": "内部简称", "standard_code": "D.04.01.004",
            "standard_expect": "需求部门全称", "conversion": "安防组 → 生产保障部。不得把简称当成另一个部门。",
            "same_object": "是同一部门", "path": "台账C列，对照组织简称表",
            "checked_by": "演示核对", "checked_on": "2026-04-20", "verified": True,
        },
    },
    {
        "id": "map-fin-date", "kind": "mapping", "code": "对照-金-01", "name": "示例金融子公司招待日期",
        "plate": "财务资金与费用管理", "shape": "mapping", "status": "已发布", "maturity": "可指导",
        "summary": "报销单日期是入账日，判断节假日必须用消费日期，两列不能混用。",
        "owner_org": "示例金融子公司", "maintainer": "党风廉政办", "applicable": "示例金融子公司",
        "period": "2026年样本", "version": "演示2026-1", "source_doc": "示例金融子公司费用样本", "source_locator": "消费日期",
        "body": {
            "unit": "示例金融子公司", "system": "演示费用台账", "source_field": "消费日期",
            "source_caliber": "发票所列消费日，不是入账日", "standard_code": "D.06.01.002",
            "standard_expect": "招待日期", "conversion": "无需换算，但不得用入账日期代替。",
            "same_object": "同一报销单", "path": "费用台账「招待」B列",
            "checked_by": "演示核对", "checked_on": "2026-06-28", "verified": True,
        },
    },
    {
        "id": "map-fin-head", "kind": "mapping", "code": "对照-金-02", "name": "示例金融子公司发票抬头",
        "plate": "财务资金与费用管理", "shape": "mapping", "status": "待核", "maturity": "可检索",
        "summary": "样本里有一张抬头写作简称，尚未与证照全称核对完成。",
        "owner_org": "示例金融子公司", "maintainer": "党风廉政办", "applicable": "示例金融子公司",
        "period": "2026年样本", "version": "演示2026-1", "source_doc": "示例金融子公司费用样本", "source_locator": "购买方",
        "body": {
            "unit": "示例金融子公司", "system": "演示费用台账", "source_field": "购买方名称",
            "source_caliber": "发票原文", "standard_code": "D.05.11.016",
            "standard_expect": "购买方名称", "conversion": "简称是否等于本单位全称，尚未核对。",
            "same_object": "待核", "path": "发票影像",
            "checked_by": "", "checked_on": "", "verified": False,
        },
    },
    {
        "id": "map-mix-pay", "kind": "mapping", "code": "对照-综-01", "name": "示例综合单位付款指令日期",
        "plate": "公司治理与决策授权", "shape": "mapping", "status": "已发布", "maturity": "可指导",
        "summary": "资金系统的指令日期是不可逆动作的时点，会议纪要日期不能代替它。",
        "owner_org": "示例综合单位", "maintainer": "党风廉政办", "applicable": "示例综合单位",
        "period": "2026年样本", "version": "演示2026-1", "source_doc": "示例综合单位资金样本", "source_locator": "指令日期",
        "body": {
            "unit": "示例综合单位", "system": "演示资金台账", "source_field": "指令日期",
            "source_caliber": "实际发出付款指令的日期", "standard_code": "D.05.06.009",
            "standard_expect": "指令日期", "conversion": "无需换算。",
            "same_object": "同一笔增资付款", "path": "资金台账按事项编号调阅",
            "checked_by": "演示核对", "checked_on": "2026-05-22", "verified": True,
        },
    },
    {
        "id": "map-eng-bid", "kind": "mapping", "code": "对照-工-01", "name": "示例工程企业投标报价",
        "plate": "采购、合同与资产管理", "shape": "mapping", "status": "试行", "maturity": "可参考",
        "summary": "投标台账报价含暂列金，与合同额口径不同，对照时要单列。",
        "owner_org": "示例工程企业", "maintainer": "党风廉政办", "applicable": "示例工程企业",
        "period": "2026年样本", "version": "演示2026-1", "source_doc": "示例工程企业投标样本", "source_locator": "报价",
        "body": {
            "unit": "示例工程企业", "system": "演示投标台账", "source_field": "投标报价",
            "source_caliber": "含暂列金", "standard_code": "D.19.01.006",
            "standard_expect": "投标报价金额", "conversion": "比较控制价前扣除暂列金并注明。",
            "same_object": "同一标段", "path": "投标台账F列",
            "checked_by": "演示核对", "checked_on": "2026-03-02", "verified": True,
        },
    },
]

TRIALS = [
    {
        "algo_code": "A.04.01.001",
        "title": "厂区安防改造样本试运行",
        "summary": "用示例制造企业三笔立项试跑。合并含税估算价526万元，超过货物限额，且没有分批确认。",
        "missing": "招标代理填写联系电话的说明已有；专家抽取记录未调到，不影响拆分这一判断，但影响后续对评审组织的判断。",
        "other_explanations": "联系电话相同曾被当作围标。核对后电话由招标代理统一填写，这一解释排除。拆分规避招标仍然成立。",
        "rows": [
            {"item": "门禁", "amount": "186万元（不含税164.6万元）", "dept": "生产保障部", "level": "并入合计"},
            {"item": "监控", "amount": "192万元", "dept": "生产保障部", "level": "并入合计"},
            {"item": "周界", "amount": "148万元", "dept": "生产保障部", "level": "并入合计"},
            {"item": "合计", "amount": "526万元，限额400万元", "dept": "同一部门同一目的", "level": "高风险"},
        ],
    },
    {
        "algo_code": "A.06.01.004",
        "title": "端午招待样本试运行",
        "summary": "示例金融子公司三笔餐饮，两笔落在放假日期。其中一笔对象是本单位值班人员，不能按外部招待直接认定。",
        "missing": "第三笔的菜单未附，对象是否含供应商尚未闭合。",
        "other_explanations": "内部值班餐误入招待科目，是必须排除的解释。审批日期晚于发票的那一笔，不适用事后补批。",
        "rows": [
            {"item": "6月19日", "amount": "人均280元", "dept": "对象为外部机构", "level": "中风险，审批晚于消费"},
            {"item": "6月20日", "amount": "人均90元", "dept": "签名均为本单位值班人员", "level": "先排除，疑似科目用错"},
            {"item": "6月20日晚餐", "amount": "人均460元", "dept": "菜单缺失", "level": "待补证"},
        ],
    },
]

PURCHASE_PARAS = [
    ("p1", "deployment", "中信集团演示〔2026〕12号  关于进一步规范采购组织的工作要求。各所属企业：为防止把应当公开招标的项目拆开实施，提出以下要求。"),
    ("p2", "requirement", "一、公开招标限额。所属企业采购货物、服务单项合同估算价达到人民币400万元以上、工程达到人民币800万元以上的，应当公开招标。估算价按含税金额计算。限额以下但归口部门另有规定的，从其规定。"),
    ("p3", "requirement", "二、禁止化整为零。同一年度内，同一需求部门就同一品目、同一使用目的提出的采购需求，不得拆分立项、分签合同，以规避公开招标限额。估算价应当合并计算。"),
    ("p4", "requirement", "三、允许分批的条件。确因技术条件、需求时点或资金安排不能合并实施的，可以分批，但须同时满足：各批次需求相互独立；归口管理部门书面确认；未通过分批使每一笔落入限额以下。仅以预算不足、年底突击为由的，不构成分批事由。"),
    ("p5", "requirement", "四、例外批准。达到限额确需采用邀请招标、竞争性谈判或单一来源的，应当事先取得集团采购归口部门批准。批准文件应当载明法定或制度规定的情形、论证意见和有效期。未经批准先行实施的，事后补办不予认可。"),
    ("p6", "requirement", "五、档案留存。采购方式审批表、立项文件、招标文件、评标报告、中标通知书和合同应当一并归档，保存期限不少于15年。缺任一关键文件的，不得办理结算。"),
    ("p7", "requirement", "六、报送时限。所属企业应当于每季度结束后15个工作日内，向集团报送本季度达到限额80%以上的采购项目清单。清单包括项目名称、品目、估算价、采购方式和是否分批。"),
    ("p8", "deployment", "七、传达安排。请各单位于下周五前将本通知传达至采购岗位，并在月度例会上口头强调。"),
    ("p9", "ambiguous", "八、对重大采购，相关负责人应当严格把关，确保程序规范、结果公正。"),
    ("p10", "untouched", "九、本要求自印发之日起施行，由集团采购归口部门负责解释。以往规定与本要求不一致的，按本要求执行。"),
]

INSPECT_PARAS = [
    ("i1", "fact", "示例单位党委巡视情况报告（演示）。巡视组于2026年4月进驻示例制造企业，了解采购组织情况。以下为演示材料，不是对真实企业的结论。"),
    ("i2", "fact", "问题一的事实经过。2026年2月，生产保障部（台账简称为安防组）分三笔立项厂区安防改造：门禁186万元、监控192万元、周界148万元，方式均为邀请招标，合同在3月18日至4月2日签署。"),
    ("i3", "experience", "核查时先把三笔按同一需求部门、同一使用目的加总，含税合计526万元，超过货物公开招标限额。台账金额原为不含税，换算后仍然超过。这一步比先查供应商关系更有效。"),
    ("i4", "experience", "两家供应商投标联系电话相同，起初被看成围标。4月28日招标代理书面说明，电话是代理按格式统一填写。因此不能仅凭联系方式认定围标。拆分规避招标这一判断不受影响。"),
    ("i5", "experience", "有效的核查顺序是：合并计算，对照限额，调取分批书面确认，核对实施日和批准日，最后才辨析供应商关系。2025年另一次核查先做工商穿透，走了弯路。"),
    ("i6", "experience", "归口部门确认，没有分批的书面确认，口头理由是预算不足。预算不足不构成允许分批的事由。"),
    ("i7", "experience", "整改回头看。2025年该企业就同类问题报过完成，措施是传达通知和自行填表，立项环节仍然只看单笔金额。2026年再次出现。原销号应当撤销。反复的原因是措施没有打在审核动作上。"),
    ("i8", "experience", "不能沿用的情形：单笔已经超过限额并履行公开招标的，不使用上述顺序；联系方式由招标文件给定、代理统一填写的，不把电话相同当成串通的支持证据。"),
    ("i9", "deployment", "建议该企业在下月办公会上再次学习采购纪律。此句是会议部署，不是可以单独引用的经验。"),
]


def task_rows():
    return [
        ("task-purchase", "梳理采购工作要求", "监督要求", "待审核", "从一份工作要求中拆出多项要求", "集团总部及所属企业", "一份通知里同时有限额、禁止拆分、分批、例外、归档和报送。传达安排不应入库。第八条过于笼统，需要追问。", "质量关尚未全部通过，不能整单发布。"),
        ("task-inspect", "萃取巡视报告中的经验", "核查经验", "办理中", "从一份巡视报告中拆出多项经验", "示例制造企业（演示）", "报告同时含事实、核查顺序、被排除的围标解释、走弯路的取证和整改反复。", "事实段只作载体。判断转折尚未全部确认。"),
        ("task-sz", "决策程序材料补充", "监督要求", "待补充", "核对先实施后补程序的日期", "示例综合单位", "付款指令日期已经对照，紧急处置的补报材料还没有。", "缺24小时补报，例外不能成立。"),
        ("task-holiday", "节日招待辨析", "核查经验", "待审核", "把节假日发票分成不同解释", "示例金融子公司", "两笔日期敏感，一笔更像内部值班餐。", "菜单缺失的一笔停在补证。"),
        ("task-rectify", "整改回头看入库", "核查经验", "已发布", "把反复发生的原因写成可引用的经验", "示例综合单位", "已发布为整改验证经验，并连接到安防改造复盘。", "2026-05-08 发布"),
        ("task-hr", "干部任前审核要点", "监督要求", "草稿", "整理凡提四必和影响期", "人力资源部", "只收集了制度目录，尚未逐条拆解。", ""),
        ("task-account", "账户归集口径", "数据对照", "办理中", "核对免归集批复与账户清单", "示例金融子公司", "监管专户的批复样本未到。", ""),
        ("task-clue", "线索研判记录方式", "核查经验", "已退回", "讨论谈话记录怎样才算数", "驻集团纪检监察组", "初稿把一次演示谈话写成了在办线索结论，已退回。", "退回原因：事实被写成了结论。"),
        ("task-tech", "账号回收要求", "监督要求", "已发布", "确认离职账号回收的要求表述", "科技与数字化部", "已发布，连接到系统账号数据标准的待核引用。", "2026-03-19 发布"),
        ("task-abroad", "境外投资程序", "监督要求", "试行", "整理先备案后交割", "投资管理部", "条文已拟，适用金融类子公司的差别尚未写完，故为试行。", ""),
    ]


def candidates():
    rows = []
    # purchase
    mapping = [
        ("c-p2", "task-purchase", "mat-purchase", "rule", "公开招标限额", "已确认", "材料写明", "高", "p2", "货物服务400万元、工程800万元，含税。", {"modality": "应当", "actor": "所属企业", "action": "达到限额时公开招标", "target": "货物、服务、工程", "conditions": ["含税估算价"], "exceptions": [], "verify": ["估算价"], "article": "第一条"}, ""),
        ("c-p3", "task-purchase", "mat-purchase", "rule", "禁止化整为零", "已确认", "材料写明", "高", "p3", "同一年度、同一部门、同一目的不得拆分。", {"modality": "不得", "actor": "需求部门", "action": "拆分立项", "target": "同一采购需求", "conditions": ["合并计算"], "exceptions": [], "verify": ["立项合计"], "article": "第二条"}, ""),
        ("c-p4", "task-purchase", "mat-purchase", "rule", "允许分批的条件", "已确认", "材料写明", "高", "p4", "三项条件要同时满足。", {"modality": "可以", "actor": "所属企业", "action": "分批", "target": "不能合并的需求", "conditions": ["相互独立", "书面确认", "不得借分批压低金额"], "exceptions": [], "verify": ["确认单"], "article": "第三条"}, ""),
        ("c-p5", "task-purchase", "mat-purchase", "rule", "例外批准", "已确认", "材料写明", "高", "p5", "事先批准，事后补办不予认可。", {"modality": "应当", "actor": "所属企业", "action": "非公开方式事先报批", "target": "达到限额的项目", "conditions": ["实施前"], "exceptions": [], "verify": ["批准日期"], "article": "第四条"}, ""),
        ("c-p6", "task-purchase", "mat-purchase", "rule", "档案与不得结算", "待人员确认", "模型归纳", "中", "p6", "归档和不得结算写在同一段。模型建议拆成档案义务和结算条件，请确认是否拆开。", {"modality": "应当", "actor": "实施部门", "action": "归档并且在缺件时停止结算", "target": "采购档案", "conditions": [], "exceptions": [], "verify": ["归档目录"], "article": "第五条"}, ""),
        ("c-p7", "task-purchase", "mat-purchase", "rule", "季度报送", "已确认", "材料写明", "高", "p7", "季后15个工作日。", {"modality": "应当", "actor": "所属企业", "action": "报送清单", "target": "达到限额80%的项目", "conditions": ["15个工作日"], "exceptions": [], "verify": ["报送日期"], "article": "第六条"}, ""),
        ("c-p8", "task-purchase", "mat-purchase", "abandon", "周五前口头传达", "已放弃", "材料写明", "高", "p8", "这是一次性传达安排。", {}, "这是会议部署，不是长期要求"),
        ("c-p9", "task-purchase", "mat-purchase", "rule", "相关负责人严格把关", "待判断", "模型归纳", "低", "p9", "看不出谁是相关负责人，也看不出重大采购的金额或种类。", {"modality": "应当", "actor": "", "action": "严格把关", "target": "重大采购", "conditions": [], "exceptions": [], "verify": [], "article": "第八条"}, ""),
    ]
    for item in mapping:
        rows.append(item)
    rows.append(("c-i3", "task-inspect", "mat-inspect", "knowledge", "先合并计算再看关系", "已确认", "材料写明", "高", "i3", "加总比先查供应商更有效。", {"situation": "多笔采购", "cannot_conclude": "不要把顺序反过来"}, ""))
    rows.append(("c-i4", "task-inspect", "mat-inspect", "knowledge", "电话相同不能直接认定围标", "已确认", "材料写明", "高", "i4", "代理填写说明改变了判断。", {"situation": "联系方式相同", "cannot_conclude": "不能仅凭电话认定围标"}, ""))
    rows.append(("c-i5", "task-inspect", "mat-inspect", "knowledge", "核查顺序和曾经的弯路", "待人员确认", "模型归纳", "中", "i5", "模型把有效顺序和2025年弯路放在同一项，建议拆成顺序、弯路两条。", {"situation": "采购核查", "cannot_conclude": "顺序尚未拆开"}, ""))
    rows.append(("c-i6", "task-inspect", "mat-inspect", "knowledge", "预算不足不构成分批事由", "已确认", "材料写明", "高", "i6", "与允许分批的条件相互印证。", {"situation": "口头称预算不足", "cannot_conclude": "不能把口头理由当成书面确认"}, ""))
    rows.append(("c-i7", "task-inspect", "mat-inspect", "knowledge", "整改后再次发生", "已确认", "材料写明", "高", "i7", "措施没有改变立项审核。", {"problem": "拆分立项", "cause": "只看单笔", "verify": "新项目仍可加总超限"}, ""))
    rows.append(("c-i8", "task-inspect", "mat-inspect", "knowledge", "不能沿用的情形", "待判断", "材料写明", "中", "i8", "这是使用边界。可以并入前面各项，也可以单独成项。尚未选择。", {"boundary": "单笔已公开招标的不适用"}, ""))
    rows.append(("c-i2", "task-inspect", "mat-inspect", "fact", "三笔立项的事实", "已确认", "材料写明", "高", "i2", "只作为案例载体，不发布成要求或经验。", {}, ""))
    rows.append(("c-i9", "task-inspect", "mat-inspect", "abandon", "下月办公会学习", "已放弃", "材料写明", "高", "i9", "会议部署。", {}, "这是会议部署，不是可引用的经验"))
    return rows
