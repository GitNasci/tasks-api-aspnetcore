using TasksApi.Repositories;
using Microsoft.EntityFrameworkCore;
using TasksApi.Data;


var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();
builder.Services.AddDbContext<TasksDbContext>(options =>
    options.UseSqlite(
        builder.Configuration.GetConnectionString("TasksDatabase")
    )
);
builder.Services.AddScoped<ITaskRepository, EfTaskRepository>();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

using (IServiceScope scope = app.Services.CreateScope())
{
    TasksDbContext dbContext =
        scope.ServiceProvider.GetRequiredService<TasksDbContext>();

    await dbContext.Database.MigrateAsync();
}

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
