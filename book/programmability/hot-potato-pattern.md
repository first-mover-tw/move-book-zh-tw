---
description: 'The Hot Potato pattern in Move: a struct with no abilities that must be consumed in the same transaction, enforcing workflow completion.'
---

# 模式：Hot Potato (燙手山芋)

在能力系統中有一種特殊情況 —— 沒有任何能力的結構體，被稱為 _Hot Potato_。它不能被儲存（既不能作為[物件](./../storage/key-ability)，也不能作為[另一個結構體的欄位](./../storage/store-ability)），不能被[複製](./../move-basics/copy-ability)或[捨棄](./../move-basics/drop-ability)。因此，一旦建構，它必須優雅地被[其模組拆解](./../move-basics/struct)，否則交易會因為存在未被捨棄的未使用值而中止 (abort)。

> 如果您熟悉支援「回呼」(callbacks) 的語言，您可以將 Hot Potato 視為呼叫回呼函式的義務。如果您不呼叫它，交易將會中止。

這個名稱源於孩子們的遊戲，球在玩家之間快速傳遞，音樂停止時，沒有人想成為最後一個拿著球的人，否則就出局了。這是對該模式最好的詮釋 —— Hot Potato 結構體的實例在呼叫之間傳遞，沒有模組可以保留它。

## 定義 Hot Potato

Hot Potato 可以是任何沒有能力的結構體。例如：

```move
public struct Request {
    /* 欄位 */
}
```

由於 `Request` 沒有能力，不能儲存或忽略，模組必須提供一個函式來拆解 (unpack) 它。

## 範例用法：借用 (Borrowing)

在容器借用的情境中，Hot Potato 可以確保借出的值必須歸還到正確的容器中。`Promise` 結構體包含借出物件的 ID 和容器的 ID，確保歸還時不會被偷換。

## 應用場景

- **借用 (Borrowing)：** 如上所述，保證值會歸還。
- **閃電貸 (Flash Loans)：** 確保借出的資金在同一次交易中歸還。
- **可變路徑執行 (Variable-path Execution)：** 解耦購買與付款邏輯（例如「先拿貨，後付款」）。
- **組合模式 (Compositional Patterns)：** 在不同模組甚至套件之間傳遞執行狀態。

## 在 Sui 框架中的使用

- `sui::borrow`
- `sui::transfer_policy` (TransferRequest)
- `sui::token` (ActionRequest)

## 總結

- Hot Potato 是沒有任何能力的結構體，必須配套提供建立和銷毀的方法。
- 用於確保交易結束前必須採取某些行動（類似回呼）。
- 常見用途包括借用、閃電貸、解耦預期行為等。
