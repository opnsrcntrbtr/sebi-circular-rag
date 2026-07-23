# Regulation edge precision audit

Sample: 50 of 1268 edges, stratified by evidence tier, seed=20260723.

Mark `[x]` when the circular genuinely cites that regulation. Then run:

    PYTHONPATH=src .venv/bin/python scripts/audit_reg_edges.py --score reports/reg_edge_audit.md

| edge | evidence / clause | correct |
| --- | --- | --- |
| SEBI/HO/CFD/PoD-1/P/CIR/2023/31 -> substantial-acquisition-of-shares-and-takeovers-2011 | subject_line | [x] |
| <sub>Master Circular for Securities and Exchange Board of India (Substantia</sub> | <sub>Securities and Exchange Board of India (Substantial Acquisition of Sha</sub> | |
| SEBI/HO/DDHS/P/CIR/2022/0063 -> listing-obligations-and-disclosure-requirements-2015 | subject_line | [x] |
| <sub>Relaxation from compliance with certain provisions of the SEBI (Listin</sub> | <sub>Securities and Exchange Board of India (Listing Obligations and Disclo</sub> | |
| SEBI/HO/DDHS/DDHS-POD-1/P/CIR/2025/84 -> issue-and-listing-of-non-convertible-securities-2021 | subject_line | [x] |
| <sub>Framework for Environment, Social and Governance (ESG) Debt Securities</sub> | <sub>Securities and Exchange Board of India (Issue and Listing of Non-Conve</sub> | |
| SEBI/HO/DDHS/DDHS-POD2/P/CIR/2025/101 -> credit-rating-agencies-1999 | subject_line | [x] |
| <sub>Master Circular for Credit Rating Agencies I. Securities and Exchange </sub> | <sub>Securities and Exchange Board of India (Credit Rating Agencies) Regula</sub> | |
| SEBI/HO/DDHS/DDHS_Div1/P/CIR/2022/159 -> issue-and-listing-of-non-convertible-securities-2021 | subject_line | [x] |
| <sub>Reporting of trades in non-convertible securities under SEBI (Issue an</sub> | <sub>Securities and Exchange Board of India (Issue and Listing of Non-Conve</sub> | |
| SEBI/HO/AFD/AFD-POD-1/P/CIR/2025/126 -> alternative-investment-funds-2012 | subject_line | [x] |
| <sub>Framework for AIFs to make co-investment within the AIF structure unde</sub> | <sub>Securities and Exchange Board of India (Alternative Investment Funds) </sub> | |
| SEBI/HO/DDHS/DDHS-PoD-1/P/CIR/2025/83 -> listing-obligations-and-disclosure-requirements-2015 | subject_line | [x] |
| <sub>Limited relaxation from compliance with certain provisions of the SEBI</sub> | <sub>Securities and Exchange Board of India (Listing Obligations and Disclo</sub> | |
| SEBI/HO/CFD/PoD2/CIR/P/2025/47 -> listing-obligations-and-disclosure-requirements-2015 | subject_line | [x] |
| <sub>Clarification on the position of Compliance Officer in terms of regula</sub> | <sub>Securities and Exchange Board of India (Listing Obligations and Disclo</sub> | |
| SEBI/HO/MIRSD/POD-1/P/CIR/2024/37 -> listing-obligations-and-disclosure-requirements-2015 | subject_line | [x] |
| <sub>Master Circular for Registrars to an Issue and Share Transfer Agents I</sub> | <sub>Securities and Exchange Board of India (Listing Obligations and Disclo</sub> | |
| HO/19/34/11(5)2025-AFD-POD1/I/188/2025 -> alternative-investment-funds-2012 | subject_line | [x] |
| <sub>Modalities for migration to AI only schemes and relaxations to Large V</sub> | <sub>Securities and Exchange Board of India (Alternative Investment Funds) </sub> | |
| SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/90 -> stock-brokers-1992 | subject_line | [x] |
| <sub>Master Circular for Stock Brokers I. Securities and Exchange Board of </sub> | <sub>SEBI (Stock Brokers) Regulations, 1992</sub> | |
| SEBI/HO/DDHS/P/CIR/2023/0164 -> listing-obligations-and-disclosure-requirements-2015 | subject_line | [x] |
| <sub>Limited relaxation from compliance with certain provisions of the SEBI</sub> | <sub>Securities and Exchange Board of India (Listing Obligations and Disclo</sub> | |
| SEBI/HO/IMD/IMD-PoD-1/P/CIR/2024/144 -> prohibition-of-insider-trading-2015 | subject_line | [x] |
| <sub>Inclusion of Mutual Fund units in the SEBI (Prohibition of Insider Tra</sub> | <sub>Securities and Exchange Board of India (Prohibition of Insider Trading</sub> | |
| SEBI/HO/MIRSD/MIRSD-PoD-2/P/CIR/2023/168 -> investment-advisers-2013 | subject_line | [x] |
| <sub>Extension in timeline for compliance with qualification and experience</sub> | <sub>Securities and Exchange Board of India (Investment Advisers) Regulatio</sub> | |
| SEBI/HO/DDHS/DDHS-RACPOD1/P/CIR/2023/027 -> issue-and-listing-of-non-convertible-securities-2021 | subject_line | [x] |
| <sub>Clarification w.r.t. issuance and listing of perpetual debt instrument</sub> | <sub>Securities and Exchange Board of India (Issue and Listing of Non-Conve</sub> | |
| SEBI/HO/DDHS/POD3/P/CIR/2024/45 -> credit-rating-agencies-1999 | subject_line | [x] |
| <sub>Master Circular for ESG Rating Providers (“ERPs”) I. ESG Rating Provid</sub> | <sub>Securities and Exchange Board of India (Credit Rating Agencies) Regula</sub> | |
| HO/49/14/14(7)2025-CFD-POD2/I/3762/2026 -> listing-obligations-and-disclosure-requirements-2015 | subject_line | [x] |
| <sub>Master Circular for compliance with the provisions of the Securities a</sub> | <sub>Securities and Exchange Board of India (Listing Obligations and Disclo</sub> | |
| SEBI/HO/DDHS/DDHS-PoD-1/P/CIR/2024/141 -> issue-and-listing-of-non-convertible-securities-2021 | powers_clause / 55 | [x] |
| <sub>Introduction of Liquidity Window facility for investors in debt securi</sub> | <sub>Securities and Exchange Board of India (Issue and Listing of Non-Conve</sub> | |
| SEBI/HO/DDHS/RACPOD1/CIR/P/2022/136 -> credit-rating-agencies-1999 | powers_clause / 2A | [x] |
| <sub>Extension of timeline for entering the details of the existing outstan</sub> | <sub>Securities and Exchange Board of India (Credit Rating Agencies) Regula</sub> | |
| SEBI/HO/MRD/TPD/CIR/P/2025/08 -> depositories-and-participants-2018 | powers_clause / 51 | [x] |
| <sub>- Development of Web-based portal: iSPOT(Integrated SEBI Portal for Te</sub> | <sub>Securities and Exchange Board of India (Depositories and Participants)</sub> | |
| HO/17/11/24(1)2026-DDHS-POD1/I/5967/2026 -> issue-and-listing-of-non-convertible-securities-2021 | powers_clause / 55 | [x] |
| <sub>Revised Norms for appointment of an independent third-party reviewer/ </sub> | <sub>Securities and Exchange Board of India (Issue and Listing of Non-Conve</sub> | |
| SEBI/HO/DDHS/RACPOD1/CIR/P/2022/136 -> debenture-trustees-1993 | powers_clause / 2A | [x] |
| <sub>Extension of timeline for entering the details of the existing outstan</sub> | <sub>Securities and Exchange Board of India (Debenture Trustees) Regulation</sub> | |
| SEBI/HO/IMD/IMD-SEC-3/P/CIR/2025/15 -> mutual-funds-1996 | powers_clause | [x] |
| <sub>Service platform for investors to trace inactive and unclaimed Mutual </sub> | <sub>SEBI (Mutual Funds) Regulations, 1996</sub> | |
| SEBI/HO/AFD/AFD-POD-2/P/CIR/2024/104 -> foreign-portfolio-investors-2019 | powers_clause / 22(1) | [x] |
| <sub>Amendment to Circular for mandating additional disclosures by FPIs tha</sub> | <sub>Securities and Exchange Board of India (Foreign Portfolio Investors) R</sub> | |
| SEBI/HO/DDHS/DDHS_Div1/P/CIR/2022/176 -> issue-and-listing-of-non-convertible-securities-2021 | powers_clause / 2A | [x] |
| <sub>Clarification to SEBI circular dated August 04, 2022 on enhanced guide</sub> | <sub>Securities and Exchange Board of India (Issue and Listing of Non-Conve</sub> | |
| DOF3/P/CIR/2022/39 -> mutual-funds-1996 | powers_clause / 25(19) | [x] |
| <sub>Timelines for Rebalancing of Portfolios of Mutual Fund Schemes</sub> | <sub>SEBI (Mutual Funds) Regulations, 1996</sub> | |
| SEBI/HO/DDHS/DDHS-PoD-2/I/11698/2026 -> infrastructure-investment-trusts-2014 | powers_clause / 33 | [x] |
| <sub>Status of SPVs post conclusion or termination of Concession Agreement.</sub> | <sub>Securities and Exchange Board of India (Infrastructure Investment Trus</sub> | |
| SEBI/HO/DDHS-PoD-1/P/CIR/2025/117 -> issue-and-listing-of-non-convertible-securities-2021 | powers_clause / 2A | [x] |
| <sub>Master Circular for Debenture Trustees</sub> | <sub>Securities and Exchange Board of India (Issue and Listing of Non-Conve</sub> | |
| SEBI/HO/IMD/IMD-PoD-1/P/CIR/2025/38 -> mutual-funds-1996 | powers_clause / 58(1) | [x] |
| <sub>Extension of timelines for submission of offsite inspection data</sub> | <sub>SEBI (Mutual Funds) Regulations, 1996</sub> | |
| SEBI/HO/DDHS/DDHS-PoD-3/P/CIR/2025/009 -> listing-obligations-and-disclosure-requirements-2015 | powers_clause / 2A | [x] |
| <sub>Format of Due Diligence Certificate to be given by the DTs</sub> | <sub>Securities and Exchange Board of India (Listing Obligations and Disclo</sub> | |
| HO/24/11/24(62)2026-IMD-RAC4/I/11872/2026 -> mutual-funds-2026 | powers_clause | [x] |
| <sub>Revision of Monthly Cumulative Report (MCR) Format</sub> | <sub>Securities and Exchange Board of India (Mutual Funds) Regulations, 202</sub> | |
| SEBI/HO/DDHS/DDHS-RACPOD1/P/CIR/2023/9 -> issue-and-listing-of-securitised-debt-instruments-and-security-receipts-2008 | powers_clause / 55 | [x] |
| <sub>Mode of settlement for trades executed on the Request for Quote (RFQ) </sub> | <sub>Securities and Exchange Board of India (Issue and Listing of Securitis</sub> | |
| SEBI/HO/MIRSD/CRADT/CIR/P/2022/38 -> issue-and-listing-of-municipal-debt-securities-2015 | powers_clause / 2A | [x] |
| <sub>Operational guidelines for ‘Security and Covenant Monitoring’ using Di</sub> | <sub>Securities and Exchange Board of India (Issue and Listing of Municipal</sub> | |
| SEBI/HO/MRD/POD-III/CIR/P/2025/134 -> depositories-and-participants-2018 | powers_clause / 51 | [x] |
| <sub>Review of Block Deal Framework</sub> | <sub>Securities and Exchange Board of India (Depositories and Participants)</sub> | |
| SEBI/HO/MRD2/DDAP/CIR/P/2021/18 -> depositories-and-participants-1996 | body_text | [x] |
| <sub>Master Circular for Depositories</sub> | <sub>SEBI (Depositories and Participants) Regulations, 1996</sub> | |
| SEBI/HO/MIRSD/DoR/P/CIR/2022/61 -> intermediaries-2008 | body_text | [x] |
| <sub>Guidelines for seeking NOC by Stock Brokers / Clearing Members for set</sub> | <sub>Securities and Exchange Board of India (Intermediaries) Regulations, 2</sub> | |
| CIR/IMD/DF/5/2013 -> mutual-funds-1996 | body_text | [x] |
| <sub>Master Circular for Mutual Funds For effective regulation of the Mutua</sub> | <sub>SEBI (Mutual Funds) Regulations, 1996</sub> | |
| SEBI/HO/AFD-1/AFD-1-PoD/P/CIR/2024/39 -> registrars-to-an-issue-and-share-transfer-agents-1993 | body_text | [x] |
| <sub>Master Circular for Alternative Investment Funds (AIFs)</sub> | <sub>SEBI (Registrars to an Issue and Share Transfer Agents) Regulations, 1</sub> | |
| SEBI/HO/DDHS-PoD1/P/CIR/2023/109 -> debenture-trustees-1993 | body_text | [x] |
| <sub>Master Circular for Debenture Trustees</sub> | <sub>Securities and Exchange Board of India (Debenture Trustees) Regulation</sub> | |
| SEBI/HO/DDHS/DDHS-POD-2/P/CIR/2025/100 -> intermediaries-2008 | body_text | [x] |
| <sub>Master Circular for ESG Rating Providers (“ERPs”) I. ESG Rating Provid</sub> | <sub>Securities and Exchange Board of India (Intermediaries) Regulations, 2</sub> | |
| SEBI/HO/AFD/AFD-PoD-1/P/CIR/2025/066 -> certification-of-associated-persons-in-the-securities-markets-2007 | body_text / 4 | [x] |
| <sub>Extension of timeline for complying with the certification requirement</sub> | <sub>SEBI (Certification of Associated Persons in the Securities Markets) R</sub> | |
| SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2023/79 -> listing-obligations-and-disclosure-requirements-2015 | body_text / 7(4) | [x] |
| <sub></sub> | <sub>Securities and Exchange Board of India (Listing Obligations and Disclo</sub> | |
| SEBI/HO/AFD-1/AFD-1-PoD/P/CIR/2024/39 -> prohibition-of-insider-trading-2015 | body_text | [x] |
| <sub>Master Circular for Alternative Investment Funds (AIFs)</sub> | <sub>Securities and Exchange Board of India (Prohibition of Insider Trading</sub> | |
| SEBI/HO/IMD/IMD-PoD-1/P/CIR/2023/133 -> portfolio-managers-2020 | body_text / 43 | [x] |
| <sub>Audit of firm-level performance data of Portfolio Managers</sub> | <sub>Securities and Exchange Board of India (Portfolio Managers) Regulation</sub> | |
| HO/47/12/11(5)2025-MRD-POD3/I/196/2025 -> depositories-and-participants-2018 | body_text | [x] |
| <sub>Provisions relating to Strengthening Governance of Market Infrastructu</sub> | <sub>Securities and Exchange Board of India (Depositories and Participants)</sub> | |
| SEBI/HO/IMD/IMD-PoD-1/P/CIR/2024/90 -> portfolio-managers-2020 | body_text | [x] |
| <sub>Master Circular for Mutual Funds</sub> | <sub>Securities and Exchange Board of India (Portfolio Managers) Regulation</sub> | |
| SEBI/HO/MIRSD/DOP1/CIR/P/2018/87 -> stock-brokers-and-sub-brokers-1992 | body_text | [x] |
| <sub>Master Circular for Stock Brokers</sub> | <sub>SEBI (Stock brokers and sub-brokers) Regulations, 1992</sub> | |
| SEBI/HO/AFD/PoD1/CIR/2024/027 -> alternative-investment-funds-2012 | body_text | [x] |
| <sub>Framework for Category I and II Alternative Investment Funds (AIFs) to</sub> | <sub>Securities and Exchange Board of India (Alternative Investment Funds) </sub> | |
| SEBI/HO/IMD/IMD-POD1/P/CIR/2023/005 -> mutual-funds-1996 | body_text / 24 | [x] |
| <sub>Management and advisory services by AMCs to Foreign Portfolio Investor</sub> | <sub>SEBI (Mutual Funds) Regulations, 1996</sub> | |
| SEBI/HO/DDHS/DDHS_Div3/P/CIR/2022/52 -> issue-and-listing-of-debt-securities-2008 | body_text | [x] |
| <sub>Master Circular for Real Estate Investment Trusts (REITs)</sub> | <sub>SEBI (Issue and Listing of Debt Securities) Regulations, 2008</sub> | |
