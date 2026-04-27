# Documentation Standards

## Required XML Doc Tags

| Tag | Purpose | Required when |
|-----|---------|---------------|
| `<summary>` | What the method/class does | Always on public APIs |
| `<param>` | Parameter description | Has parameters |
| `<returns>` | Return value description | Non-void return |
| `<exception>` | Exceptions that may be thrown | Throws or propagates exceptions |

---

## Templates

### Method
```csharp
/// <summary>
/// Retrieves an order by its unique identifier.
/// </summary>
/// <param name="id">The unique identifier of the order.</param>
/// <param name="ct">Token to cancel the async operation.</param>
/// <returns>
/// The matching <see cref="OrderDto"/>, or <c>null</c> if the order does not exist.
/// </returns>
/// <exception cref="ArgumentNullException">
/// Thrown when <paramref name="id"/> is null.
/// </exception>
public async Task<OrderDto?> GetOrderAsync(OrderId id, CancellationToken ct)
```

### Class / Handler
```csharp
/// <summary>
/// Handles the <see cref="CreateOrderCommand"/> use case.
/// Validates the command, creates a new <see cref="Order"/> aggregate,
/// and persists it via the repository.
/// </summary>
public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, OrderDto>
```

### Interface
```csharp
/// <summary>
/// Provides data access operations for <see cref="Order"/> aggregates.
/// </summary>
public interface IOrderRepository
{
    /// <summary>
    /// Retrieves all orders that are awaiting confirmation.
    /// </summary>
    /// <param name="ct">Token to cancel the async operation.</param>
    /// <returns>
    /// A (possibly empty) collection of pending <see cref="Order"/> aggregates.
    /// </returns>
    Task<IEnumerable<Order>> GetPendingOrdersAsync(CancellationToken ct);
}
```

---

## Anti-Patterns

- Comments that restate the code: `// increment i` on `i++`
- Missing docs on public interfaces and abstract classes
- `<summary>` that just repeats the method name: `/// <summary>Get order.</summary>`
- Outdated docs that no longer match the implementation — treat as a bug
- Commenting out dead code instead of deleting it (use version control)
