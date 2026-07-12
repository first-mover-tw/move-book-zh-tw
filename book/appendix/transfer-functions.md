---
description: 快速參考 (Quick reference)：Sui transfer 函式（transfer, share, freeze, receive）及其
  public 變體的權限與結束狀態。
---

# 附錄 C: 轉移函式

## 轉移函式比較

| 函式                      | 公開函式                | 最終狀態 | 權限                     |
| :------------------------ | :---------------------- | :------- | :----------------------- |
| [`transfer`][transfer]    | `public_transfer`       | 地址擁有 | 完整                     |
| [`share_object`][share]   | `public_share_object`   | 共享     | 參考、可變參考、刪除     |
| [`freeze_object`][freeze] | `public_freeze_object`  | 凍結     | 參考                     |
| [`party_transfer`][party] | `public_party_transfer` | 群組     | [請參閱群組表格](#party) |

## 狀態比較

| 狀態     | 描述                                         |
| :------- | :------------------------------------------- |
| 地址擁有 | 物件可由某個地址（或某個物件）完整存取。     |
| 共享     | 物件可由任何人參考及刪除。                   |
| 凍結     | 物件可透過不可變參考存取。                   |
| 群組     | 取決於群組設定（[請參閱群組表格](#party)）。 |

## 群組 {#party}

| 函式           | 描述                               |
| :------------- | :--------------------------------- |
| `single_owner` | 物件具有與「地址擁有」相同的權限。 |

[transfer]: https://docs.sui.io/references/framework/sui_sui/transfer#sui_transfer_transfer
[share]: https://docs.sui.io/references/framework/sui_sui/transfer#sui_transfer_share_object
[freeze]: https://docs.sui.io/references/framework/sui_sui/transfer#sui_transfer_freeze_object
[party]: https://docs.sui.io/references/framework/sui_sui/transfer#sui_transfer_party_transfer
