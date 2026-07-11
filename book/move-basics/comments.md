---
description:
  如何在 Move 中使用行內註解 (line comments)、區塊註解 (block comments) 與文件註解 (doc comments)
  來進行文件撰寫與程式碼註解。
---

# 註解 (Comments) {#comments}

註解是一種為程式碼加上筆記或說明文件的方式。編譯器會忽略它們，不會產生任何 Move bytecode。你可以用註解來解釋程式碼的作用、給自己或其他開發者留下筆記、暫時移除一部分程式碼，或是產生文件。Move 中有三種註解：行註解、區塊註解，以及文件註解。

## 行註解 (Line Comment) {#line-comment}

你可以用雙斜線 `//` 來註解掉該行剩下的內容。`//` 之後的所有內容都會被編譯器忽略。

```move file=packages/samples/sources/move-basics/comments-line.move anchor=main

```

## 區塊註解 (Block Comment) {#block-comment}

區塊註解用來註解掉一整段程式碼。它們以 `/*` 開頭，以 `*/` 結尾。`/*` 和 `*/` 之間的所有內容都會被編譯器忽略。你可以用區塊註解來註解掉單行或多行程式碼，甚至可以用它們來註解掉一行中的一部分。

```move file=packages/samples/sources/move-basics/comments-block.move anchor=main

```

這個範例有點極端，但它展示了所有可以使用區塊註解的方式。

## 文件註解 (Doc Comment) {#doc-comment}

文件註解是用來為程式碼產生文件的特殊註解。它們與行註解類似，但以三個斜線 `///` 開頭,並放置在其所說明項目——模組、結構、函式或常數——的定義之前。

```move file=packages/samples/sources/move-basics/comments-doc.move anchor=main

```

文件工具會將公開成員的文件註解收集到參考頁面中——貫穿本書所連結的
[標準函式庫與框架文件](https://docs.sui.io/references/framework)正是以這種方式產生的。一個寫得好的文件註解會說明函式的作用,以及在什麼條件下會中止。

## 空白字元 (Whitespace) {#whitespace}

與某些語言不同,空白字元(空格、tab 和換行)對程式的意義沒有任何影響。
