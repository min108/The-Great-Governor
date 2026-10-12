ORGS = [
    ("org-jw", "中央纪委国家监委驻中国中信集团有限公司纪检监察组", "驻集团纪检监察组", "dispatched", "派驻监督机构", "", 1),
    ("org-bgt", "办公厅", "办公厅", "headquarters", "总部机构", "办公运行与综合管理", 2),
    ("org-board", "董事会办公室", "董事会办公室", "headquarters", "总部机构", "公司治理与决策授权", 3),
    ("org-strategy", "战略发展部", "战略发展部", "headquarters", "总部机构", "战略经营与改革发展", 4),
    ("org-invest", "投资管理部", "投资管理部", "headquarters", "总部机构", "投资、产权与境外管理", 5),
    ("org-finance", "财务管理部", "财务管理部", "headquarters", "总部机构", "财务资金与费用管理", 6),
    ("org-hr", "人力资源部", "人力资源部", "headquarters", "总部机构", "干部人事与薪酬福利", 7),
    ("org-syn", "业务协同部", "业务协同部", "headquarters", "总部机构", "业务协同与关联交易", 8),
    ("org-risk", "风险合规部", "风险合规部", "headquarters", "总部机构", "风险合规与法律事务", 9),
    ("org-audit", "审计部", "审计部", "headquarters", "总部机构", "审计监督与整改", 10),
    ("org-tech", "科技与数字化部", "科技与数字化部", "headquarters", "总部机构", "科技与数据管理", 11),
    ("org-party", "党群工作部", "党群工作部", "headquarters", "总部机构", "党的领导与党的建设", 12),
    ("org-lzb", "党委巡视办（党风廉政办）", "党风廉政办", "headquarters", "大监督体系建设牵头部门。对外可称党委巡视办，对内履行党风廉政办职责。", "纪检巡视与廉洁作风", 13),
]

SUBS = [
    "中信金控", "中信银行", "中信证券", "中信建投证券", "中信信托", "中信保诚人寿", "中信金融资产", "中信财务",
    "中信装备", "中信重工", "中信戴卡", "中信控股", "中信金属", "中信矿业国际", "中信出版", "中信农业",
    "中信数字科技", "中信国际电讯", "中信建设", "中信城开", "中信华创", "中信和业", "中信缅甸", "中信环境",
    "中信医疗", "中信海直", "中信咨询", "中信泰富", "中信特钢", "中信能源", "中信兴业", "中信投资控股",
    "中信国安", "中信欧洲", "中国政企基金",
]

DEMO_UNITS = [
    ("org-demo-fin", "示例金融子公司", "示例金融子公司", "demo", "演示用主体，不代表任何一家真实子公司的经营或监督结论。", "财务资金与费用管理", 100),
    ("org-demo-mfg", "示例制造企业", "示例制造企业", "demo", "演示用主体，用于大宗采购与制造场景，不对应真实企业。", "采购、合同与资产管理", 101),
    ("org-demo-eng", "示例工程企业", "示例工程企业", "demo", "演示用主体，用于工程发包场景。", "采购、合同与资产管理", 102),
    ("org-demo-mix", "示例综合单位", "示例综合单位", "demo", "演示用主体，用于招待、决策和整改场景。", "纪检巡视与廉洁作风", 103),
]


def organizations():
    rows = list(ORGS)
    for i, name in enumerate(SUBS, start=20):
        rows.append((f"org-sub-{i}", name, name, "subsidiary", "一级子公司。名录用于建设范围和适用范围，不据此推断股权。", "", i))
    rows.extend(DEMO_UNITS)
    return rows


OBJECTS = [
    ("obj-post-purchase", "post", "采购归口管理岗", "负责采购方式合规性审核，不得同时担任需求提出和评标组织。", "org-lzb", {"duty": "方式审核、限额合并计算、例外受理", "separation": "与需求部门、评标专家库管理分离"}),
    ("obj-post-finance", "post", "费用审核岗", "审核招待报销的事前审批、标准和发票。", "org-finance", {"duty": "标准审核、节假日标识、抬头核验"}),
    ("obj-supplier-a", "supplier", "演示供应商甲", "演示项目中的中标候选人，注册地址与演示供应商乙相邻。", "org-demo-mfg", {"credit_code": "91310000DEMO00001A", "contact": "021-60000001", "note": "演示主体"}),
    ("obj-supplier-b", "supplier", "演示供应商乙", "与甲使用同一联系电话，需辨析是否围标或商务代办。", "org-demo-mfg", {"credit_code": "91310000DEMO00002B", "contact": "021-60000001", "note": "演示主体"}),
    ("obj-supplier-c", "supplier", "演示供应商丙", "联系方式独立，报价偏离合理。", "org-demo-mfg", {"credit_code": "91310000DEMO00003C", "contact": "010-60000088", "note": "演示主体"}),
    ("obj-project-split", "project", "演示项目·厂区安防改造", "同一使用目的被拆成三笔立项，合计超过公开招标限额。", "org-demo-mfg", {"year": "2026", "lots": ["门禁", "监控", "周界"], "total": "5260000"}),
    ("obj-contract-1", "contract", "演示合同·门禁采购", "估算价186万元，邀请招标，含税口径与台账不一致。", "org-demo-mfg", {"amount_incl_tax": "1860000", "amount_excl_tax": "1646018", "signed": "2026-03-18"}),
    ("obj-contract-2", "contract", "演示合同·监控采购", "估算价192万元，与门禁项目同一需求部门、同一月份。", "org-demo-mfg", {"amount_incl_tax": "1920000", "signed": "2026-03-22"}),
    ("obj-contract-3", "contract", "演示合同·周界采购", "估算价148万元，三笔合计526万元。", "org-demo-mfg", {"amount_incl_tax": "1480000", "signed": "2026-04-02"}),
    ("obj-matter-split", "matter", "化整为零规避招标", "示例制造企业2026年一季度厂区安防改造采购。", "org-demo-mfg", {"chain": ["主体", "决策", "适用要求", "分析思路", "疑点与证据", "核查", "整改"], "thread": "split"}),
    ("obj-matter-sz", "matter", "先实施后补程序的投资决策", "示例综合单位一笔股权增资，资金划出早于党委会。", "org-demo-mix", {"thread": "sanzhong", "decision_date": "2026-05-20", "pay_date": "2026-04-11"}),
    ("obj-matter-ent", "matter", "节假日业务招待", "示例金融子公司端午期间三笔餐饮报销。", "org-demo-fin", {"thread": "entertain", "dates": ["2026-06-19", "2026-06-20"]}),
    ("obj-matter-rect", "matter", "巡视成果运用与整改回头看", "示例综合单位采购领域问题的整改与再次发生。", "org-demo-mix", {"thread": "rectify", "round": "2025年常规巡视"}),
    ("obj-person-li", "person", "李某（化名）", "示例制造企业采购部负责人，演示材料中的经办人。", "org-demo-mfg", {"role": "需求部门负责人"}),
    ("obj-person-zhou", "person", "周某（化名）", "示例综合单位分管投资的副总经理。", "org-demo-mix", {"role": "决策环节分管领导"}),
]
