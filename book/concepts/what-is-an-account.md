---
description: 理解 Sui 帳戶 (Sui accounts)：它們如何從私鑰 (private keys) 產生、由地址 (addresses) 識別，並支援多種密碼學方案 (crypto schemes)。
title: 帳戶 (Account)
keywords:
  - Move
  - Sui
  - Move tutorial
  - account
questions:
  - What is Account in Move?
  - How do I use Account in Move?
answer: 'Understand Sui accounts: how they are generated from private keys, identified by addresses, and support multiple crypto schemes.'
goal:
  description: 'Reader understands Sui accounts: how they are generated from private keys, identified by addresses, and support multiple crypto schemes'
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

# 帳戶 (Account) {#account}

帳戶是用來識別使用者的方式。帳戶由私鑰產生，並透過[地址](./address)識別。帳戶可以擁有物件，也可以發送交易。每一筆交易都有一個發送者，發送者透過[地址](./address)識別。

帳戶不需要在任何地方建立或註冊：只要產生了金鑰對，它就存在了，而且任何有效的地址都可以在沒有事前設定的情況下接收物件。鏈上並沒有「所有帳戶」的紀錄——沒有物件且沒有交易紀錄的地址，與從未使用過的地址是無法區分的。

Sui 支援多種帳戶的簽章方案：ed25519、ECDSA（基於 secp256k1 與 secp256r1 曲線）、passkeys（基於 WebAuthn 標準的裝置驗證器，例如 Face ID、Touch ID 或硬體安全金鑰）、多重簽章 (multisig)（由金鑰組合所控制的帳戶），以及 zkLogin（從 Web2 登入衍生出帳戶）。這種*密碼學靈活性*（cryptographic agility）讓 Sui 在帳戶的建立與控制方式上具備了不尋常的彈性。

## 延伸閱讀 (Further Reading) {#further-reading}

- [Sui 官方部落格](https://blog.sui.io)中的 [Sui 中的密碼學 (Cryptography in Sui)](https://blog.sui.io/wallet-cryptography-specifications/)
- [Sui 文件](https://docs.sui.io)中的 [金鑰與地址 (Keys and Addresses)](https://docs.sui.io/guides/developer/transactions/transaction-auth/auth-overview)
- [Sui 文件](https://docs.sui.io)中的 [簽章 (Signatures)](https://docs.sui.io/guides/developer/cryptography/signing)
- [Sui 文件](https://docs.sui.io)中的 [Passkey](https://docs.sui.io/develop/cryptography/passkeys)
