# Agent Demo 完整运行输出

- 研究主题：分析2024年新能源汽车行业竞争格局
- Run ID：`sample-nev-2024`
- 最终状态：`completed`
- 说明：本文件由 `agent_demo/main.py` 端到端运行后自动生成。

## 步骤1：任务拆解

**输入：** `分析2024年新能源汽车行业竞争格局`

**输出：**

```json
{
  "topic": "分析2024年新能源汽车行业竞争格局",
  "objective": "用可追溯的行业统计和公司披露判断市场增长、竞争位置与主要风险",
  "sub_questions": [
    "2024年中国新能源汽车市场规模、增速和渗透率如何？",
    "主要厂商的销量规模和增速如何？",
    "不同公司披露口径是否可直接比较？",
    "现有证据支持哪些结论，仍有哪些信息缺口？"
  ],
  "search_queries": [
    "2024 中国 新能源汽车 产销 渗透率",
    "2024 比亚迪 新能源汽车 全球销量 研发投入",
    "2024 吉利 新能源汽车 销量 年度报告",
    "2024 Tesla 全球 交付量"
  ],
  "acceptance_criteria": {
    "minimum_sources": 3,
    "required_source_types": [
      "行业统计",
      "公司公告/年度报告"
    ],
    "all_numeric_claims_need_citations": true,
    "scope_differences_must_be_disclosed": true
  }
}
```

## 步骤2：信息检索

**工具：** `LocalCorpusSearch`

| Evidence ID | 类型 | 来源 | 相关度 |
|---|---|---|---:|
| ev_c66cd9f7c38e | 年度报告 | Geely Automobile Holdings Limited Annual Report 2024 | 1.00 |
| ev_54b361ba5875 | 公司公告 | Tesla Fourth Quarter 2024 Production, Deliveries & Deployments | 1.00 |
| ev_8d31924baefb | 行业统计 | 2024年中国汽车产销量再创新高 | 0.80 |
| ev_841f0b95b755 | 公司公告/新闻稿 | 比亚迪成为CCTV科技强国战略合作伙伴 | 0.64 |

## 步骤3：关键数据提取

**工具：** `StructuredFactExtractor`

| 指标 | 数值 | 口径 | 证据 |
|---|---:|---|---|
| 吉利汽车总销量 | 2,176,567辆 | 公司全球（含领克合营企业100%销量） | ev_c66cd9f7c38e |
| 吉利新能源汽车销量 | 888,235辆 | 公司全球 | ev_c66cd9f7c38e |
| 吉利新能源汽车销量占比 | 41% | 公司全球 | ev_c66cd9f7c38e |
| 吉利中国市场新能源汽车销量 | 849,922辆 | 中国市场 | ev_c66cd9f7c38e |
| Tesla全球汽车交付量 | 1,789,226辆 | 全球/纯电动车 | ev_54b361ba5875 |
| Tesla全球汽车产量 | 1,773,443辆 | 全球/纯电动车 | ev_54b361ba5875 |
| 中国新能源汽车产量 | 1288.8万辆 | 中国市场 | ev_8d31924baefb |
| 中国新能源汽车销量 | 1286.6万辆 | 中国市场 | ev_8d31924baefb |
| 中国新能源汽车销量同比增速 | 35.5% | 中国市场 | ev_8d31924baefb |
| 新能源汽车新车销量占比 | 40.9% | 中国市场 | ev_8d31924baefb |
| 比亚迪全球销量 | 427.21万辆 | 全球/新能源车（含纯电与插混） | ev_841f0b95b755 |
| 比亚迪研发投入 | 542亿元 | 公司全球 | ev_841f0b95b755 |

## 步骤4：人工确认

```json
{
  "decision": "approve",
  "reviewer": "demo-auto-reviewer",
  "reviewed_at": "2026-09-14T14:27:19.125666Z",
  "item_count": 12,
  "note": "自动确认，用于可重复的交付样例"
}
```

## 步骤5：报告生成

报告草稿由 `EvidenceBoundReporter` 根据已确认事实生成，并保存为 `05_draft_report.md`。草稿中的数值主张使用稳定 Evidence ID 就近引用。

## 步骤6：报告质量门禁

```json
{
  "passed": true,
  "checks": [
    {
      "name": "minimum_evidence",
      "passed": true,
      "detail": "4 sources"
    },
    {
      "name": "citation_integrity",
      "passed": true,
      "detail": [
        "ev_54b361ba5875",
        "ev_841f0b95b755",
        "ev_8d31924baefb",
        "ev_c66cd9f7c38e"
      ]
    },
    {
      "name": "numeric_claim_support",
      "passed": true,
      "detail": []
    },
    {
      "name": "required_sections",
      "passed": true,
      "detail": [
        "核心结论",
        "关键数据",
        "竞争格局判断",
        "风险与局限",
        "来源"
      ]
    },
    {
      "name": "scope_disclosure",
      "passed": true,
      "detail": "global/China and BEV/PHEV scopes disclosed"
    },
    {
      "name": "human_review",
      "passed": true,
      "detail": "demo-auto-reviewer"
    }
  ]
}
```

## 运行轨迹

| 序号 | 阶段 | 工具/模型 | 状态 |
|---:|---|---|---|
| 1 | task_decomposition | RuleBasedPlanner | started |
| 2 | task_decomposition | RuleBasedPlanner | completed |
| 3 | retrieval | LocalCorpusSearch | started |
| 4 | retrieval | LocalCorpusSearch | completed |
| 5 | data_extraction | StructuredFactExtractor | started |
| 6 | data_extraction | StructuredFactExtractor | completed |
| 7 | human_review | HumanReviewGate | started |
| 8 | human_review | HumanReviewGate | completed |
| 9 | report_generation | EvidenceBoundReporter | started |
| 10 | report_generation | EvidenceBoundReporter | completed |
| 11 | verification | DeterministicQualityGate | started |
| 12 | verification | DeterministicQualityGate | completed |

## 最终报告

# 2024年新能源汽车行业竞争格局研究摘要

- 研究主题：分析2024年新能源汽车行业竞争格局
- Run ID：`sample-nev-2024`
- 研究范围：中国行业总量与主要企业公开披露

## 核心结论

2024年中国新能源汽车销量达到1286.6万辆，同比增长35.5%，新能源新车销量占比达到40.9%。这说明行业仍处在高增长阶段，同时新能源车已从增量品类进入汽车消费的主流区间。[ev_8d31924baefb]

企业层面呈现“龙头扩大规模、追赶者加速转型、纯电龙头承压”的分化。比亚迪披露2024年全球销量为427.21万辆；吉利新能源汽车销量为888,235辆，同比增长92%，新能源占公司总销量41%；Tesla全球交付量为1,789,226辆，同比约下降1%。[ev_841f0b95b755] [ev_c66cd9f7c38e] [ev_54b361ba5875]

## 关键数据

| 指标 | 2024年数据 | 口径 | 证据 |
|---|---:|---|---|
| 中国新能源汽车销量 | 1286.6万辆 | 中国市场，全年 | [ev_8d31924baefb] |
| 中国新能源汽车销量增速 | 35.5% | 同比 | [ev_8d31924baefb] |
| 新能源新车销量占比 | 40.9% | 占全部汽车新车销量 | [ev_8d31924baefb] |
| 比亚迪销量 | 427.21万辆 | 全球，新能源车含纯电与插混 | [ev_841f0b95b755] |
| 吉利新能源汽车销量 | 888,235辆 | 公司全球 | [ev_c66cd9f7c38e] |
| Tesla汽车交付量 | 1,789,226辆 | 全球，纯电动车 | [ev_54b361ba5875] |

## 竞争格局判断

1. **市场扩容仍是首要变量。** 中国新能源汽车销量同比增长35.5%，渗透率达到40.9%，行业竞争已经从教育市场转向对产品组合、成本效率和渠道覆盖的综合竞争。[ev_8d31924baefb]
2. **比亚迪保持显著规模领先。** 其全球销量约为Tesla全球交付量的2.39倍，但该比值只能表示披露规模差异，不能直接解释同一细分市场份额，因为比亚迪包含插混，Tesla为纯电口径。[ev_841f0b95b755] [ev_54b361ba5875]
3. **吉利是高增速追赶者。** 吉利新能源汽车销量同比增长92%，新能源销量占比达到41%，显示传统自主品牌的新能源转型已经形成规模贡献。[ev_c66cd9f7c38e]
4. **技术投入仍是竞争门槛。** 比亚迪披露研发投入达到542亿元、同比增长36%，说明头部企业仍以研发强度支撑产品迭代与平台化能力。[ev_841f0b95b755]

## 风险与局限

- **统计口径不完全一致：** 行业数据为中国市场销量，企业数据包含全球销量；比亚迪包含纯电和插混，Tesla为纯电。因此报告不据此计算中国市场份额。
- **资料覆盖有限：** 离线演示语料仅覆盖行业总量及三家代表性企业，未覆盖价格带、车型级销量、盈利能力和渠道库存。
- **时点限制：** 报告只讨论2024年已披露数据，不把后续经营表现倒推为2024年结论。

## 来源

- [ev_c66cd9f7c38e] [Geely Automobile Holdings Limited Annual Report 2024](https://www.geelyauto.com.hk/wp-content/uploads/2025/04/e00175_Annual-Report_20250428-1.pdf)，吉利汽车控股有限公司，2025-04-28。
- [ev_54b361ba5875] [Tesla Fourth Quarter 2024 Production, Deliveries & Deployments](https://ir.tesla.com/press-release/tesla-fourth-quarter-2024-production-deliveries-and-deployments)，Tesla Investor Relations，2025-01-02。
- [ev_8d31924baefb] [2024年中国汽车产销量再创新高](https://app.www.gov.cn/govdata/gov/202501/14/523622/article.html)，中国政府网（转引中国汽车工业协会数据），2025-01-14。
- [ev_841f0b95b755] [比亚迪成为CCTV科技强国战略合作伙伴](https://www.bydglobal.com/cn/news/2025-05-27/1617162652697)，比亚迪，2025-05-27。

