using Microsoft.EntityFrameworkCore;
using TasksApi.Data;
using TasksApi.Models;

namespace TasksApi.Repositories;

public class EfTaskRepository : ITaskRepository
{
    private readonly TasksDbContext _context;

    public EfTaskRepository(TasksDbContext context)
    {
        _context = context;
    }

    public async Task<IEnumerable<TaskItem>> GetAllAsync()
    {
        return await _context.Tasks
            .AsNoTracking()
            .OrderBy(task => task.Id)
            .ToListAsync();
    }

    public async Task<TaskItem?> GetByIdAsync(int id)
    {
        return await _context.Tasks
            .AsNoTracking()
            .FirstOrDefaultAsync(task => task.Id == id);
    }

    public async Task<TaskItem> CreateAsync(TaskItem taskItem)
    {
        taskItem.CreatedAt = DateTime.UtcNow;

        _context.Tasks.Add(taskItem);

        await _context.SaveChangesAsync();

        return taskItem;
    }

    public async Task<bool> UpdateAsync(TaskItem taskItem)
    {
        TaskItem? existingTask =
            await _context.Tasks.FindAsync(taskItem.Id);

        if (existingTask is null)
        {
            return false;
        }

        existingTask.Title = taskItem.Title;
        existingTask.Description = taskItem.Description;
        existingTask.IsCompleted = taskItem.IsCompleted;

        await _context.SaveChangesAsync();

        return true;
    }

    public async Task<bool> DeleteAsync(int id)
    {
        TaskItem? taskItem = await _context.Tasks.FindAsync(id);

        if (taskItem is null)
        {
            return false;
        }

        _context.Tasks.Remove(taskItem);

        await _context.SaveChangesAsync();

        return true;
    }
}