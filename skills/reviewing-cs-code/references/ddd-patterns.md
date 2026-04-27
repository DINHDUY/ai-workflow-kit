# Domain-Driven Design — Detailed Reference

## Entities

**Rules:**
- MUST have a strongly-typed identity (e.g., `OrderId`, not `int`)
- Contain behavior, not just data — rich domain model
- Encapsulate business rules inside the entity
- Expose private collections via read-only views

**Red flags:**
- `public List<OrderItem> Items { get; set; }` — mutable, exposed collection
- `public decimal Total { get; set; }` — settable by anyone, no business rule enforcement
- Business logic for the entity living in a service class instead

See `examples/ddd-entity.cs` for full rich entity vs. anemic entity comparison.

---

## Value Objects

**Rules:**
- Immutable — no setters after construction
- Identity by value, not by reference
- Use `record` types in C#
- Validate invariants in constructor / primary constructor

```csharp
public record Money(decimal Amount, string Currency);
public record Address(string Street, string City, string ZipCode);
public record OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
}
```

---

## Aggregates

**Rules:**
- Enforce all invariants — aggregate must always be in a consistent state
- Only aggregate root entities may be referenced from outside the aggregate
- All modifications go through the aggregate root — never directly manipulate child entities
- Keep aggregates small; large aggregates = write contention and performance issues

```csharp
// ✅ Good — Aggregate root controls invariant
public class Order // ← Aggregate root
{
    private readonly List<OrderItem> _items = new();

    public void AddItem(Product product, int quantity)
    {
        if (Status != OrderStatus.Draft)
            throw new InvalidOrderStateException(Id, Status, OrderStatus.Draft);

        _items.Add(new OrderItem(product.Id, product.Price, quantity));
    }
}
// OrderItem is only reachable through Order — never fetched independently
```

---

## Domain Events

**Rules:**
- Represent meaningful business occurrences (past tense naming)
- Immutable — use `record` types
- Raised by the aggregate, handled in the Application layer
- Never carry mutable state

```csharp
public record OrderPlacedEvent(OrderId OrderId, CustomerId CustomerId, DateTime OccurredAt);
public record OrderCancelledEvent(OrderId OrderId, string Reason, DateTime OccurredAt);

// Aggregate raises events:
public class Order
{
    private readonly List<IDomainEvent> _events = new();
    public IReadOnlyCollection<IDomainEvent> DomainEvents => _events.AsReadOnly();

    public void Place()
    {
        if (!_items.Any())
            throw new DomainException("Cannot place an empty order.");

        Status = OrderStatus.Placed;
        _events.Add(new OrderPlacedEvent(Id, CustomerId, DateTime.UtcNow));
    }
}
```

---

## Domain Services

Use when logic spans multiple aggregates or doesn't naturally fit in one entity.

**Rules:**
- Stateless operations
- Depend on domain interfaces (not infrastructure)
- Named as verbs or verb phrases (`OrderPricer`, `InventoryAllocator`)

```csharp
public class InventoryAllocator
{
    private readonly IInventoryRepository _inventory;

    public InventoryAllocator(IInventoryRepository inventory) => _inventory = inventory;

    public async Task<AllocationResult> AllocateAsync(Order order, CancellationToken ct)
    {
        var inventory = await _inventory.GetForProductsAsync(order.ProductIds, ct);
        // Cross-aggregate allocation logic
        return new AllocationResult(/* ... */);
    }
}
```

---

## Repositories

**Rules:**
- Return domain objects — never EF entities or raw data models
- Intention-revealing method names (not generic `Find` or `Query`)
- Interfaces defined in Domain layer, implementations in Infrastructure
- Accept and return strongly-typed IDs

```csharp
// ✅ Good — Intention-revealing, strongly typed
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(OrderId id, CancellationToken ct);
    Task<IEnumerable<Order>> GetPendingOrdersAsync(CancellationToken ct);
    Task<IEnumerable<Order>> GetByCustomerAsync(CustomerId customerId, CancellationToken ct);
    Task AddAsync(Order order, CancellationToken ct);
}

// ❌ Bad — Generic, exposes persistence details
public interface IOrderRepository
{
    Task<Order> FindAsync(int id);    // int instead of OrderId
    IQueryable<Order> Query();        // Leaks EF IQueryable to domain layer
}
```
