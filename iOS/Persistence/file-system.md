---
title: File System
type: thread
topics: [Persistence]
subtopic: file-system
status: draft
---

# File System


### Directories
- Documents: User data
- Library: App support files
  - Application Support
  - Caches
- tmp: Temporary files

### FileManager
```swift
let fileManager = FileManager.default
let documentsURL = fileManager.urls(for: .documentDirectory, 
                                    in: .userDomainMask).first
```

### File Operations
- Creating files
- Reading files
- Writing files
- Deleting files
- Moving files
- File attributes

### Data Serialization
- JSON
- Property Lists (plist)
- Custom formats
- Binary data

### Best Practices
- iCloud backup exclusion
- File protection
- Background operations
- Error handling

