FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

WORKDIR /src

COPY ["TasksApi/TasksApi.csproj", "TasksApi/"]

RUN dotnet restore "TasksApi/TasksApi.csproj"

COPY . .

WORKDIR "/src/TasksApi"

RUN dotnet publish "TasksApi.csproj" \
    --configuration Release \
    --output /app/publish \
    /p:UseAppHost=false


FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final

WORKDIR /app

EXPOSE 8080

ENV ASPNETCORE_HTTP_PORTS=8080

COPY --from=build /app/publish .

ENTRYPOINT ["dotnet", "TasksApi.dll"]