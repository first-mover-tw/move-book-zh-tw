---
description: Sui 中的物件展示 (Object Display)：使用 Display Registry 為你的物件定義中繼資料範本 (metadata template)，並將 Display 從 V1 遷移到 V2。
---

# 物件展示 (Object Display) {#object-display}

Sui 上的物件在結構與行為上都是明確的，可以用容易理解的方式展示。然而，為了支援客戶端更豐富的中繼資料，有一套標準且高效的方式來「描述」它們給客戶端——`Display` 物件，註冊於 [Sui Framework](./sui-framework) 定義的系統 _Display Registry_ 中。

## 背景 (Background) {#background}

過去曾有不同的嘗試，希望對物件的標準結構達成共識，以便能在使用者介面中展示。其中一種做法是在物件結構中定義特定欄位，當這些欄位存在時就會用於 UI。這種做法不夠靈活，要求開發者在每個物件中都定義相同的欄位，而且有時這些欄位對該物件來說並不合理。

```move file=packages/samples/sources/programmability/display.move anchor=background

```

如果其中任何欄位包含靜態資料，這些資料就會在每個物件中重複出現。而且，由於 Move 沒有介面（interface），如果不「手動」檢查物件的型別，就無法得知某個物件是否具有特定欄位，這使得客戶端的擷取工作變得更加複雜。

## 物件展示 (Object Display) {#object-display-1}

為了解決這些問題，Sui 引進了一套標準方式來描述物件以供展示。展示中繼資料不是定義在物件結構中的欄位，而是儲存在一個獨立的物件——`Display<T>`——中，與型別 `T` 相關聯。如此一來，展示中繼資料不會重複，也易於擴充與維護。

Sui Display 的另一項重要特性，是能夠定義範本（template）並在範本中使用物件欄位。這不僅讓展示更加靈活，也讓開發者不必在每個物件中都定義相同名稱與型別的欄位。

> Object Display 由 [Sui Full Node](https://docs.sui.io/operators/full-node/sui-full-node) 原生支援，只要某個物件型別有關聯的 Display，客戶端就能為任何物件擷取展示中繼資料。

## 展示註冊表 (Display Registry) {#display-registry}

每個型別 `T` 恰好對應一個 `Display<T>`，且它位於一個可預測的地址。這兩項特性都來自 _Display Registry_——一個位於保留地址 `0xd` 的系統共享物件（參見[保留地址](./../appendix/reserved-addresses)）。當建立一個展示時，其物件 ID 是從註冊表的 `UID` 與型別 `T` 一起[推導](https://docs.sui.io/references/framework/sui_sui/derived_object)而來。因此，任何人——包括 RPC 與其他客戶端——都能離線計算出 `Display<T>` 的 ID 並直接擷取，而不需要掃描事件或查詢歷史資料。

```move
module sui::display_registry;

/// 顯示的根，用來讓地址得以衍生。
/// 該地址由系統於 `0xd` 產生。
public struct DisplayRegistry has key { id: UID }

/// 保存型別 `T` 的顯示值。
public struct Display<phantom T> has key {
    id: UID,
    /// 給定顯示物件的所有 (key,value) 項目。
    fields: VecMap<String, String>,
    /// 管理此顯示的 `DisplayCap` 之 ID。對於尚未領取 capability 的
    /// 已遷移 V1 顯示，則為 `None`。
    cap_id: Option<ID>,
}

/// 用來管理該顯示的 capability 物件。
public struct DisplayCap<phantom T> has key, store { id: UID }
```

`Display<T>` 物件本身是*共享的*，其權限則由另一個獨立的自有物件——`DisplayCap<T>` [能力（capability）](./capability)——來代表。持有該能力的人可以隨時 `set`（設定）、`unset`（取消設定）或 `clear`（清除）展示欄位，且變更會全域套用，不需要更新每一個物件。該能力可以轉移給其他帳戶，或整合進具有自訂中繼資料管理功能的應用程式中。

## 建立展示 (Creating a Display) {#creating-a-display}

新的 `Display` 可以透過以下兩個函式之一來建立，兩者都接受一個對 `DisplayRegistry` 的可變參考，並回傳 `Display<T>` 以及其對應的 `DisplayCap<T>`：

- `display_registry::new<T>` ——接受一個[內部許可 (Internal Permit)](./../move-basics/internal-permit)，因此只能從定義 `T` 的模組中呼叫；
- `display_registry::new_with_publisher<T>` ——接受 [Publisher](./publisher) 物件，適用於在定義模組之外建立展示的情況。

由於註冊表是一個共享物件，無法在[模組初始化函式 (module initializer)](./module-initializer) 中存取——展示是在套件發佈後，透過一個獨立的一次性呼叫來建立的：

```move file=packages/samples/sources/programmability/display.move anchor=hero

```

`set` 呼叫定義了範本欄位，`share` 則透過共享 `Display` 物件來完成建立；接著 `DisplayCap` 會被轉移給發佈者，讓其之後可以用來更新欄位。請注意，這個函式被定義為 `entry` 而非 `public`：一次性的設定函式最好不要放進套件的公開 API，這樣未來升級時就能移除它——[升級相容性規則](https://docs.sui.io/develop/publish-upgrade-packages/upgrade)會凍結 `public` 函式簽章，但不會凍結 `entry` 函式的簽章。

## 標準欄位 (Standard Fields) {#standard-fields}

最廣泛支援的欄位有：

- `name` ——物件的名稱。使用者檢視物件時會顯示此名稱。
- `description` ——物件的描述。使用者檢視物件時會顯示此描述。
- `link` ——應用程式中用來連結到該物件的連結。
- `image_url` ——物件圖片的 URL 或 blob。
- `thumbnail_url` ——較小圖片的 URL，用於錢包、瀏覽器與其他產品中作為預覽。
- `project_url` ——與該物件或創作者相關聯的網站連結。
- `creator` ——表示物件創作者的字串。

> 請參閱 [Sui 官方文件](https://docs.sui.io/develop/objects/display) 以取得最新支援欄位清單。

雖然有一套標準欄位集合，但 Display 物件並不強制要求使用這些欄位。開發者可以定義任何需要的欄位，客戶端也可以依需求使用這些欄位。某些應用程式可能需要額外欄位而省略其他欄位，Display 具備足夠的靈活性來支援這些情況。

## 範本語法 (Template Syntax) {#template-syntax}

Display 中的每個值都是一個*格式字串 (format string)*——由字面文字與以 `{` 與 `}` 分隔的運算式組成。最簡單的運算式是欄位路徑：`{path}` 會被替換為該路徑對應欄位的值，其中路徑是以點分隔的欄位名稱清單，從被展示的物件開始。若要輸出字面上的大括號，將其重複一次即可——`{{` 會變成 `{`。

```move file=packages/samples/sources/programmability/display.move anchor=nested

```

上述 `LittlePony` 型別的 Display 可以定義如下：

```json
{
  "name": "Just a pony",
  "image_url": "{image_url}",
  "description": "{metadata.description}"
}
```

欄位路徑只是最基本的運算式。運算式的完整形式有三個部分——一條用來導覽資料的*鏈 (chain)*、以 `|` 分隔的可選*後備值 (fallbacks)*清單，以及以 `:` 開頭、控制值如何呈現的可選*轉換 (transform)*：

```text
{ chain | fallback | ... : transform }
```

以下各節將介紹這套語法中最常用到的部分。完整文法——包含字面值、結構與列舉值、衍生物件存取，以及完整的轉換清單——請參見
[Object Display Syntax](https://docs.sui.io/references/object-display-syntax) 參考文件。

### 向量與映射索引 (Vector and Map Indexing) {#vector-and-map-indexing}

鏈可以透過方括號對 `vector` 或 `VecMap` 進行索引。數值索引一律需要帶型別後綴——例如 `0u64` 而非 `0`——而且也可以用另一個欄位的值作為索引：

```text
{items[0u64]}           first element of the `items` vector
{items[idx]}            use the `idx` field's value as the index
{scores[6u32]}          look up the key `6u32` in a VecMap, returns its value
```

### 動態欄位存取 (Dynamic Field Access) {#dynamic-field-access}

範本可以超越物件本身的欄位，從儲存中載入[動態欄位 (dynamic fields)](./dynamic-fields)。`->` 運算子用來載入動態欄位，`=>` 用來載入[動態物件欄位 (dynamic object field)](./dynamic-object-fields)，鍵值則放在方括號中：

```text
{parent->['color']}     dynamic field with the string key 'color'
{parent->['color'].x}   read field `x` on the loaded value
{parent=>['hat']}       dynamic object field (the value is a full object)
```

由於每次載入都是從儲存中讀取，因此會受到預算限制：一個範本預設最多可執行 8 次物件載入，其中 `->` 花費 1 次，`=>` 花費 2 次。

### 轉換 (Transforms) {#transforms}

預設情況下，一個值會被呈現為人類可讀的字串。`:` 之後的轉換可以改變這一點——這對於非純文字的值（例如位元組向量或時間戳記）很有用：

| 轉換                | 效果                                                   |
| ------------------- | ------------------------------------------------------ |
| `str`（_預設_）     | 人類可讀的字串；`String` 與 `vector<u8>` 使用 UTF-8。  |
| `hex`               | 小寫、補零的十六進位。                                 |
| `base64`            | Base64 編碼的位元組；支援 `url` 與 `nopad` 修飾詞。    |
| `bcs`               | BCS 序列化後的值，再進行 Base64 編碼——適用於聚合型別。 |
| `json`              | 結構化的 JSON 值；僅在其為整個格式字串時使用。         |
| `timestamp`（`ts`） | 以 Unix 毫秒讀取的數值，格式化為 ISO 8601。            |
| `url`               | 類似 `str`，但會對 URL 保留字元進行百分比編碼。        |

```text
{amount:hex}                    render `amount` as hex
{created_at:ts}                 "2023-04-12T17:00:00Z"
{metadata:json}                 emit the whole struct as JSON
```

### 後備值 (Fallbacks) {#fallbacks}

如果一條鏈求值結果為 null——例如缺少的欄位、超出範圍的索引，或是 `None` 的 [Option](./../move-basics/option)——就會嘗試 `|` 之後的下一條鏈。以單引號括起的字串字面值可以作為方便的預設值：

```text
{display_name | name | 'Anonymous'}
```

如果所有備選項都是 null，整個格式字串就會求值為 null，該欄位就會從結果中省略。

## 從 V1 遷移至 V2 (Migrating from V1 to V2) {#migrating-from-v1-to-v2}

本頁描述的、以註冊表為基礎的 Display，是這套標準的第二版——_Display V2_。最初的版本——V1，實作於 `sui::display` 模組中——早於註冊表出現：V1 的 `Display<T>` 物件是自有的而非共享的，只能透過 `Publisher` 物件建立，且是透過事件被發現的。同一個型別可以存在任意數量的 V1 展示，而全節點會使用最近更新的那一個。V2 以從註冊表推導取代了基於事件的發現機制，並將「任意數量的展示」縮減為每個型別恰好一個。

現有的 V1 展示已由系統遷移自動轉換為 V2：對於每個擁有 V1 展示的型別，都已存在一個具有相同欄位、且 `cap_id` 設為 `none` 的共享 `Display<T>`。要管理這樣的展示，創作者可以透過以下兩種方式之一來取得其 `DisplayCap`：

- `claim` ——以舊版 V1 `Display` 物件作為對該型別擁有權限的證明來消耗它，並在此過程中將其銷毀；
- `claim_with_publisher` ——改用 [Publisher](./publisher) 物件；之後遺留的 V1 物件可以用 `delete_legacy` 銷毀。

```move file=packages/samples/sources/programmability/display.move anchor=migrate

```

對於在系統遷移完成之後才建立的 V1 展示，`display_registry::migrate_v1_to_v2` 函式可以直接執行遷移：它會建立 V2 `Display`，複製舊物件的欄位，銷毀該舊物件，並回傳新的展示連同其能力物件。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 官方文件中的[物件展示 (Object Display)](https://docs.sui.io/develop/objects/display)
- [Object Display Syntax](https://docs.sui.io/references/object-display-syntax) ——完整的範本語言參考
- [Publisher](./publisher) ——創作者的表示方式
- [Internal Permit](./../move-basics/internal-permit) ——用於建立展示的授權機制
