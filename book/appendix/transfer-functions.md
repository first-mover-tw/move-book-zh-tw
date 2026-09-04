---
description: 快速參考：Sui 轉移函式 (transfer functions)：轉移 (transfer)、分享 (share)、凍結 (freeze)、接收 (receive)，及其具備權限 (permissions) 與終端狀態 (end states) 的公開變體 (public variants)。
title: '附錄 C: 轉移函式 (Transfer Functions)'
keywords:
  - Move
  - Sui
  - Move tutorial
  - appendix
  - transfer
  - functions
questions:
  - What transfer functions exist in Move?
  - How do I transfer objects?
  - What is public_transfer vs transfer?
answer: Sui provides transfer, public_transfer, share_object, freeze_object, and their variants for moving object ownership between addresses.
goal:
  description: Reader understands all transfer functions available in Sui Move
  requires:
    - has_frontmatter:
        - title
        - description
        - keywords
      label: Has required frontmatter fields
    - min_words: 50
      label: Needs content depth
    - has_questions: true
      label: Needs questions for AI search visibility
    - has_answer: true
      label: Needs answer summary for AI citation
---

# 附錄 C：轉移函式 (Appendix C: Transfer Functions) {#appendix-c-transfer-functions}

## 轉移函式比較 (Transfer Functions Comparison) {#transfer-functions-comparison}

| 函式                      | 公開函式                | 最終狀態 | 權限                        |
| :------------------------ | :---------------------- | :------- | :-------------------------- |
| [`transfer`][transfer]    | `public_transfer`       | 地址擁有 | 完整                        |
| [`share_object`][share]   | `public_share_object`   | 共享     | 參考、可變參考、刪除        |
| [`freeze_object`][freeze] | `public_freeze_object`  | 凍結     | 參考                        |
| [`party_transfer`][party] | `public_party_transfer` | Party    | [請參閱 Party 表格](#party) |

## 狀態比較 (States Comparison) {#states-comparison}

| 狀態     | 說明                                            |
| :------- | :---------------------------------------------- |
| 地址擁有 | 物件可由地址（或物件）完全存取                  |
| 共享     | 物件可由任何人參考及刪除                        |
| 凍結     | 物件可透過不可變參考存取                        |
| Party    | 取決於 Party 設定 ([請參閱 Party 表格](#party)) |

## Party {#party}

| 函式           | 說明                             |
| :------------- | :------------------------------- |
| `single_owner` | 物件具有與「地址擁有」相同的權限 |

[transfer]: https://docs.sui.io/references/framework/sui_sui/transfer#sui_transfer_transfer
[share]: https://docs.sui.io/references/framework/sui_sui/transfer#sui_transfer_share_object
[freeze]: https://docs.sui.io/references/framework/sui_sui/transfer#sui_transfer_freeze_object
[party]: https://docs.sui.io/references/framework/sui_sui/transfer#sui_transfer_party_transfer
