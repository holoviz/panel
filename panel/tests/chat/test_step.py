import pytest

from panel.chat.step import ChatStep


class TestChatStep:
    def test_initial_status(self):
        step = ChatStep()
        assert step.status == "pending", "Initial status should be 'pending'"

    def test_status_transitions_and_titles(self):
        step = ChatStep(running_title="Running", pending_title="Pending", success_title="Success", failed_title="Error Occurred")
        assert step.status == "pending", "Initial status should be 'pending'"

        # Test running status
        with step:
            assert step.status == "running", "Status should be 'running' during context execution"
            assert step.title == "Running", "Title should be 'Running' during context execution"

        # Test success status
        assert step.status == "success", "Status should be 'success' after context execution without errors"
        assert step.title == "Success", "Title should be 'Success' after context execution without errors"

        # Test failed status
        with pytest.raises(ValueError):
            with step:
                raise ValueError("Error")
        assert step.status == "failed", "Status should be 'failed' after an exception"
        assert step.title == "Error Occurred", "Title should update to 'Error Occurred' on failure"

    def test_avatar_and_collapsed_behavior(self):
        step = ChatStep(collapsed_on_success=True)
        initial_avatar = step._avatar_placeholder.object

        # Test avatar updates
        with step:
            assert step._avatar_placeholder.object != initial_avatar, "Avatar should change when status is 'running'"
        assert step._avatar_placeholder.object != initial_avatar, "Avatar should change when status is 'success'"

        # Test collapsed behavior
        assert step.collapsed, "Step should be collapsed on success when collapsed_on_success is True"

    def test_streaming_updates(self):
        step = ChatStep()

        # Test content streaming
        step.stream("First message")
        assert len(step.objects) == 1, "First message should be added to objects"
        assert step.objects[0].object == "First message", "First message should be 'First message'"
        step.stream("Second message")
        assert len(step.objects) == 1
        assert step.objects[0].object == "First messageSecond message", "Messages should be concatenated"

    def test_streaming_title_updates(self):
        step = ChatStep(running_title="Run")
        step.stream_title("Pend", status="pending")
        assert step.pending_title == "Pend", "Pending title should be 'Pend'"
        assert step.title == "Pend", "Title should be 'Pend' when status is 'pending'"

        step.stream_title("ing", status="pending")
        assert step.pending_title == "Pending", "Pending title should be 'Pending'"
        assert step.title == "Pending", "Title should be 'Pending' when status is 'pending'"

        step.stream_title("Starting now...", status="pending", replace=True)
        assert step.pending_title == "Starting now...", "Pending title should be 'Starting now...'"
        assert step.title == "Starting now...", "Title should be 'Starting now...' when status is 'pending'"

        step.stream_title("ning")
        assert step.running_title == "Running"
        assert step.title == "Starting now...", "Title should be 'Starting now...' when status is 'pending'"
        step.status = "running"
        assert step.title == "Running", "Title should be 'Running' when status is 'running'"

    def test_serialization(self):
        step = ChatStep()
        serialized = step.serialize()
        assert isinstance(serialized, str), "Serialization should return a string representation"

    def test_repeated_error(self):
        step = ChatStep()
        with pytest.raises(ValueError):
            with step:
                raise ValueError("Testing")

        assert step.status == "failed", "Status should be 'failed' after an exception"
        assert step.title == "Error: 'ValueError'", "Title should update to 'Error: 'ValueError'' on failure"
        assert step.objects[0].object == "Testing", "Error message should be streamed to the message pane"

        with pytest.raises(RuntimeError):
            with step:
                raise RuntimeError("Second Testing")

        assert step.status == "failed", "Status should be 'failed' after an exception"
        assert step.title == "Error: 'RuntimeError'", "Title should update to 'Error: 'RuntimeError'' on failure again"
        assert step.objects[0].object == "Testing\nSecond Testing", "Error message should be streamed to the message pane"

    def test_context_manually_set_failed(self):
        step = ChatStep()
        with step:
            step.status = "failed"
        assert step.status == "failed", "Status should be 'failed' after manually setting it to 'failed'"

    def test_context_exception_ignore(self):
        step = ChatStep(context_exception="ignore")
        with step:
            raise ValueError("Testing")
        assert step.objects == []

    def test_context_exception_raise(self):
        step = ChatStep(context_exception="raise")
        with pytest.raises(ValueError, match="Testing"):
            with step:
                raise ValueError("Testing")
        assert step.objects[0].object == "Testing"

    def test_context_exception_summary(self):
        step = ChatStep(context_exception="summary")
        with step:
            raise ValueError("Testing")
        assert step.objects[0].object == "Testing"

    def test_context_exception_verbose(self):
        step = ChatStep(context_exception="verbose")
        with step:
            raise ValueError("Testing")
        assert "Traceback" in step.objects[0].object

    def test_stream_none(self):
        step = ChatStep()
        step.stream(None)
        assert len(step) == 1
        assert step[0].object == ""
        step.stream("abc")
        assert len(step) == 1
        assert step[0].object == "abc"

    def test_header_inherits_width(self):
        step = ChatStep(width=100)
        assert step.header.width == 100

    @pytest.mark.parametrize("width_key", ["max_width", "min_width"])
    def test_header_inherits_stretch_width(self, width_key):
        step = ChatStep(**{width_key: 100}, sizing_mode="stretch_width")
        assert getattr(step.header, width_key) == 100
        assert step.header.sizing_mode == "stretch_width"
