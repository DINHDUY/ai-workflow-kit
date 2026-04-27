# DRY Principle

**Do not Repeat Yourself.** After the second occurrence of similar logic, refactor to a shared component.

---

## Shared Validation

```csharp
// ❌ Bad — Same null/range checks duplicated in every handler
public class CreateOrderHandler
{
    public async Task Handle(CreateOrderCommand command, CancellationToken ct)
    {
        if (command == null) throw new ArgumentNullException(nameof(command));
        if (string.IsNullOrWhiteSpace(command.CustomerId)) throw new ArgumentException(...);
        if (command.Amount <= 0) throw new ArgumentOutOfRangeException(...);
        // ...
    }
}

// ✅ Good — FluentValidation validator, applied once via MediatR pipeline behavior
public class CreateOrderCommandValidator : AbstractValidator<CreateOrderCommand>
{
    public CreateOrderCommandValidator()
    {
        RuleFor(x => x.CustomerId).NotEmpty().MaximumLength(50);
        RuleFor(x => x.Amount).GreaterThan(0);
    }
}

// Registered in DI:
services.AddTransient<IValidator<CreateOrderCommand>, CreateOrderCommandValidator>();
// Applied automatically via ValidationBehavior<TRequest, TResponse> in the MediatR pipeline
```

---

## Base Repository

```csharp
// ✅ Good — Common CRUD operations defined once
public abstract class RepositoryBase<T, TId> where T : class
{
    protected readonly AppDbContext Context;

    protected RepositoryBase(AppDbContext context) => Context = context;

    public virtual async Task<T?> GetByIdAsync(TId id, CancellationToken ct)
        => await Context.Set<T>().FindAsync(new object?[] { id }, ct);

    public virtual async Task AddAsync(T entity, CancellationToken ct)
        => await Context.Set<T>().AddAsync(entity, ct);
}

// Specific repository only adds what's unique
public class OrderRepository : RepositoryBase<Order, OrderId>, IOrderRepository
{
    public OrderRepository(AppDbContext context) : base(context) { }

    public async Task<IEnumerable<Order>> GetPendingOrdersAsync(CancellationToken ct)
        => await Context.Orders
            .Where(o => o.Status == OrderStatus.Pending)
            .ToListAsync(ct);
}
```

---

## Extension Methods for Cross-Cutting Logic

```csharp
// ✅ Good — Shared pagination, reused across all queries
public static class QueryableExtensions
{
    public static IQueryable<T> Paginate<T>(this IQueryable<T> query, int page, int pageSize)
        => query.Skip((page - 1) * pageSize).Take(pageSize);
}

// Usage: var orders = await _context.Orders.Paginate(page, pageSize).ToListAsync(ct);
```

---

## Generic Cross-Cutting Concerns

Avoid duplicating these per-caller — register once in DI:

- **Logging**: `ILogger<T>` injected via DI — never static loggers
- **Retry**: `Polly` policies registered once, applied via HTTP client factory or pipeline behavior
- **Caching**: `IMemoryCache` / `IDistributedCache` wrapper, not inline `Dictionary<>` caches
- **Result pattern**: Shared `Result<T>` / `Result<T, TError>` type instead of ad hoc exception + null handling
