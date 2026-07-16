using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using TasksApi.Data;
using TasksApi.Models;
using TasksApi.Repositories;

namespace TasksApi.Tests;

public class EfTaskRepositoryTests
{
    private static async Task<(
        SqliteConnection Connection,
        TasksDbContext Context,
        EfTaskRepository Repository
    )> CreateRepositoryAsync()
    {
        SqliteConnection connection =
            new("Data Source=:memory:");

        await connection.OpenAsync();

        DbContextOptions<TasksDbContext> options =
            new DbContextOptionsBuilder<TasksDbContext>()
                .UseSqlite(connection)
                .Options;

        TasksDbContext context = new(options);

        await context.Database.EnsureCreatedAsync();

        EfTaskRepository repository = new(context);

        return (connection, context, repository);
    }

    [Fact]
    public async Task CreateAsync_SavesTaskInDatabase()
    {
        // Arrange
        var setup = await CreateRepositoryAsync();

        await using SqliteConnection connection = setup.Connection;
        await using TasksDbContext context = setup.Context;

        EfTaskRepository repository = setup.Repository;

        TaskItem taskItem = new()
        {
            Title = "Test repository",
            Description = "Created by an automated test",
            IsCompleted = false
        };

        // Act
        TaskItem createdTask =
            await repository.CreateAsync(taskItem);

        TaskItem? storedTask =
            await repository.GetByIdAsync(createdTask.Id);

        // Assert
        Assert.True(createdTask.Id > 0);
        Assert.NotNull(storedTask);
        Assert.Equal("Test repository", storedTask.Title);
        Assert.False(storedTask.IsCompleted);
    }

    [Fact]
    public async Task UpdateAsync_UpdatesExistingTask()
    {
        // Arrange
        var setup = await CreateRepositoryAsync();

        await using SqliteConnection connection = setup.Connection;
        await using TasksDbContext context = setup.Context;

        EfTaskRepository repository = setup.Repository;

        TaskItem taskItem = new()
        {
            Title = "Original title",
            Description = "Original description",
            IsCompleted = false
        };

        TaskItem createdTask =
            await repository.CreateAsync(taskItem);

        createdTask.Title = "Updated title";
        createdTask.Description = "Updated description";
        createdTask.IsCompleted = true;

        // Act
        bool updated =
            await repository.UpdateAsync(createdTask);

        TaskItem? storedTask =
            await repository.GetByIdAsync(createdTask.Id);

        // Assert
        Assert.True(updated);
        Assert.NotNull(storedTask);
        Assert.Equal("Updated title", storedTask.Title);
        Assert.Equal("Updated description", storedTask.Description);
        Assert.True(storedTask.IsCompleted);
    }

    [Fact]
    public async Task DeleteAsync_RemovesExistingTask()
    {
        // Arrange
        var setup = await CreateRepositoryAsync();

        await using SqliteConnection connection = setup.Connection;
        await using TasksDbContext context = setup.Context;

        EfTaskRepository repository = setup.Repository;

        TaskItem taskItem = new()
        {
            Title = "Task to delete",
            Description = "This task should be deleted",
            IsCompleted = false
        };

        TaskItem createdTask =
            await repository.CreateAsync(taskItem);

        // Act
        bool deleted =
            await repository.DeleteAsync(createdTask.Id);

        TaskItem? storedTask =
            await repository.GetByIdAsync(createdTask.Id);

        // Assert
        Assert.True(deleted);
        Assert.Null(storedTask);
    }
}