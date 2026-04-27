# Error Handling — Detailed Reference

## Custom Exception Hierarchy

Define domain-specific exceptions in the Domain layer. Use a hierarchy for consistent mapping.

```csharp
// Base — Domain layer
public abstract class DomainException : Exception
{
    protected DomainException(string message) : base(message) { }
}

// Specific domain exceptions
public class OrderNotFoundException : DomainException
{
    public OrderNotFoundException(OrderId id)
        : base($"Order {id.Value} was not found.") { }
}

public class OrderLimitExceededException : DomainException
{
    public OrderLimitExceededException(OrderId id)
        : base($"Order {id.Value} has reached the maximum item limit.") { }
}

public class InvalidOrderStateException : DomainException
{
    public InvalidOrderStateException(OrderId id, OrderStatus current, OrderStatus required)
        : base($"Order {id.Value} must be in '{required}' state, but is '{current}'.") { }
}
```

---

## Try/Catch Patterns

```csharp
// ❌ Bad — Silent swallow
catch (Exception ex) { }

// ❌ Bad — Stack trace to end user
catch (Exception ex) { return ex.StackTrace; }

// ❌ Bad — No context in log
catch (Exception ex)
{
    _logger.LogError("Error"); // Missing orderId, operation name
}

// ✅ Good — Domain exception: Warning + re-throw
catch (OrderNotFoundException ex)
{
    _logger.LogWarning(ex,
        "Order {OrderId} not found during {Operation}",
        orderId, nameof(ProcessOrderAsync));
    throw; // Let API layer map to 404
}

// ✅ Good — Unexpected exception: Error + clean message to caller
catch (Exception ex)
{
    _logger.LogError(ex,
        "Unexpected error in {Operation} for order {OrderId}",
        nameof(ProcessOrderAsync), orderId);
    throw new ApplicationException("An error occurred processing your request.");
}
```

---

## API-Level Exception Mapping

Map domain exceptions to HTTP status codes in a global handler — not in individual controllers.

```csharp
// Program.cs — global exception handler
app.UseExceptionHandler(err => err.Run(async context =>
{
    var feature = context.Features.Get<IExceptionHandlerFeature>();
    var (status, message) = feature?.Error switch
    {
        OrderNotFoundException     => (404, "Order not found."),
        InvalidOrderStateException => (422, "Order is in an invalid state."),
        DomainException ex         => (400, ex.Message),
        _                         => (500, "An unexpected error occurred.")
    };

    context.Response.StatusCode = status;
    await context.Response.WriteAsJsonAsync(new { error = message });
}));
```

---

## Anti-Patterns Checklist

- [ ] Empty catch blocks — must at minimum log
- [ ] Catch all `Exception` without specific handling for domain cases first
- [ ] Stack traces returned to API consumers
- [ ] Missing `CancellationToken` propagation (tasks that can't be cancelled)
- [ ] Swallowing `OperationCanceledException` — re-throw it
- [ ] Logging PII or tokens inside exception messages
- [ ] Re-wrapping exceptions that should propagate (`throw new Exception(ex.Message)` loses stack)
