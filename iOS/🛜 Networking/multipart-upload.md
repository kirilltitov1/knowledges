---
title: Multipart Upload
type: thread
topics: [Networking]
subtopic: multipart-upload
status: draft
---

# Multipart Upload


### File Upload
- Multipart/form-data
- Boundary
- Progress tracking
- Large files

### Implementation
```swift
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("multipart/form-data; boundary=\(boundary)", 
                 forHTTPHeaderField: "Content-Type")
```

