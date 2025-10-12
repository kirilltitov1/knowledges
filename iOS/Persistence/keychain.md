---
type: "thread"
topics:
  - Users
  - kirilltitov
  - DocumentsUsers", "kirilltitov", "Documents"]"
status: "draft"
summary: ""
title: "keychain"
---
title: Keychain
type: thread
topics: ["Persistence"]
subtopic: keychain
status: draft---

# Keychain


### Purpose
- Secure storage
- Passwords
- Tokens
- Certificates
- Cryptographic keys

### Keychain Services API
- SecItemAdd
- SecItemCopyMatching
- SecItemUpdate
- SecItemDelete

### Accessibility
- kSecAttrAccessibleWhenUnlocked
- kSecAttrAccessibleAfterFirstUnlock
- kSecAttrAccessibleAlways (deprecated)
- kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly

### Keychain Sharing
- Access groups
- App groups
- Keychain sharing entitlement

### Wrappers
- KeychainAccess library
- Custom wrapper classes
- Property wrappers

