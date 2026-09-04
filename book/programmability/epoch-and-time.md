---
description: Sui Move 中的存取時間：在你的智慧合約中，使用紀元 (epochs) 表示作業期間，並使用時鐘 (Clock) 取得毫秒時間戳記。
title: 紀元 (Epoch) 與時間 (Time)
keywords:
  - Move
  - Sui
  - Move tutorial
  - epoch
  - time
questions:
  - What is Epoch and Time in Move?
  - How do I use Epoch and Time in Move?
  - What is Epoch in Move?
  - What is Time in Move?
answer: 'Access time in Sui Move: use epochs for operational periods and Clock for millisecond timestamps in your smart contracts.'
goal:
  description: 'Reader understands access time in Sui Move: use epochs for operational periods and Clock for millisecond timestamps in your smart contracts'
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

# Epoch 與時間 (Epoch and Time) {#epoch-and-time}

Sui 有兩種存取目前時間的方式：_epoch_ 與 `Clock` 物件。前者代表系統中的運作週期，約每 24 小時變更一次。後者提供自 Unix Epoch 起算的目前時間（毫秒）。兩者皆可在程式中自由存取。

## 時期 (Epoch) {#epoch}

Epoch 用於將系統劃分為不同的運作週期。在一個 epoch 期間，驗證者集合固定不變；在 epoch 邊界時，則可能變更。Epoch 在共識演算法中扮演關鍵角色，並作為質押機制的計量單位。

可從[交易情境](./transaction-context)讀取目前的 epoch：

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=epoch

```

也可以取得 epoch 開始時的 Unix 時間戳記（毫秒）：

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=epoch_start

```

這兩個值皆內嵌於交易本身，因此讀取不需費用，也不需要存取任何物件。

通常，epoch 用於質押與系統操作；不過在自訂情境中，也可用來模擬 24 小時週期。若應用程式依賴質押邏輯，或需要得知目前的驗證者集合，它們便至關重要。

## 時間 (Time) {#time}

如需更精確的時間測量，Sui 提供 `Clock` 物件。這是一個系統物件，由系統交易在每次共識提交時更新——約每四分之一秒一次——並儲存自 Unix Epoch 起算的目前時間（毫秒）。`Clock` 物件定義於 `sui::clock` 模組中，並具有[保留地址](./../appendix/reserved-addresses) `0x6`。

Clock 是共享物件，但嘗試以可變方式存取它的交易將會失敗。這項限制允許平行存取 `Clock` 物件，對維持效能相當重要。

```move
module sui::clock;

/// 向 Move 呼叫公開時間的單例共享物件。此
/// 物件位於地址 0x6，且入口函式只能讀取它（透過
/// 不可變參考存取）。
///
/// 嘗試以 `Clock` 的可變參考或值作為接受參數的
/// 入口函式將無法通過驗證；除非 `Clock` 以不可變
/// 參考傳遞，否則誠實驗證者不會簽署或執行使用
/// `Clock` 作為輸入參數的交易。
public struct Clock has key {
    id: UID,
    /// 時鐘的時間戳記，由系統交易在每次共識提交
    /// 排程時自動設定，或在測試期間由
    /// `sui::clock::increment_for_testing` 設定。
    timestamp_ms: u64,
}
```

在一般使用情況下，該模組公開單一函式：`timestamp_ms`。它會回傳自 Unix Epoch 起算的目前時間（毫秒）。

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=clock

```

`Clock` 提供幾項實用保證：在單一交易內，`timestamp_ms` 總是回傳相同值；跨交易時，該值絕不會減少。不過，由於時鐘僅在共識提交時更新，彼此執行時間相近的交易可能會看到相同的時間戳記。

## 測試 (Testing) {#testing}

由於真實 `Clock` 僅能由系統更新，該模組提供僅供測試使用的函式，可建立時鐘、設定其值，以及銷毀它：

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=test

```

## 總結 (Summary) {#summary}

- 目前的 epoch 與其開始時間戳記可從[交易情境](./transaction-context)讀取——不需費用且每筆交易皆可取得；一個 epoch 約持續 24 小時。
- 保留地址 `0x6` 的 `Clock` 物件提供毫秒時間，並於每次共識提交時更新；只能以不可變方式存取。
- 在一筆交易內，`Clock` 值絕不會變更；跨交易時也絕不會減少。
- 在測試中，使用 `create_for_testing`、`set_for_testing`、`increment_for_testing` 與 `destroy_for_testing` 控制時鐘。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::clock](https://docs.sui.io/references/framework/sui/clock) 模組文件。
