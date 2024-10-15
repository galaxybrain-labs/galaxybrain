from unittest.mock import Mock

import pytest

from griptape.artifacts import TextArtifact
from griptape.events import EventBus
from griptape.events.event_listener import EventListener
from griptape.structures import Agent, Workflow
from griptape.tasks import ActionsSubtask
from tests.mocks.mock_task import MockTask
from tests.mocks.mock_tool.tool import MockTool


class TestBaseTask:
    @pytest.fixture()
    def task(self):
        EventBus.add_event_listeners([EventListener(handler=Mock())])
        agent = Agent(
            tools=[MockTool()],
        )
        EventBus.add_event_listeners([EventListener(handler=Mock())])

        agent.add_task(MockTask("foobar", max_meta_memory_entries=2))

        return agent.task

    def test_meta_memories(self, task):
        subtask = ActionsSubtask()

        subtask.structure = task.structure

        assert len(task.meta_memories) == 0

        task.structure.task_memory.process_output(MockTool().test, subtask, TextArtifact("foo"))
        task.structure.task_memory.process_output(MockTool().test, subtask, TextArtifact("foo"))
        task.structure.task_memory.process_output(MockTool().test, subtask, TextArtifact("foo"))

        assert len(task.meta_memories) == 2

    def test_parent_outputs(self, task):
        parent_1 = MockTask("foobar1", id="foobar1")
        parent_2 = MockTask("foobar2", id="foobar2")
        parent_3 = MockTask("foobar3", id="foobar3")
        child = MockTask("foobar", id="foobar")

        child.add_parent(parent_1)
        child.add_parent(parent_2)
        child.add_parent(parent_3)

        workflow = Workflow(tasks=[parent_1, parent_2, parent_3, child])
        workflow.run()

        parent_3.output = None
        assert child.parent_outputs == {
            parent_1.id: parent_1.output,
            parent_2.id: parent_2.output,
        }

    def test_parents_output(self, task):
        parent_1 = MockTask("foobar1", id="foobar1")
        parent_2 = MockTask("foobar2", id="foobar2")
        parent_3 = MockTask("foobar3", id="foobar3")
        child = MockTask("foobar", id="foobar")

        child.add_parent(parent_1)
        child.add_parent(parent_2)
        child.add_parent(parent_3)

        workflow = Workflow(tasks=[parent_1, parent_2, parent_3, child])
        workflow.run()

        parent_2.output = None

        assert child.parents_output_text == "foobar1\nfoobar3"

    def test_parents_property_no_structure(self, task):
        workflow = Workflow()
        task1 = MockTask("foobar1", id="foobar1")
        task2 = MockTask("foobar2", id="foobar2")
        task3 = MockTask("foobar3", id="foobar3")
        child = MockTask("foobar", id="foobar")

        child.add_parent(task1)
        child.add_parent(task2)
        child.add_parent(task3)

        with pytest.raises(ValueError, match="Structure must be set to access parents"):
            child.parents  # noqa: B018

        workflow.add_tasks(task1, task2, task3, child)
        child.structure = workflow

        assert len(child.parents) == 3

    def test_children_property_no_structure(self, task):
        workflow = Workflow()
        task1 = MockTask("foobar1", id="foobar1")
        task2 = MockTask("foobar2", id="foobar2")
        task3 = MockTask("foobar3", id="foobar3")
        parent = MockTask("foobar", id="foobar")

        parent.add_child(task1)
        parent.add_child(task2)
        parent.add_child(task3)

        with pytest.raises(ValueError, match="Structure must be set to access children"):
            parent.children  # noqa: B018

        workflow.add_tasks(task1, task2, task3, parent)
        parent.structure = workflow

        assert len(parent.children) == 3

    def test_execute_publish_events(self, task):
        task.execute()

        assert EventBus.event_listeners[0].handler.call_count == 2

    def test_add_parent(self, task):
        agent = Agent()
        parent = MockTask("parent foobar", id="parent_foobar", structure=agent)

        result = task.add_parent(parent)
        result = task.add_parent(parent)

        assert parent.id in task.parent_ids
        assert task.id in parent.child_ids
        assert result == task

        assert agent.tasks == [parent]

    def test_add_child(self, task):
        agent = Agent()
        child = MockTask("child foobar", id="child_foobar", structure=agent)

        result = task.add_child(child)
        result = task.add_child(child)

        assert child.id in task.child_ids
        assert task.id in child.parent_ids
        assert result == task

        assert agent.tasks == [child]

    def test_add_parent_bitshift(self, task):
        parent = MockTask("parent foobar", id="parent_foobar")

        added_task = task << parent

        assert parent.id in task.parent_ids
        assert task.id in parent.child_ids
        assert added_task == parent

    def test_add_child_bitshift(self, task):
        child = MockTask("child foobar", id="child_foobar")

        added_task = task >> child

        assert child.id in task.child_ids
        assert task.id in child.parent_ids
        assert added_task == child
