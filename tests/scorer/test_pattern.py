import pytest
from test_helpers.utils import simple_task_state

from inspect_ai.scorer import CORRECT, INCORRECT, Target, pattern


@pytest.mark.asyncio
async def test_single_match_success():
    scorer = pattern("(foo)")
    state = simple_task_state("foo")
    result = await scorer(state, Target(["foo"]))

    assert result.text == CORRECT


@pytest.mark.asyncio
async def test_single_match_failure_with_target():
    scorer = pattern("(foo)")
    state = simple_task_state("foo")
    result = await scorer(state, Target(["target doesn't match"]))

    assert result.text == INCORRECT


@pytest.mark.asyncio
async def test_single_match_failure_from_model():
    scorer = pattern("(foo)")
    state = simple_task_state("model doesn't match")
    result = await scorer(state, Target(["foo"]))

    assert result.text == INCORRECT


@pytest.mark.asyncio
async def test_single_match_case_sensitive():
    scorer = pattern(pattern="(FOO)", ignore_case=True)
    state = simple_task_state("foo")
    result = await scorer(state, Target(["foo"]))

    assert result.text == CORRECT


@pytest.mark.asyncio
async def test_multi_match_success_on_first_match():
    scorer = pattern("(foo) (bar)")
    state = simple_task_state("foo bar")
    result = await scorer(state, Target(["foo"]))

    assert result.text == CORRECT
    assert result.answer == "foo"


@pytest.mark.asyncio
async def test_multi_match_success_on_subsequent_match():
    scorer = pattern("(foo) (bar)")
    state = simple_task_state("foo bar")
    result = await scorer(state, Target(["bar"]))

    assert result.text == CORRECT
    assert result.answer == "bar"


@pytest.mark.asyncio
async def test_multi_match_success_all_match():
    scorer = pattern("(foo) (foo)", match_all=True)
    state = simple_task_state("foo foo")
    result = await scorer(state, Target(["foo"]))

    assert result.text == CORRECT
    assert result.answer == "foo"


@pytest.mark.asyncio
async def test_multi_match_failure_when_matching_all():
    scorer = pattern("(foo|bar) (foo|bar)", match_all=True)
    state = simple_task_state("foo bar")
    result = await scorer(state, Target(["bar"]))

    assert result.text == INCORRECT
    assert result.answer is None


@pytest.mark.asyncio
async def test_multi_match_failure_with_target():
    scorer = pattern("(foo) (bar)")
    state = simple_task_state("foo bar")
    result = await scorer(state, Target(["target doesn't match"]))

    assert result.text == INCORRECT


@pytest.mark.asyncio
async def test_multi_match_failure_from_model():
    scorer = pattern("(foo) (bar)")
    state = simple_task_state("model doesn't match")
    result = await scorer(state, Target(["bar"]))

    assert result.text == INCORRECT


@pytest.mark.asyncio
async def test_only_returns_exact_target_matches():
    scorer = pattern("(f[oz]o) (b[az]r)")
    state = simple_task_state("foo bzr")
    result = await scorer(state, Target(["bar"]))

    assert result.text == INCORRECT
