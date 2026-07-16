using TasksApi.Models;

namespace TasksApi.Repositories;

public interface ITaskRepository
{
    Task<IEnumerable<TaskItem>> GetAllAsync();

    Task<TaskItem?> GetByIdAsync(int id);

    Task<TaskItem> CreateAsync(TaskItem taskItem);

    Task<bool> UpdateAsync(TaskItem taskItem);

    Task<bool> DeleteAsync(int id);
}