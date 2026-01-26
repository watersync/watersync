# Future Implementation: Soft Delete Functionality

## Overview
This document contains the soft delete functionality implementation that was removed from the main refactoring plan. This can be implemented in a future iteration when the basic model abstractions are stable.

## Soft Delete Implementation

### SoftDeleteMixin

```python
class SoftDeleteMixin(models.Model):
    """Provides soft delete functionality."""
    
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
    
    def soft_delete(self, save=True):
        """Mark object as deleted."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if save:
            self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def restore(self, save=True):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        if save:
            self.save(update_fields=['is_deleted', 'deleted_at'])
```

### Enhanced Managers for Soft Delete

```python
class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet that handles soft-deleted objects."""
    
    def alive(self):
        """Return only non-deleted objects."""
        return self.filter(is_deleted=False)
    
    def dead(self):
        """Return only soft-deleted objects."""
        return self.filter(is_deleted=True)
    
    def with_deleted(self):
        """Return all objects including soft-deleted."""
        return self
        
    def soft_delete(self):
        """Soft delete all objects in queryset."""
        return self.update(
            is_deleted=True,
            deleted_at=timezone.now()
        )


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""
    
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()
    
    def with_deleted(self):
        """Return queryset including soft-deleted objects."""
        return SoftDeleteQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        """Return only soft-deleted objects."""
        return SoftDeleteQuerySet(self.model, using=self._db).dead()
```

### Migration Considerations

When implementing soft delete:

1. **Add fields to existing models** via data migration
2. **Update all model managers** to use SoftDeleteManager
3. **Add soft delete buttons** to UI where appropriate
4. **Update view logic** to handle soft-deleted objects
5. **Consider cascade behavior** for related objects

### Testing Requirements

- Test that soft delete doesn't break existing queries
- Test restore functionality
- Test manager behavior (alive, dead, with_deleted)
- Test cascade behavior for foreign keys
- Test admin interface integration

### UI Considerations

- Add "Restore" buttons for soft-deleted objects
- Show deleted status in list views (if desired)
- Add filters for deleted/active objects
- Consider "trash" view for managing deleted objects

## Implementation Priority

This should be implemented **after** the basic model abstractions are stable and well-tested. Suggested timeline:

1. Complete Priority 1-3 from main refactoring
2. Evaluate need for soft delete functionality
3. Implement if business requirements justify the complexity
4. Add comprehensive testing and documentation

## Risk Assessment

**Benefits:**
- Data safety - accidental deletes can be recovered
- Audit trail - can see what was deleted when
- Business intelligence - analyze deleted data patterns

**Risks:**
- Increased complexity in queries and relationships
- Database bloat over time
- Potential performance impact
- More complex backup/restore procedures
- Need for cleanup processes for truly removing data

## Alternative Approaches

Consider these alternatives before implementing soft delete:

1. **Database backups** - Regular backups may be sufficient for data recovery
2. **Audit logging** - Log deletion events without keeping data
3. **Archive tables** - Move deleted data to separate archive tables
4. **Version control** - Use django-simple-history for change tracking