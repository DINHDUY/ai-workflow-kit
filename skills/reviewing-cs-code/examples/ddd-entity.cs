// DDD Patterns — Code Examples
// See references/ddd-patterns.md for full explanations of each pattern

namespace Examples.DomainDrivenDesign;

// ── Value Objects ─────────────────────────────────────

// ✅ Immutable, equality by value, validated via record
public record OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
    public override string ToString() => Value.ToString();
}

public record CustomerId(string Value)
{
    public CustomerId(string value) : this(value)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(value);
    }
}

public record Money(decimal Amount, string Currency)
{
    public static Money Zero(string currency) => new(0, currency);
    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new InvalidOperationException($"Cannot add {Currency} and {other.Currency}.");
        return this with { Amount = Amount + other.Amount };
    }
}

// ── Rich Entity (✅ Good) ─────────────────────────────

public class Order
{
    public OrderId Id { get; private set; }
    public CustomerId CustomerId { get; private set; }
    public Money TotalAmount { get; private set; }
    public OrderStatus Status { get; private set; }

    private readonly List<OrderItem> _items = new();
    public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();

    private readonly List<IDomainEvent> _events = new();
    public IReadOnlyCollection<IDomainEvent> DomainEvents => _events.AsReadOnly();

    // Factory method — controls creation invariants
    public static Order Create(CustomerId customerId)
    {
        ArgumentNullException.ThrowIfNull(customerId);
        var order = new Order
        {
            Id = OrderId.New(),
            CustomerId = customerId,
            Status = OrderStatus.Draft,
            TotalAmount = Money.Zero("USD")
        };
        order._events.Add(new OrderCreatedEvent(order.Id, customerId, DateTime.UtcNow));
        return order;
    }

    // Behavior method — enforces business rules
    public void AddItem(Product product, int quantity)
    {
        if (Status != OrderStatus.Draft)
            throw new InvalidOrderStateException(Id, Status, OrderStatus.Draft);

        ArgumentNullException.ThrowIfNull(product);
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(quantity);

        var item = new OrderItem(product.Id, product.Price, quantity);
        _items.Add(item);
        TotalAmount = _items.Aggregate(Money.Zero("USD"), (sum, i) => sum.Add(i.LineTotal));
    }

    public void Place()
    {
        if (!_items.Any())
            throw new DomainException("Cannot place an empty order.");

        Status = OrderStatus.Placed;
        _events.Add(new OrderPlacedEvent(Id, CustomerId, DateTime.UtcNow));
    }

    public void ClearDomainEvents() => _events.Clear();
}

// ── Anemic Entity (❌ Bad) ────────────────────────────

public class Order_Anemic
{
    public int Id { get; set; }                              // Primitive ID, no strong type
    public List<OrderItem> Items { get; set; } = new();     // Mutable, fully exposed
    public decimal Total { get; set; }                      // No encapsulation, no rules
    public string Status { get; set; } = "Draft";           // Magic string, no validation
    // All business logic lives in services — anemic model anti-pattern
}

// ── Domain Events ─────────────────────────────────────

public record OrderCreatedEvent(OrderId OrderId, CustomerId CustomerId, DateTime OccurredAt)
    : IDomainEvent;

public record OrderPlacedEvent(OrderId OrderId, CustomerId CustomerId, DateTime OccurredAt)
    : IDomainEvent;

// ── Repository Interface (Domain Layer) ───────────────

// ✅ Good: Intention-revealing names, strongly-typed IDs, CancellationToken
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(OrderId id, CancellationToken ct);
    Task<IEnumerable<Order>> GetPendingOrdersAsync(CancellationToken ct);
    Task<IEnumerable<Order>> GetByCustomerAsync(CustomerId customerId, CancellationToken ct);
    Task AddAsync(Order order, CancellationToken ct);
    Task UpdateAsync(Order order, CancellationToken ct);
}

// ❌ Bad: Generic, int IDs, exposes IQueryable
public interface IOrderRepository_Bad
{
    Task<Order?> FindAsync(int id);       // int instead of OrderId
    IQueryable<Order> Query();            // Leaks EF IQueryable to domain layer
}
