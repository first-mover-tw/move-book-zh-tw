# 事件 (Events)

事件是用於通知鏈外監聽器關於鏈上事件的一種方式。它們用於發送有關交易的附加資訊，這些資訊不存儲在鏈上，因此無法在鏈上存取。事件由位於 [Sui 框架](./sui-framework) 中的 `sui::event` 模組發送。

> 任何具有 [copy](./../move-basics/copy-ability) 和 [drop](./../move-basics/drop-ability) 能力的自定義類型都可以作為事件發送。Sui 校驗器 (Verifier) 要求該類型必須是模組內部的。

```move
module sui::event;

/// 發送一個自定義 Move 事件，將資料傳送到鏈外。
/// 用於建立自定義索引並以最適合特定應用程式的方式追蹤鏈上活動。
/// 類型 `T` 是索引事件的主要方式，可以包含 phantom 參數，
/// 例如 `emit(MyEvent<phantom T>)`。
public native fun emit<T: copy + drop>(event: T);
```

## 發送事件 (Emitting Events)

事件使用 `sui::event` 模組中的 `emit` 函式發送。該函式接收一個參數 — 要發送的事件。事件資料按值傳遞。

```move file=packages/samples/sources/programmability/events.move anchor=emit

```

Sui 校驗器要求傳遞給 `emit` 函式的類型必須是 **模組內部的 (internal to the module)**。因此，發送來自另一個模組的類型將導致編譯錯誤。原始類型雖然符合 `copy` 和 `drop` 的要求，但不允許作為事件發送。

## 事件結構 (Event Structure)

事件是交易結果的一部分，存儲在 **交易效果 (transaction effects)** 中。因此，它們原生具有 `sender` 欄位，即發送交易的地址。因此，無需在事件中添加「sender」欄位。同樣地，事件元資料包含時間戳。但請注意，時間戳是相對於節點的，在不同節點之間可能會略有不同。

<!-- ## Reliability -->
