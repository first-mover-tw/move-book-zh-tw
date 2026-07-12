---
title: 模組擴展 (Module Extensions) | Reference
description:
  Move 模組擴充參考手冊 (Move module extensions reference)：為既有模組新增僅限測試或模式限定的宣告，用於外部套件
  (package)。
---

# 模組擴充 (Module Extensions)

**模組擴充 (Module Extensions)** 允許套件向現有模組新增宣告，**就像**這些宣告是定義在該模組內部一樣。擴充是透過模式屬性（mode attribute）選擇性加入的，且永遠不會修改或移除現有項目。

### 範例 (Example)

想像一下，你有一個現成的模組想在你的套件中進行測試，但它缺少一些內部的存取器（accessors）或測試操作，這導致你無法對其編寫完整的測試。作為一個簡單的例子，考慮一個定義為庫的簡單計數器模組：

```move
module counter::counter {
    public struct Counter has drop { value: u64 }

    public fun new(): Counter { Counter { value: 0 } }

    public fun incr(mut c: Counter): Counter {
        c.value = c.value + 1;
        c
    }

    public fun destroy(c: Counter): u64 {
        let Counter { value } = c;
        value
    }
}
```

你可能在自己的套件中使用此模組來實作步數計數器：

```move
module app::step_counter {
    use counter::counter::{Counter, new, incr, destroy};
    enum Step { Once, Many(u64) }

    public fun step(c: Counter, s: Step): Counter {
        match s {
            Step::Once => incr(c),
            Step::Many(n) => {
                let mut c = c;
                let mut i = 0;
                while (i < n) {
                    c = incr(c);
                    i = i + 1;
                }
                c
            }
        }
    }
}
```

假設你想為這個計數器行為撰寫額外的測試，包括確保不變數（invariants）以及能夠在不消耗計數器的情況下查看當前值。擴充允許你在自己的套件中將此行為新增為測試定義，而無需分叉（forking）或更新下游依賴。

```move
#[test_only]
extend module counter::counter {
    /// 在不消耗計數器的情況下查看當前值。
    public fun peek(c: &Counter): u64 { c.value }
}

#[test_only]
extend module app::step_counter {
    use counter::counter::{Counter, new, incr, peek};

    // 局部測試輔助函式，保持斷言整潔。
    fun expect_value(c: &Counter, want: u64) { assert!(c.peek() == want, 0); }

    /// 等效性：Once == Many(1)。
    #[test]
    fun once_equals_many1() {
        let c1a = step(new(), Step::Once);
        let c1b = step(new(), Step::Many(1));
        expect_value(&c1a, 1);
        expect_value(&c1b, 1);
    }
}
```

在此用法中，你擴充了 `counter::counter` 模組（以增加輔助工具和測試）和 `app::step_counter` 模組（以增加步數邏輯的測試）。所有這些程式碼都存在於你的套件中，並且只會影響測試建置。可發佈的程式碼則保持不變。

> **注意**：擴充只能新增新項目；它們不能修改或移除現有項目。此外，只有在根套件中定義的擴充才會被套用（依賴項中的擴充不會被套用）。

## 擴充語法 (Extension Syntax)

擴充是透過在 `module` 關鍵字前加上 `extend` 關鍵字來定義的：

```move
#[mode(name1, name2, ...)]      // 或 #[test_only]
extend module <address>::<identifier> {
    (<use> | <type> | <function> | <constant>)*
}
```

擴充也允許用於單檔案模組形式：

```move
#[mode(test)]
extend module p<address>::<identifier>;

(<use> | <type> | <function> | <constant>)*
```

在上述兩種情況下：

- 擴充必須定義模式屬性。
- `<address>::<identifier>` 是套件和模組名稱。
- 模組元素與標準 [模組](modules) 相同。
- 擴充塊在啟用的模式下編譯到目標模組中。
- `<address>::<identifier>` 必須解析為當前建置中已存在的模組。

## 套用擴充 (Applying Extensions)

令 `M` 為當前建置中的一個模組。令 `E1, E2, ... En` 為定位到 `M` 的所有擴充，且滿足：

- `Ei` 定義在當前建置的根套件中（其他的會被忽略）。
- `Ei` 定義的目標是 `M`。
- `Ei` 具有作用中的模式屬性。

在展開過程中，`M` 的實際內容將轉換為：

```
module M {
    ... M 的原始內容 ...
    ... E1 的內容 ...
    ... E2 的內容 ...
    ...
    ... En 的內容 ...
}
```

名稱解析、能見度、版本規則（edition rules）、型別檢查等，都套用於合併後的整體模組。這意味著擴充中的每個宣告都被視為直接寫入目標模組中，並受相同的能見度、版本特性、重複定義錯誤、名稱衝突等約束。

這意味著擴充不得修改或覆蓋現有的宣告，也不得遮蔽現有的 `use` 定義等。可以新增新的 `use` 定義，但它們的編譯仍受可決定的 (decidable) 依賴排序約束，如 [`use`](uses) 章節所述。

> **提示**：擴充程式碼受與目標模組相同的版本特性約束。如果目標模組處於較舊的版本，擴充程式碼也必須與該版本相容。
