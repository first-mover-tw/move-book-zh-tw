---
description:
  在 Sui Move 中存取時間 (Access Time in Sui Move)：在智慧合約中，操作週期用 epoch (epoch)，毫秒級時間戳記用
  Clock (Clock)。
---

# Epoch 與時間 (Epoch and Time) {#epoch-and-time}

Sui 提供兩種存取當前時間的方式：**epoch** 與 `Clock` 物件。前者代表系統中的操作週期，大約每 24 小時變更一次。後者則提供自 Unix Epoch 以來的毫秒數時間。兩者皆可在程式中自由存取。

## 紀元 (Epoch) {#epoch}

Epoch 用於將系統劃分為各個操作週期。在一個 epoch 期間，驗證者集合是固定的；在 epoch 邊界時，驗證者集合可能會變更。Epoch 在共識演算法中扮演關鍵角色，並在質押機制中作為計量單位使用。

當前的 epoch 可以從[交易上下文 (transaction context)](./transaction-context)讀取：

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=epoch

```

也可以取得該 epoch 開始時的 Unix 時間戳記（以毫秒為單位）：

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=epoch_start

```

這兩個值都內嵌在交易本身之中，因此讀取它們是免費的，也不需要存取任何物件。

一般來說，epoch 用於質押與系統操作，但在自訂情境中，也可以用來模擬 24 小時的週期。如果應用程式依賴質押邏輯，或需要知道當前的驗證者集合，epoch 就顯得至關重要。

## 時間 (Time) {#time}

若需要更精確的時間量測，Sui 提供了 `Clock` 物件。它是一個系統物件，每次共識提交時（大約每四分之一秒）都會由系統交易更新，儲存自 Unix Epoch 以來的當前時間（以毫秒為單位）。`Clock` 物件定義於 `sui::clock` 模組中，並具有[保留地址 (reserved address)](./../appendix/reserved-addresses) `0x6`。

Clock 是一個共享物件，但任何嘗試以可變方式存取它的交易都會失敗。這項限制允許對 `Clock` 物件進行平行存取，這對維持效能十分重要。

```move
module sui::clock;

/// 這是一個對 Move 呼叫公開時間的單例共享物件（Singleton shared object）。這個
/// 物件位於 address 0x6，且只能透過不可變參考（immutable reference）被
/// entry functions 讀取（存取）。
///
/// 若 Entry Functions 試圖以可變參考（mutable reference）或值（value）接受 `Clock`，
/// 將無法通過驗證，而誠實的 validator
/// 也不會簽署或執行以 `Clock` 作為
/// 輸入參數的交易，除非是以不可變參考傳入。
public struct Clock has key {
    id: UID,
    /// clock 的時間戳記（timestamp），會在每次共識（consensus）完成一次
    /// schedule 時，由系統交易（system transaction）
    /// 自動設定，或在測試期間由 `sui::clock::increment_for_testing`
    /// 設定。
    timestamp_ms: u64,
}
```

在一般用途上，此模組公開了一個函式 —— `timestamp_ms`。它會回傳自 Unix Epoch 以來的當前時間（以毫秒為單位）。

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=clock

```

`Clock` 附帶了幾項實用的保證：在單一交易內，`timestamp_ms` 永遠回傳相同的值；而跨交易時，此值永遠不會減少。然而，由於時鐘只在共識提交時更新，彼此相近執行的交易可能會看到相同的時間戳記。

## 測試 (Testing) {#testing}

由於真正的 `Clock` 只能由系統更新，此模組提供了僅供測試使用的函式，用於建立時鐘、設定其數值，以及銷毀它：

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=test

```

## 總結 (Summary) {#summary}

- 當前的 epoch 及其開始時間戳記皆從[交易上下文 (transaction context)](./transaction-context)讀取 —— 免費且在每筆交易中皆可取得；一個 epoch 大約持續 24 小時。
- 位於保留地址 `0x6` 的 `Clock` 物件提供以毫秒為單位的時間，並在每次共識提交時更新；它只能以不可變方式存取。
- 在單一交易內，`Clock` 的數值永遠不會改變，而跨交易時它永遠不會減少。
- 在測試中，可使用 `create_for_testing`、`set_for_testing`、`increment_for_testing` 與 `destroy_for_testing` 來控制時鐘。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::clock](https://docs.sui.io/references/framework/sui/clock) 模組文件。
