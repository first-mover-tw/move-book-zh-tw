# Epoch 與時間 (Epoch and Time)

Sui 有兩種存取目前時間的方式：`Epoch` 和 `Time`。前者代表系統中的運作週期，大約每 24 小時更改一次；後者代表自 Unix Epoch 以來的目前時間（毫秒）。兩者都可以在程式中自由存取。

## Epoch (週期)

Epoch 用於將系統劃分為不同的運作週期。在一個 epoch 期間，驗證者集 (validator set) 是固定的；然而，在 epoch 邊界，驗證者集可以被更改。Epoch 在共識演算法中起著至關重要的角色，用於確定目前的驗證者集。它們也用作質押 (staking) 機制中的衡量基準。

可以從 [交易上下文](./transaction-context) 中讀取 Epoch：

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=epoch

```

也可以獲取 epoch 開始時的 unix 時間戳：

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=epoch_start

```

通常，epoch 用於質押和系統操作，但在自定義場景中，它們可以用於模擬 24 小時週期。如果應用程式依賴於質押邏輯或需要了解目前的驗證者集，則它們至關重要。

## 時間 (Time)

為了獲得更精確的時間測量，Sui 提供了 `Clock` 物件。它是一個系統物件，由系統在檢查點 (checkpoint) 期間更新，存儲自 Unix Epoch 以來的目前時間（毫秒）。`Clock` 物件定義在 `sui::clock` 模組中，擁有保留地址 `0x6`。

`Clock` 是一個共享物件 (shared object)，但嘗試以可變方式 (mutably) 存取它的交易將會失敗。此限制允許對 `Clock` 物件進行並行存取，這對於保持系統效能非常重要。

```move
module sui::clock;

/// 單例共享物件，向 Move 呼叫公開時間。
/// 此物件位於地址 0x6，且只能由進入函式 (entry functions) 讀取（透過不可變參考存取）。
/// 
/// 嘗試透過可變參考或值接收 `Clock` 的進入函式將無法通過校驗，
/// 誠實的驗證者將不會簽署或執行將 `Clock` 作為輸入參數使用的交易，除非它是透過不可變參考傳遞的。
public struct Clock has key {
    id: UID,
    /// 時鐘的時間戳，每當共識提交計劃時由系統交易自動設置，
    /// 或者在測試期間透過 `sui::clock::increment_for_testing` 設置。
    timestamp_ms: u64,
}
```

`Clock` 模組中僅提供一個公開函式：`timestamp_ms`。它傳回自 Unix Epoch 以來的目前時間（毫秒）。

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=clock

```

## 測試 (Testing)

`Clock` 模組提供了多種用於測試的方法。

```move file=packages/samples/sources/programmability/epoch-and-time.move anchor=test

```
