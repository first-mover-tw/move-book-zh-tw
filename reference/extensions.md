---
title: 模組擴展 (Module Extensions) | Reference
description:
  Move 模組擴充參考手冊 (Move module extensions reference)：為既有模組新增僅限測試或模式限定的宣告，用於外部套件
  (package)。
---

# 模組擴展 (Module Extensions)

**模組擴展** 讓一個套件可以向現有模組新增宣告，**就像** 它們是在該模組內部定義的一樣。擴展是可選的（通過模式屬性），並且永遠不會修改或移除現有項目。

### 例子

想像您有一個現成的模組想在您的套件中測試，但它缺少一些內部訪問器或測試操作，使您無法對其進行完整測試。作為一個簡單示例，考慮一個定義為庫的簡單計數器模組：

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

您可能在自己的套件中使用此模組來實現步驟計數器：

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

假設您想為此計數器行為編寫額外的測試，包括確保不變量和無需消耗計數器即可查看當前值的能力。擴展允許您在自己的套件中將此行為作為測試宣告添加，而無需分叉和更新下游依賴。

```move
#[test_only]
extend module counter::counter {
    /// 在不消耗計數器的情況下查看當前值。
    public fun peek(c: &Counter): u64 { c.value }
}

#[test_only]
extend module app::step_counter {
    use counter::counter::{Counter, new, incr, peek};

    // 本地測試輔助函式以保持斷言整潔。
    fun expect_value(c: &Counter, want: u64) { assert!(c.peek() == want, 0); }

    /// 等價性：Once == Many(1)。
    #[test]
    fun once_equals_many1() {
        let c1a = step(new(), Step::Once);
        let c1b = step(new(), Step::Many(1));
        expect_value(&c1a, 1);
        expect_value(&c1b, 1);
    }
}
```

在此用法中，您擴展了 `counter::counter` 模組（以添加輔助程式和測試）和 `app::step_counter` 模組（以為步驟邏輯添加測試）。所有此程式碼都位於您的套件中，並且它僅影響測試構建。可發佈的程式碼保持不變。

> **注意**：擴展只能添加新項目；它們無法修改或移除現有項目。此外，只應用根套件中定義的擴展（依賴中的擴展不應用）。

## 擴展語法

擴展通過在 `module` 關鍵字前添加 `extend` 關鍵字來定義：

```move
#[mode(name1, name2, ...)]      // 或 #[test_only]
extend module <address>::<identifier> {
    (<use> | <type> | <function> | <constant>)*
}
```

擴展對於單檔案模組形式是允許的：

```move
#[mode(test)]
extend module p<address>::<identifier>;

(<use> | <type> | <function> | <constant>)*
```

在兩種情況下：

- 擴展必須定義一個模式屬性。
- `<address>::<identifier>` 是套件和模組名稱。
- 模組元素與標準[模組](modules)中的相同。
- 擴展區塊在啟用的模式下被編譯到目標模組中。
- `<address>::<identifier>` 必須解析為當前構建中的現有模組。

## 應用擴展

設 `M` 為當前構建中的一個模組。設 `E1, E2, ... En` 為所有針對 `M` 的擴展，使得：

- `Ei` 在當前構建的根套件中定義（其他的被忽略）。
- `Ei` 針對 `M`
- `Ei` 具有活躍的模式屬性。

在擴展期間，`M` 的有效內容被轉換為：

```
module M {
    ... M 的原始內容 ...
    ... E1 的內容 ...
    ... E2 的內容 ...
    ...
    ... En 的內容 ...
}
```

名稱解析、可見性、版本規則、型別檢查等應用於結果模組的整體。這意味著擴展中的每個宣告都被視為直接在目標模組中編寫的，並受相同的可見性、版本功能、重複定義錯誤、名稱衝突等的約束。

這意味著擴展不能修改或覆蓋現有宣告，也不能遮蔽現有 `use` 宣告等。可以添加新的 use 宣告，但它們的編譯仍然受限於可決定的依賴排序，如 [`use`](uses) 部分所述。

> **提示**：擴展程式碼受到與目標模組相同的版本功能約束。如果目標模組使用較舊的版本，擴展程式碼也必須與該版本兼容。
