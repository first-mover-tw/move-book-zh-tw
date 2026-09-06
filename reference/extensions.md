---
title: 模組擴充功能 (Module Extensions) | 參考手冊
description: Move 模組擴充功能 (Move module extensions) 參考手冊：從外部套件 (external packages) 向現有模組新增僅限測試 (test-only) 或受模式控管 (mode-gated) 的宣告 (declarations)。
keywords:
  - Move
  - Sui
  - Move reference
  - module
  - extensions
  - reference
  - modules
questions:
  - How does Module Extensions work in Move?
  - What is the syntax for Module Extensions in Move?
  - What is Extension Syntax in Move?
  - What is Applying Extensions in Move?
answer: 'Move module extensions reference: add test-only or mode-gated declarations to existing modules from external packages.'
goal:
  description: 'Reader understands move module extensions reference: add test-only or mode-gated declarations to existing modules from external packages'
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

# 模組擴充功能 (Module Extensions) {#module-extensions}

**模組擴充功能**可讓套件將新的宣告加入既有模組，**如同**它們是在該模組內定義。擴充功能透過模式屬性選擇啟用，且絕不會修改或移除既有項目。

### 範例 (Example) {#example}

假設你有一個現成的模組，想在套件中對它進行測試，但它缺少一些內部存取子或測試操作，無法讓你為其撰寫完整測試。作為簡單範例，請考慮一個定義為函式庫的計數器模組：

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

你可以在自己的套件中使用此模組來實作步數計數器：

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

假設你想為此計數器行為撰寫額外測試，包括確保不變數，以及能夠在不消耗計數器的情況下查看目前值。擴充功能可讓你在自己的套件中，將此行為作為測試定義加入，而無須分支並更新下游依賴項。

```move
#[test_only]
extend module counter::counter {
    /// 查看目前的值，而不消耗計數器。
    public fun peek(c: &Counter): u64 { c.value }
}

#[test_only]
extend module app::step_counter {
    use counter::counter::{Counter, new, incr, peek};

    // 區域測試輔助函式，讓斷言保持簡潔。
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

在此用法中，你會擴充 `counter::counter` 模組（以加入輔助函式與測試）及 `app::step_counter` 模組（以加入步數邏輯的測試）。所有這些程式碼都位於你的套件中，且只會影響測試建置。可發布的程式碼保持不變。

> **注意**：擴充功能只能新增項目；無法修改或移除既有項目。另
> 外，只有在根套件中定義的擴充功能會套用（依賴項中的擴充功能不會
> 套用）。

## 擴充功能語法 (Extension Syntax) {#extension-syntax}

擴充功能的定義方式是在 `module` 關鍵字前加入 `extend` 關鍵字：

```move
#[mode(name1, name2, ...)]      // 或 #[test_only]
extend module <address>::<identifier> {
    (<use> | <type> | <function> | <constant>)*
}
```

擴充功能可用於單一文件的模組形式：

```move
#[mode(test)]
extend module p<address>::<identifier>;

(<use> | <type> | <function> | <constant>)*
```

在這兩種情況中：

- 擴充功能必須定義模式屬性。
- `<address>::<identifier>` 是套件與模組名稱。
- 模組元素與標準[模組](modules)相同。
- 擴充功能區塊會在已啟用的模式下編譯至目標模組。
- `<address>::<identifier>` 必須解析為目前建置中既有的模組。

## 套用擴充功能 (Applying Extensions) {#applying-extensions}

令 `M` 為目前建置中的模組。令 `E1, E2, ... En` 為所有以 `M` 為目標的擴充功能，且：

- `Ei` 定義於目前建置的根套件中（其他會被忽略）。
- `Ei` 以 `M` 為目標。
- `Ei` 具有作用中的模式屬性。

在展開期間，`M` 的有效內容會轉換為：

```
module M {
    ... M 的原始內容 ...
    ... E1 的內容 ...
    ... E2 的內容 ...
    ...
    ... En 的內容 ...
}
```

名稱解析、可見性、版本規則、型別檢查等，皆會套用至整個產生的模組。這表示擴充功能中的每個宣告，都會被視為直接寫在目標模組中，並受到相同的可見性、版本功能、重複定義錯誤、名稱衝突等規則約束。

這表示擴充功能不得修改或覆寫既有宣告，也不得遮蔽既有的 `use` 定義等。可以新增新的 use 定義，但其編譯仍須遵守可判定的依賴項排序，如 [`use`](uses) 章節所述。

> **提示**：擴充功能程式碼受到與目標模組相同的版本功能約束。若目標模組使用較舊版本，擴充功能程式碼也必須與該版本相容。
