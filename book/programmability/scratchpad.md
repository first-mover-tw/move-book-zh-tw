---
description: 了解 sui::scratch 如何提供每筆交易暫存的鍵值儲存，以及定義鍵的模組如何控制其項目的存取。
title: 暫存區 (Scratchpad)
keywords:
  - Move
  - Sui
  - Move tutorial
  - scratchpad
  - scratch
questions:
  - What is the Scratchpad in Move?
  - How do I use sui::scratch in Move?
  - How do I keep per-transaction state on Sui?
  - What is In-Place Access in Move?
answer: The sui::scratch module provides an ephemeral key-value store shared by all calls in a transaction. Entries are discarded when the transaction ends, and the module that defines a key type controls access to its entries.
goal:
  description: Reader understands how to use sui::scratch for per-transaction state and how the module that defines a key type controls access to its entries
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

# 暫存板 (Scratchpad) {#scratchpad}

目前介紹的每一種儲存機制，其生命週期都比使用它的交易更長。
[物件](./../storage)、[動態欄位](./dynamic-fields)、
[動態集合](./dynamic-collections)和[地址餘額](./address-balances)都會持續存在於鏈上，直到被明確變更或移除為止。不過，有時程式只需要在單一交易中保留一個值。它可能需要一個旗標來記錄某項操作是否已發生、由多次呼叫共用的計數器，或一個函式留給另一個函式的備註。
_scratchpad_（Sui Framework 的 `sui::scratch` 模組）為這類情況提供暫時性的鍵值儲存區。它僅存在於一筆交易期間，並會在交易結束時捨棄。

## 鍵和值 (Keys and Values) {#keys-and-values}

每個暫存板項目都有一個鍵。鍵的型別和值會以與[動態欄位](./dynamic-fields)名稱相同的方式一同進行雜湊。與動態欄位不同，暫存板項目不會附加至物件。所有項目都屬於限定在目前交易範圍內的單一儲存區。程式會透過[交易情境](./transaction-context)而非父層 `UID` 存取此儲存區。

鍵和值的要求反映了此儲存區的暫時性特質：

- 鍵必須具有 `copy` 和 `drop`。這與動態欄位名稱相似，但動態欄位名稱還需要 `store`。暫存板鍵不需要 `store`，因為它永遠不會寫入儲存空間。
- 值必須具有 `drop`，因為交易結束時尚存的任何項目都會被捨棄。值不需要 `store`，因為暫存板不是儲存空間。
- 讀取項目會回傳值的*複本*，因此 `read` 也需要 `copy`。你可以使用 `remove` 取出無法複製的值，或使用[下方](#in-place-access)介紹的借用風格巨集就地存取它。

## 存取控制 (Access Control) {#access-control}

對暫存板的所有存取（包括讀取和寫入）皆由定義鍵型別的模組控制。其閘門是 `Permit<K>` 結構，透過交換 `internal::Permit<K>` 發出——亦即本書先前介紹的[內部許可](./../move-basics/internal-permit)：

```move
module sui::scratch;

/// `Permit<K>` 控制對所有以型別 `K` 的值作為鍵之項目的存取。
/// 它由 `internal::Permit<K>` 發出，讓定義 `K` 的模組能控制
/// 對暫存項目的所有存取。
public struct Permit<phantom K: copy + drop>() has copy, drop;

/// 從具有特權的 `internal::Permit<K>` 發出 `Permit<K>`，授予對
/// 以型別 `K` 的值作為鍵之暫存項目的存取權。
public fun permit<K: copy + drop>(_: internal::Permit<K>): Permit<K> { /* ... */ }
```

每個暫存板操作都會取得其操作鍵型別所對應的 `Permit<K>`。由於
`internal::permit<K>()` 只能從定義 `K` 的模組中呼叫，每個模組都是以其自身型別作為鍵之暫存板區域的唯一權限持有者。兩個模組不會衝突，而且一個模組無法讀取或修改另一個模組的項目。

> 與僅具有 `drop` 的 `internal::Permit` 不同，暫存板的 `Permit` 也具有 `copy`：單一許可可授權交易中的任意數量操作。它仍然沒有 `store`，因此無法保留至後續交易——這很適合不會在那時存在的儲存區。

## 使用暫存板 (Using the Scratchpad) {#using-the-scratchpad}

若要使用暫存板，請先定義鍵型別。任何具有 `copy + drop` 的型別皆可使用。常見作法是為每個項目建立空的[位置結構](./../move-basics/struct#positional-structs)：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=key

```

大多數時候，模組會存取自己的項目，因此框架提供了可內嵌建立許可的 `internal_*` 巨集捷徑。它們可作為 `TxContext` 的方法使用，讓任何取得交易情境的函式都能存取暫存板：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=usage

```

基本操作各自都有取得許可的形式（`scratch::add`，也可使用
`ctx.scratch_add(permit, ...)`），以及供定義模組使用的巨集形式
（`ctx.scratch_internal_add!(...)`）：

- `add` - 新增 `key`-`value` 項目。若 `key` 已存在項目，無論其值型別為何都會中止。
- `read` - 回傳值的複本。若項目不存在，或值型別不符，則會中止。
- `remove` - 移除項目並回傳值，且具有與 `read` 相同的中止條件。
- `exists` / `exists_with_type` - 檢查項目是否存在，可選擇是否檢查值型別。
- `read_opt` / `remove_opt` - `read` 和 `remove` 的版本，若項目缺失會回傳
  [Option](./../move-basics/option)，而非中止。
- `replace` - 移除既有值（若有），並以新值取代它，同時回傳舊值。舊值和新值的型別可以不同。

會修改儲存區的函式——`add`、`remove`、`remove_opt` 和 `replace`——會取得
`&mut TxContext`。`read` 和存在性操作會取得 `&TxContext`。

## 就地存取 (In-Place Access) {#in-place-access}

`read` 會回傳複本。若要使用基本操作變更值，你必須先移除它，再將它加回去。*借用風格*巨集會替你處理這些步驟。它們會將值從其槽位取出、將參考傳遞給提供的函式，然後再還原該值。這既不需要 `copy`，也不需要手動記帳：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=get

```

共有四個巨集；若鍵沒有項目，它們都會略過函式：

- `get_do` / `get_mut_do` - 使用值的不可變或可變參考呼叫函式。若項目不存在，則不執行任何操作。
- `get_fold` / `get_mut_fold` - 同時回傳結果。它們會回傳函式產生的任何結果，或在項目不存在時回傳提供的預設值。

這些巨集會在內部呼叫 `begin_borrow` 和 `end_borrow`。這些函式是公開的，但不預期直接使用。`begin_borrow` 會暫時移除值，並在其槽位放入 `BorrowMarker`。該標記對交易而言是唯一的，而 `end_borrow` 會在還原值之前檢查它。

此設計帶來兩項結果。首先，即使是唯讀存取，巨集也會取得 `&mut TxContext`。其次，提供的函式不得再次存取相同鍵。函式執行期間，槽位只包含標記，因此對該鍵的巢狀存取會中止，而非觀察到部分更新的項目。

## 每筆交易狀態 (Per-Transaction State) {#per-transaction-state}

暫存板很有用，因為交易中的每次呼叫都能看到相同狀態。單一[交易](./../concepts/what-is-a-transaction)可以串接許多命令，呼叫許多函式，而每個函式都能存取相同暫存板。即使沒有任何單一函式能觀察每次呼叫，這仍可讓程式針對整筆交易強制執行規則。例如，無論如何呼叫，你都可以限制一項操作在單筆交易中執行的次數：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=counter

```

計數器的生命週期恰好為一筆交易。第一次呼叫找不到任何項目並從零開始，後續呼叫會遞增計數器，而最終值會在交易結束時捨棄。這可避免清理作業、過時狀態和儲存成本。若沒有暫存板，相同模式會需要專用物件和謹慎的重設作業。

標記可強制執行更嚴格的規則。在下列範例中，`one_time_action` 會在執行操作前新增標記。同一交易中的第二次呼叫會找到標記並中止。`continue_after_action` 函式也會檢查標記，因此只有在操作恰好完成一次後才會執行：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=once

```

第一次檢查會防止第二次呼叫成功。第二次檢查會在交易略過操作時拒絕對
`continue_after_action` 的呼叫。兩者共同保證，在目前交易中，`continue_after_action` 會緊接於恰好一次對 `one_time_action` 的呼叫之後。

> 如同其他每筆交易資源，暫存板受到[協定限制](./../guides/building-against-limits)約束：在撰寫本文時，單一交易最多可持有 16,384 個項目——是交易中命令數量上限的 16 倍。

## 共用存取權 (Sharing Access) {#sharing-access}

由於 `Permit` 是一般值，定義模組不必將暫存板存取權保留給自己。它可以發出許可，並授予其他程式碼存取其項目的權限：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=permit

```

許可持有者會使用明確取得許可的函式——此處透過它們的 `TxContext` 方法別名：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=explicit

```

這遵循一般的[內部許可](./../move-basics/internal-permit)模式。許可值攜帶操作權限，因此傳遞該值便會授予該權限。`copy` 能力讓共用許可能在交易中重複使用，而缺少 `store` 則保證 `Permit` 無法超出其生命週期。

將授權函式設為 `public` 可讓任何呼叫者取得許可，並對該鍵型別使用所有暫存板操作。當套件外部的程式碼需要直接存取時，這很有用。

> 若只有同一套件中的模組需要存取，請優先使用範圍較窄的 `public(package)` 函式，而非發出 `Permit`。定義模組會保留許可，並且只公開其他模組所需的操作。

例如，定義模組可以允許其套件中的其他模組取代備註，而不授予它們對 `NoteKey` 執行所有操作的權限：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=package_access

```

## 與 Hot Potato 的比較 (Comparison with Hot Potato) {#comparison-with-hot-potato}

暫存板看似與前一節的 [Hot Potato](./hot-potato-pattern) 模式相似。兩者都讓單筆交易內的多次呼叫共用狀態，並且都不會在交易結束後留下任何內容。不過，它們提供不同的保證：

- Hot potato 會透過函式簽章傳遞；暫存板不會變更函式簽章。函式只需要它原本就取得的 `TxContext`。
- Hot potato 會以可見方式約束交易。持有該值的人能看見它，並且必須決定下一步將它交給哪裡。以暫存板為基礎的行為從外部不可見，因為簽章中沒有任何內容揭露這些呼叫彼此相連。
- Hot potato 會建立明確義務，必須呼叫最終的消耗函式。能力系統會強制執行此義務。暫存板項目不會建立此類義務，並會在交易結束時消失。
- Hot potato 可以包裝任何值，包括不得捨棄的資產。暫存板值需要 `drop`，因此暫存板無法攜帶必須被消耗的資源。

對於*必須*完成的流程，例如閃電貸款或交換，請使用 hot potato。對於在原本無法共用資訊的呼叫之間，攜帶交易預先定義資訊的情況，請使用暫存板。

## 總結 (Summary) {#summary}

- _scratchpad_——`sui::scratch`——是限定於單一交易範圍的暫時性鍵值儲存區。項目會在交易結束時捨棄。
- 項目由其鍵的型別和值識別，並像動態欄位名稱一樣進行雜湊。鍵需要 `copy + drop`，值需要 `drop`，而讀取還需要 `copy`。
- 存取受到由[內部許可](./../move-basics/internal-permit)發出的 `Permit<K>` 控制，讓定義鍵型別的模組成為其項目的唯一權限持有者。
- `internal_*` 巨集——可作為 `ctx.scratch_internal_add!` 等形式使用——會為定義模組內嵌建立許可。
- 借用風格的 `get_do` / `get_mut_do` / `get_fold` / `get_mut_fold` 巨集會透過參考授予函式對值的暫時存取權，無須複製或手動移除後再新增。
- 交易中所有呼叫之間的共用狀態，可實現涵蓋整筆交易的規則，例如限制每筆交易中操作可執行的次數。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::scratch](https://docs.sui.io/references/framework/sui/scratch) 模組文件。
- [Internal Permit](./../move-basics/internal-permit) - `Permit<K>` 背後的機制。
- [Dynamic Fields](./dynamic-fields) - 暫存板項目的持久化對應機制。
