import pytest

from infra.db.models.users import User
from infra.db.models.tasks import Task
from infra.db.repository.user_repo import UserRepository
from infra.db.repository.task_repo import TaskRepository
from service.task_service import TaskService
from service.exceptions import TaskServiceError
from api.schemas.task_schemas import TaskCreateForUserSchema, TaskUpdateForUserSchema


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
def test_check_is_root_task():
    task = Task(id=1, task_id=None)
    assert TaskService(None, None).check_is_root_task(task)


@pytest_mark_asyncio
def test_check_task_done_true():
    task = Task(pass_date="2024-01-01", done=True)
    assert TaskService(None, None).check_task_done(task)


@pytest_mark_asyncio
def test_check_task_done_false():
    task = Task(pass_date=None, done=False)
    assert not TaskService(None, None).check_task_done(task)


@pytest_mark_asyncio
async def test_check_is_root_for_user_success(task_service: TaskService, mock_task_repo: TaskRepository, mock_user_repo: UserRepository, mocker):
    task = Task(id=1, task_id=None)
    mock_user_repo.get_user_and_tasks = mocker.AsyncMock(
        return_value=User(id=1, tasks=[task]))
    mock_task_repo.get_task = mocker.AsyncMock(return_value=task)
    await task_service.check_is_root_for_user(1, 1)


@pytest_mark_asyncio
async def test_check_is_root_for_user_fail(task_service: TaskService, mock_task_repo: TaskRepository, mock_user_repo: UserRepository, mocker):
    user_task = Task(id=1, task_id=None)
    other_task = Task(id=2, task_id=None)
    mock_user_repo.get_user_and_tasks = mocker.AsyncMock(
        return_value=User(id=1, tasks=[user_task]))
    mock_task_repo.get_task = mocker.AsyncMock(return_value=other_task)
    with pytest.raises(TaskServiceError):
        await task_service.check_is_root_for_user(1, 2)


@pytest_mark_asyncio
async def test_get_root_tasks_for_user(task_service: TaskService, mock_user_repo: TaskRepository, mocker):
    root = Task(id=1, task_id=None)
    sub = Task(id=2, task_id=1)
    mock_user_repo.get_user_and_tasks = mocker.AsyncMock(
        return_value=User(id=1, tasks=[root, sub]))
    result = await task_service.get_root_tasks_for_user(1)
    assert result == [root]


@pytest_mark_asyncio
async def test_get_full_trees(task_service: TaskService, mock_task_repo: TaskRepository, mocker):
    root1 = Task(id=1)
    root2 = Task(id=2)
    mock_task_repo.get_root_tasks = mocker.AsyncMock(
        return_value=[root1, root2])
    task_service.get_task_tree = mocker.AsyncMock(
        side_effect=lambda id, **kwargs: f"tree-{id}")
    result = await task_service.get_full_trees()
    assert result == ["tree-1", "tree-2"]


@pytest_mark_asyncio
async def test_get_task_tree(task_service: TaskService, mock_task_repo: TaskRepository, mocker):
    mock_task_repo.get_nested_tasks = mocker.AsyncMock(return_value="tree")
    result = await task_service.get_task_tree(1)
    assert result == "tree"


@pytest_mark_asyncio
async def test_get_tasks_trees(task_service: TaskService, mocker):
    task_service.get_task_tree = mocker.AsyncMock(
        side_effect=lambda tid, **_: f"tree-{tid}")
    result = await task_service.get_tasks_trees([1, 2])
    assert result == ["tree-1", "tree-2"]


@pytest_mark_asyncio
async def test_get_user_task_tree(task_service: TaskService, mocker):
    task_service.check_is_root_for_user = mocker.AsyncMock()
    task_service.get_task_tree = mocker.AsyncMock(return_value="tree")
    result = await task_service.get_user_task_tree(1, 1)
    assert result == "tree"


@pytest_mark_asyncio
async def test_get_user_tasks_trees(task_service: TaskService, mocker):
    task_service.get_root_tasks_for_user = mocker.AsyncMock(
        return_value=[Task(id=1), Task(id=2)])
    task_service.get_tasks_trees = mocker.AsyncMock(
        return_value=["tree-1", "tree-2"])
    result = await task_service.get_user_tasks_trees(1)
    assert result == ["tree-1", "tree-2"]


@pytest_mark_asyncio
async def test_finish_task_success(task_service: TaskService, mock_task_repo: TaskRepository, mocker):
    task = Task(id=1, pass_date="2024-01-01", done=True)
    subtask = Task(id=2, pass_date="2024-01-01", done=True)
    task_service.get_task_tree = mocker.AsyncMock(return_value=[task, subtask])
    mock_task_repo.finish_task = mocker.AsyncMock(return_value=task)
    result = await task_service.finish_task(1)
    assert result == task


@pytest_mark_asyncio
async def test_finish_task_fail_unfinished_subtasks(task_service: TaskService, mock_task_repo: TaskRepository, mocker):
    task = Task(id=1, title='t1', pass_date="2024-01-01", done=True)
    unfinished = Task(id=2, title='t2', pass_date=None, done=False)
    task_service.get_task_tree = mocker.AsyncMock(
        return_value=[task, unfinished])
    mock_task_repo.get_nested_tasks = mocker.AsyncMock()
    with pytest.raises(TaskServiceError) as exc_info:
        await task_service.finish_task(1)
    assert "not finished subtasks" in str(exc_info.value)


@pytest_mark_asyncio
async def test_add_task_to_user(task_service: TaskService, mock_task_repo: TaskRepository, mocker):
    schema = TaskCreateForUserSchema(
        title="Test", task_id=None, description='test desc')
    mock_task_repo.create_task = mocker.AsyncMock(return_value="created")
    result = await task_service.add_task_to_user(1, schema)
    assert result == "created"


@pytest_mark_asyncio
async def test_update_task_for_user_success(task_service: TaskService, mock_user_repo: UserRepository, mock_task_repo: TaskRepository, mocker):
    mock_user_repo.get_user_and_tasks = mocker.AsyncMock(
        return_value=User(id=1, tasks=[Task(id=1)]))
    mock_task_repo.update_task = mocker.AsyncMock(return_value="updated")
    schema = TaskUpdateForUserSchema(title="Updated")
    result = await task_service.update_task_for_user(1, 1, schema)
    assert result == "updated"


@pytest_mark_asyncio
async def test_update_task_for_user_fail(task_service: TaskService, mock_user_repo: UserRepository, mocker):
    mock_user_repo.get_user_and_tasks = mocker.AsyncMock(
        return_value=User(id=1, tasks=[]))
    schema = TaskUpdateForUserSchema(title="Updated")
    with pytest.raises(TaskServiceError):
        await task_service.update_task_for_user(1, 1, schema)


@pytest_mark_asyncio
async def test_finish_task_for_user_success(task_service: TaskService, mock_task_repo: TaskRepository, mocker):
    task = Task(id=1, user_id=1)
    mock_task_repo.get_task = mocker.AsyncMock(return_value=task)
    task_service.finish_task = mocker.AsyncMock(return_value="finished")
    result = await task_service.finish_task_for_user(1, 1)
    assert result == "finished"


@pytest_mark_asyncio
async def test_finish_task_for_user_fail(task_service: TaskService, mock_task_repo: TaskRepository, mocker):
    task = Task(id=1, title='t1', user_id=999)
    mock_task_repo.get_task = mocker.AsyncMock(return_value=task)
    task_service.finish_task = mocker.AsyncMock()
    with pytest.raises(TaskServiceError):
        await task_service.finish_task_for_user(2, 1)
