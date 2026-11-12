---
description: 瞭解 sui::scratch 如何提供每筆交易的暫時性鍵值儲存區，以及定義索引鍵的模組如何控管對其項目的存取。
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

# 暫存區 (Scratchpad) {#scratchpad}

到目前為止介紹的所有儲存機制，其生命週期都比使用它的交易更長。
[物件](./../storage)、[動態欄位](./dynamic-fields)、
[動態集合](./dynamic-collections) 和 [地址餘額](./address-balances) 都會持續儲存在鏈上，直到明確變更或移除為止。不過，有時程式只需要在單筆交易中保留某個值。例如，它可能需要一個旗標來記錄某項動作是否已經執行、一個由多次呼叫共用的計數器，或一則由某個函式留給另一個函式的備註。_暫存區_（Sui Framework 的 `sui::scratch` 模組）為這些情況提供暫時性的鍵值儲存區。它只存在於單筆交易中，並在交易結束時丟棄。

## 鍵和值 (Keys and Values) {#keys-and-values}

每個暫存區項目都有一個鍵。鍵的型別和值會以與[動態欄位](./dynamic-fields)名稱相同的方式一併雜湊。不同於動態欄位，暫存區項目不會附屬於物件。所有項目都屬於目前交易範圍內的單一儲存區。程式會透過[交易情境](./transaction-context)存取此儲存區，而不是透過父項 `UID`。

鍵和值的要求反映了儲存區的暫時性：

- 鍵必須具備 `copy` 和 `drop`。這與動態欄位名稱類似，但動態欄位名稱還需要 `store`。暫存區鍵不需要 `store`，因為它永遠不會寫入儲存空間。
- 值必須具備 `drop`，因為交易結束時，任何剩餘項目都會被丟棄。值不需要 `store`，因為暫存區不是儲存空間。
- 讀取項目會回傳值的*副本*，因此 `read` 也需要 `copy`。若值無法複製，可以用 `remove` 取出；也可以透過下文介紹的借用風格巨集在原處存取。

## 存取控制 (Access Control) {#access-control}

暫存區的所有存取操作——讀取與寫入皆然——都由定義鍵型別的模組控制。控管方式是使用 `Permit<K>` 結構體；它是以 `internal::Permit<K>`（本書稍早介紹的[內部許可](./../move-basics/internal-permit)）換取而來：

```move
module sui::scratch;

/// `Permit<K>` 會控管所有以 K 型別值為鍵的項目之存取權。
/// 它由 `internal::Permit<K>` 核發，讓定義 `K` 的模組能控制所有暫存區項目的存取。
public struct Permit<phantom K: copy + drop>() has copy, drop;

/// 以具特權的 `internal::Permit<K>` 核發 `Permit<K>`，授予存取以 K 型別值為鍵的暫存區項目之權限。
public fun permit<K: copy + drop>(_: internal::Permit<K>): Permit<K> { /* ... */ }
```

每個暫存區操作都會取得一個對應其操作鍵型別的 `Permit<K>`。由於只有定義 `K` 的模組才能呼叫 `internal::permit<K>()`，因此每個模組都是暫存區中以自身型別為鍵之部分的唯一管理者。兩個模組不會發生鍵衝突，某個模組也無法讀取或修改另一個模組的項目。

> 不同於只有 `drop` 的 `internal::Permit`，暫存區的 `Permit` 也具備 `copy`：單一許可可在交易中授權任意次操作。它仍不具備 `store`，因此無法留到後續交易使用——這很適合一個屆時已不存在的儲存區。

## 使用暫存區 (Using the Scratchpad) {#using-the-scratchpad}

若要使用暫存區，請先定義鍵型別。任何具備 `copy + drop` 的型別都適用。常見的做法是為每個項目定義一個空的[位置結構體](./../move-basics/struct#positional-structs)：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=key

```

模組大多會存取自己的項目，因此 Framework 提供 `internal_*` 巨集捷徑，可在行內建立許可。這些捷徑是 `TxContext` 的方法，讓任何取得交易情境的函式都能存取暫存區：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=usage

```

基本操作各有兩種形式：一種是取得許可的形式（`scratch::add`，也可用 `ctx.scratch_add(permit, ...)`），另一種是供定義該鍵的模組使用的巨集形式（`ctx.scratch_internal_add!(...)`）：

- `add` - 新增一筆 `key`-`value` 項目。如果 `key` 已有項目，無論其值型別為何，都會中止。
- `read` - 回傳值的副本。如果項目不存在，或值型別不符，就會中止。
- `remove` - 移除項目並回傳值；中止條件與 `read` 相同。
- `exists` / `exists_with_type` - 檢查項目是否存在，可選擇檢查值型別。
- `read_opt` / `remove_opt` - `read` 和 `remove` 的版本；找不到項目時會回傳 [Option](./../move-basics/option)，而不會中止。
- `replace` - 移除現有值（若有），再於原處新增一個值，並回傳舊值。新舊值的型別可以不同。

會修改儲存區的函式——`add`、`remove`、`remove_opt` 和 `replace`——會取得 `&mut TxContext`。`read` 和檢查是否存在的操作則會取得 `&TxContext`。

## 原處存取 (In-Place Access) {#in-place-access}

`read` 會回傳副本。若要使用基本操作變更值，必須先移除再加回。*借用風格*巨集會替你處理這些步驟：它們會從儲存格取出值，將參考傳給指定函式，再於之後還原值。這不需要 `copy`，也不需要手動記錄狀態：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=get

```

這類巨集共有四個；若鍵沒有對應項目，它們都會略過函式：

- `get_do` / `get_mut_do` - 以不可變或可變參考呼叫函式。項目不存在時不執行任何操作。
- `get_fold` / `get_mut_fold` - 也會回傳結果。若項目不存在，就回傳函式產生的值，或指定的預設值。

這些巨集會在內部呼叫 `begin_borrow` 和 `end_borrow`。這些函式是公開的，但不建議直接使用。`begin_borrow` 會暫時移除值，並在其儲存格放入 `BorrowMarker`。此標記在該交易中是唯一的；`end_borrow` 會檢查標記，再還原值。

這種設計有兩個結果。第一，即使是唯讀存取，巨集也會取得 `&mut TxContext`。第二，指定的函式不得再次存取相同的鍵。函式執行期間，儲存格中只有標記，因此巢狀存取該鍵會中止，而不會讀取到尚未完整更新的項目。

## 每筆交易的狀態 (Per-Transaction State) {#per-transaction-state}

暫存區的實用之處在於，同一筆交易中的每次呼叫都會看到相同狀態。單一[交易](./../concepts/what-is-a-transaction)可以串接許多會呼叫多個函式的命令，而每個函式都能存取相同的暫存區。即使沒有任何單一函式能觀察到所有呼叫，程式仍可據此對整筆交易強制執行規則。例如，你可以限制某項動作在單筆交易中執行的次數，不受呼叫方式影響：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=counter

```

計數器的生命週期恰好是一筆交易。第一次呼叫找不到值，便從零開始；之後的呼叫會遞增計數器；交易結束時，最終值便會被丟棄。這樣就不必清理狀態，也不會留下過時狀態或產生儲存成本。若沒有暫存區，相同模式就需要專用物件並仔細重設。

標記可用來強制執行更嚴格的規則。在下例中，`one_time_action` 會先新增標記，再執行動作。同一筆交易中若再次呼叫，就會找到標記並中止。`continue_after_action` 函式也會檢查標記，因此只有在該動作恰好完成一次後才會執行：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=once

```

第一次檢查會防止第二次呼叫成功。第二次檢查則會在交易略過該動作時，拒絕呼叫 `continue_after_action`。兩者合起來可確保目前交易中的 `one_time_action` 恰好呼叫一次，且之後才會呼叫 `continue_after_action`。

> 和其他每筆交易的資源一樣，暫存區也受[協定限制](./../guides/building-against-limits)：撰寫本文時，單筆交易最多可容納 16,384 個項目，是交易中命令數量上限的 16 倍。

## 共用存取權 (Sharing Access) {#sharing-access}

由於 `Permit` 是一般值，定義該型別的模組不必把暫存區存取權限定在自身。它可以核發許可，讓其他程式碼存取自己的項目：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=permit

```

持有許可的一方會使用明確取得許可的函式——此處透過 `TxContext` 的方法別名呼叫：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=explicit

```

這符合一般的[內部許可](./../move-basics/internal-permit)模式。許可值承載了執行操作的權限，因此傳遞該值就會授予此權限。`copy` 能力讓共用許可可在交易中重複使用；缺少 `store` 則保證 `Permit` 不會超出該交易的生命週期。

若將授予函式設為 `public`，任何呼叫者都能取得許可，並對該鍵型別執行所有暫存區操作。當套件外的程式碼需要直接存取時，這種方式就很實用。

> 若只有同一套件中的模組需要存取，請優先使用範圍較窄的 `public(package)` 函式，而不是發出 `Permit`。定義該型別的模組可保留許可，只公開其他模組所需的操作。

例如，定義該型別的模組可以允許套件中的其他模組取代備註，而不授予它們對 `NoteKey` 執行所有操作的權限：

```move file=packages/samples/sources/programmability/scratchpad.move anchor=package_access

```

## 與燙手山芋比較 (Comparison with Hot Potato) {#comparison-with-hot-potato}

暫存區看起來可能和前一節的[燙手山芋 (Hot Potato)](./hot-potato-pattern) 模式類似。兩者都能讓同一筆交易中的多次呼叫共用狀態，也都不會在交易結束後留下任何內容。不過，它們提供的保證不同：

- 燙手山芋會透過函式簽章傳遞；暫存區不會改變函式簽章。函式只需要它原本就會取得的 `TxContext`。
- 燙手山芋會明確呈現交易的限制。持有該值的人看得見它，並且必須決定下一步要傳給誰。暫存區的行為對外不可見，因為函式簽章中沒有任何資訊能顯示這些呼叫彼此相關。
- 燙手山芋會明確要求呼叫最終的消耗函式。能力系統會強制執行此要求。暫存區項目沒有這種要求，並會在交易結束時消失。
- 燙手山芋可以包裝任何值，包括不得丟棄的資產。暫存區的值必須具備 `drop`，因此無法承載必須消耗的資源。

若流程*必須*完成，例如閃電貸款或交換，請使用燙手山芋。若要在原本無從共用資訊的多次呼叫之間，傳遞與交易相關的預定資訊，請使用暫存區。

## 總結 (Summary) {#summary}

- _暫存區_（`sui::scratch`）是範圍限定於單筆交易的暫時性鍵值儲存區。交易結束時，項目會被丟棄。
- 項目由鍵的型別和值識別，並以與動態欄位名稱相同的方式進行雜湊。鍵需要 `copy + drop`，值需要 `drop`，讀取則也需要 `copy`。
- 存取權由 `Permit<K>` 控管；它是以[內部許可](./../move-basics/internal-permit)核發而來，因此定義鍵型別的模組是其項目的唯一管理者。
- `internal_*` 巨集（例如 `ctx.scratch_internal_add!`）會在行內為定義該鍵的模組建立許可。
- 借用風格的 `get_do` / `get_mut_do` / `get_fold` / `get_mut_fold` 巨集會讓函式以參考方式暫時存取值，不必複製，也不必手動移除再新增。
- 交易中所有呼叫共用狀態，因此可以制定整筆交易適用的規則，例如限制某項動作在單筆交易中的執行次數。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::scratch](https://docs.sui.io/references/framework/sui/scratch) 模組文件。
- [內部許可](./../move-basics/internal-permit) - `Permit<K>` 背後的機制。
- [動態欄位](./dynamic-fields) - 暫存區項目的持續性對應機制。
