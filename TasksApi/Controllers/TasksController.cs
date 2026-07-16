using Microsoft.AspNetCore.Mvc;
using TasksApi.Models;
using TasksApi.Repositories;
using TasksApi.Dtos;

namespace TasksApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TasksController : ControllerBase
{
    private readonly ITaskRepository _repository;

    public TasksController(ITaskRepository repository)
    {
        _repository = repository;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<TaskItem>>> GetAll()
    {
        IEnumerable<TaskItem> tasks = await _repository.GetAllAsync();

        return Ok(tasks);
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<TaskItem>> GetById(int id)
    {
        TaskItem? taskItem = await _repository.GetByIdAsync(id);

        if (taskItem is null)
        {
            return NotFound();
        }

        return Ok(taskItem);
    }

    [HttpPost]
    public async Task<ActionResult<TaskItem>> Create(CreateTaskDto dto)
    {
        TaskItem taskItem=new()
        {
            Title = dto.Title,
            Description = dto.Description,
            IsCompleted = dto.IsCompleted
        };

        TaskItem createdTask = await _repository.CreateAsync(taskItem);

        return CreatedAtAction(
        nameof(GetById),
        new { id = createdTask.Id },
        createdTask
        );
    }

    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(int id, UpdateTaskDto dto)
    {
        TaskItem? existingTask = await _repository.GetByIdAsync(id);

        if (existingTask is null)
        {
            return NotFound();
        }

        existingTask.Title = dto.Title;
        existingTask.Description = dto.Description;
        existingTask.IsCompleted = dto.IsCompleted;

        await _repository.UpdateAsync(existingTask);

        return NoContent();
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        bool deleted = await _repository.DeleteAsync(id);

        if (!deleted)
        {
            return NotFound();
        }

        return NoContent();
    }
}