---
type: "thread"
status: "draft"
summary: ""
title: "Best Practices"
---

# Best Practices


### Do's ✅
- Use async/await for new code
- Isolate mutable state with actors
- Handle cancellation properly
- Use appropriate priority/QoS
- Avoid blocking main thread
- Use structured concurrency
- Test concurrent code thoroughly

### Don'ts ❌
- Don't use `DispatchQueue.main.sync` on main thread
- Don't create unlimited threads
- Don't ignore race conditions
- Don't forget to cancel operations
- Don't mix too many paradigms
- Don't over-complicate simple tasks
- Don't forget error handling

### Common Patterns
- Coordinator pattern for complex flows
- Repository pattern with async
- Service layer with Combine
- ViewModel with @MainActor

